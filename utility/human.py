import os
import requests
import json
from core_functions import get_latest_record_id
from urllib.parse import unquote

WEBHOOK_URL = os.environ['WEBHOOK_URL']
# Webhook URL configured in the environment variables

# The tool configuration
tool_config = {
    "type": "function",
    "function": {
        "name": "human_assistance_request",
        "description":
        "Detects requests for an intention to buy something and collects user contact information.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description":
                    "Name of the user requesting to buy something."
                },
                "phone_number": {
                    "type": "string",
                    "description": "Phone number of the user."
                },
                "address": {
                    "type": "string",
                    "description": "Physical address of the user."
                }
            },
            "required": ["name", "phone_number", "address"]
        }
    }
}


# The callback function (Sends data to the Webhook URL)
def human_assistance_request(arguments):
  """
  Detects requests for the intention to buy, validates user's contact information,
  and sends them to a Webhook URL. If any information is missing or incorrect, 
  it asks the user to provide the correct information.

  :param arguments: dict, Contains the user's contact information and thread ID.
                    Expected keys: name, email, phone_number, address, thread_id.
  :return: dict or str, Response from the webhook, error message, or request for correct information.
  """

  # Extracción y validación de los campos
  name = unquote(unquote(arguments.get('name')))
  phone_number = arguments.get('phone_number')
  address = unquote(unquote(arguments.get('address')))
  record_id = get_latest_record_id()

  # Inclusión del thread_id en el payload
  data = {
      "name": name,
      "phone_number": phone_number,
      "address": address,
      "record_id": record_id
  }
  # Sending the data to the Webhook URL
  try:
    response = requests.post(WEBHOOK_URL,
                             headers={"Content-Type": "application/json"},
                             data=json.dumps(data))
    if response.status_code == 200:
      return "Your request for human assistance has been received. We will contact you soon."
    else:
      return f"Error processing your request for human assistance: {response.text}"
  except requests.exceptions.RequestException as e:
    return f"Failed to send data to the webhook: {e}"
