import logging
from flask import Flask, request, jsonify
import core_functions
import assistant
from core_functions import client, process_run_status
import time
import json

# Configure loggingr
logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)  
logging.getLogger("werkzeug").setLevel(logging.WARNING)

# Check OpenAI version compatibility
core_functions.check_openai_version()

# Create Flask app
app = Flask(__name__)

# Initialize all available tools
tool_data = core_functions.load_tools_from_directory('tools')

# Create or load assistant
assistant_id = assistant.create_assistant(client, tool_data)


# Route to start the conversation and send thread info
@app.route('/start', methods=['GET'])
def start_conversation():
  # core_functions.check_api_key()  # Check the API key
  platform = request.args.get(
      'platform', 'Not Specified')  # Get the platform or use a default
  username = request.args.get(
      'username', None)  # Recupera el username del parámetro de la URL
  logging.info(
      f" -> Starting a new conversation from platform: {platform}, username: {username}"
  )
  thread = client.beta.threads.create()
  logging.info(f" -> New thread created with ID: {thread.id}")

  # Añade la información del thread, incluyendo el username si está disponible
  core_functions.add_thread(thread.id, platform, username)

  return jsonify({"thread_id": thread.id})


@app.route('/chat', methods=['POST'])
def chat():
  # core_functions.check_api_key()  # Check the API key
  data = request.json
  thread_id = data.get('thread_id')
  user_input = data.get('message', '')

  if not thread_id:
    logging.error(" -> Error: Missing thread_id")
    return jsonify({"error": "Missing thread_id"}), 400

  logging.info(
      f" -> Received message: {user_input} for thread ID: {thread_id}")

  # Start run and send run ID back to ManyChat
  client.beta.threads.messages.create(thread_id=thread_id,
                                      role="user",
                                      content=user_input)
  run = client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=assistant_id)
  print("Run started with ID:", run.id)

  return jsonify({"run_id": run.id})

# Check status of run
@app.route('/check', methods=['POST'])
def check_run_status():
  data = request.json
  thread_id = data.get('thread_id')
  run_id = data.get('run_id')
  if not thread_id or not run_id:
    print(" -> Error: Missing thread_id or run_id in /check")
    return jsonify({"response": "error"})

  result = process_run_status(thread_id, run_id, client, tool_data)
  return jsonify(result)


# start the app
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
