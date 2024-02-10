import requests

# URL base de la API de World Time
BASE_URL = "http://worldtimeapi.org/api/timezone/"

# Configuración de la herramienta
tool_config = {
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description":
        "Obtains the current time from the World Time API for a specific timezone.",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type":
                    "string",
                    "description":
                    "The timezone to get the current time for. Defaults to America/Mexico_City if not specified."
                }
            },
            "required": []
        }
    }
}


# La función de devolución de llamada
def get_current_time(arguments):
  """
    Realiza una solicitud HTTP GET a la API de World Time para obtener la hora actual en la zona horaria especificada.
    Si no se especifica una zona horaria, utiliza por defecto America/Mexico_City.

    :param arguments: dict, Contiene la zona horaria especificada por el usuario.
                      Espera la clave 'timezone'.
    :return: dict o str, Respuesta con la hora actual o mensaje de error.
    """

  # Extracción de la zona horaria de los argumentos, con un valor predeterminado si no se proporciona
  timezone = arguments.get('timezone', 'America/Mexico_City')

  # Construcción de la URL completa
  url = BASE_URL + timezone

  # Realización de la solicitud HTTP GET
  try:
    response = requests.get(url)
    if response.status_code == 200:
      data = response.json()
      # Extracción y retorno de la información relevante de la respuesta
      current_time = data.get('datetime')
      return {"message": f"The current time in {timezone} is: {current_time}"}
    else:
      # Manejo de respuestas de error de la API
      return f"Error retrieving the current time for {timezone}: {response.text}"
  except requests.exceptions.RequestException as e:
    # Manejo de errores de conectividad
    return f"Failed to connect to the World Time API: {e}"
