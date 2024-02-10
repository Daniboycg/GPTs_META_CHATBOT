import importlib.util
from flask import request, abort
import logging
import openai
import os
from packaging import version
import requests
import re
import time
import json

WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
AIRTABLE_DB_URL = os.environ.get('AIRTABLE_DB_URL')
AIRTABLE_API_KEY = f"Bearer {os.environ.get('AIRTABLE_API_KEY')}"
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Initialize OpenAI client
if not OPENAI_API_KEY:
  raise ValueError("No OpenAI API key found in environment variables")
client = openai.OpenAI(api_key=OPENAI_API_KEY)


# Check the current OpenAI version
def check_openai_version():
  required_version = version.parse("1.1.1")
  current_version = version.parse(openai.__version__)
  if current_version < required_version:
    raise ValueError(
        f"Error: OpenAI version {openai.__version__} is less than the required version 1.1.1"
    )
  else:
    logging.info("OpenAI version is compatible.")


# Add thread to DB with platform identifier
def add_thread(thread_id, platform, username):
  url = f"{AIRTABLE_DB_URL}"  # reemplaza esto con tu URL de la API web de Airtable
  headers = {
      "Authorization": AIRTABLE_API_KEY,
      "Content-Type": "application/json"
  }
  data = {
      "records": [{
          "fields": {
              "Thread_id": thread_id,
              "Platform": platform,
              "Username": username
          }
      }]
  }

  try:
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
      print("Thread added to DB successfully.")
    else:
      # Handle non-200 HTTP response status codes
      print(
          f"Failed to add thread: HTTP Status Code {response.status_code}, Response: {response.text}"
      )
  except Exception as e:
    # Handle exceptions like network errors, request timeouts, etc.
    print(f"An error occurred while adding the thread: {e}")


def get_latest_record_id():
  headers = {
      "Authorization": AIRTABLE_API_KEY,
      "Content-Type": "application/json"
  }
  params = {
      "maxRecords": 1,
      "view": "All",
      "sort[0][field]": "Created",
      "sort[0][direction]": "desc"
  }
  response = requests.get(AIRTABLE_DB_URL, headers=headers, params=params)
  if response.status_code == 200:
    records = response.json().get('records', [])
    if records:
      latest_record = records[0]
      return latest_record[
          'id']  # Aquí cambiamos 'Thread_id' por 'id' para obtener el ID del registro.
    else:
      raise ValueError("No records found.")
  else:
    response.raise_for_status()

def process_run_status(thread_id, run_id, client, tool_data):
  start_time = time.time()
  while time.time(
  ) - start_time < 8:  # Mantén el bucle por menos de 8 segundos
    run_status = client.beta.threads.runs.retrieve(thread_id=thread_id,
                                                   run_id=run_id)
    logging.info(f"Checking run status: {run_status.status}")

    if run_status.status == 'completed':
      messages = client.beta.threads.messages.list(thread_id=thread_id)
      message_content = messages.data[0].content[0].text.value
      logging.info(f"Message content before cleaning: {message_content}")

      # Elimina las anotaciones
      message_content = re.sub(r"【.*?†.*?】", '', message_content)
      message_content = re.sub(r'[^\S\r\n]+', ' ', message_content).strip()

      # logging.info(f"Run completed, returning response: {message_content}")
      return {"response": message_content, "status": "completed"}

    elif run_status.status == 'requires_action':
      # Implementa aquí el manejo específico de las acciones requeridas si es necesario
      logging.info("Run requires action, handling...")
      for tool_call in run_status.required_action.submit_tool_outputs.tool_calls:
        function_name = tool_call.function.name

        try:
          arguments = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
          logging.error(
              f"JSON decoding failed: {e.msg}. Input: {tool_call.function.arguments}"
          )
          arguments = {}  # Set to default value

        # Use the function map from tool_data
        if function_name in tool_data["function_map"]:
          function_to_call = tool_data["function_map"][function_name]
          output = function_to_call(arguments)
          client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id,
                                                       run_id=run_id,
                                                       tool_outputs=[{
                                                           "tool_call_id":
                                                           tool_call.id,
                                                           "output":
                                                           json.dumps(output)
                                                       }])
        else:
          logging.warning(f"Function {function_name} not found in tool data.")
          break

    elif run_status.status == 'failed':
      logging.error("Run failed")
      return {"response": "error", "status": "failed"}

    time.sleep(2)  # Espera un poco antes de revisar nuevamente para evitar saturar el servidor

  logging.info("Run timed out")
  return {"response": "timeout", "status": "timeout"}

# Get all of the available resources
def get_resource_file_ids(client):
  file_ids = []
  resources_folder = 'resources'
  if os.path.exists(resources_folder):
    for filename in os.listdir(resources_folder):
      file_path = os.path.join(resources_folder, filename)
      if os.path.isfile(file_path):
        with open(file_path, 'rb') as file:
          response = client.files.create(file=file, purpose='assistants')
          file_ids.append(response.id)
  return file_ids


# Function to load tools from a file
def load_tools_from_directory(directory):
  tool_data = {"tool_configs": [], "function_map": {}}

  for filename in os.listdir(directory):
    if filename.endswith('.py'):
      module_name = filename[:-3]
      module_path = os.path.join(directory, filename)
      spec = importlib.util.spec_from_file_location(module_name, module_path)
      module = importlib.util.module_from_spec(spec)
      spec.loader.exec_module(module)

      # Load tool configuration
      if hasattr(module, 'tool_config'):
        tool_data["tool_configs"].append(module.tool_config)

      # Map functions
      for attr in dir(module):
        attribute = getattr(module, attr)
        if callable(attribute) and not attr.startswith("__"):
          tool_data["function_map"][attr] = attribute

  return tool_data
