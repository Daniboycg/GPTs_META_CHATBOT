# META Chatbot Template
## Overview
This project integrates the advanced capabilities of the ChatGPT model to create an AI Chatbot designed to interact with users across various META platforms, including Facebook, Instagram, and WhatsApp. Utilizing Replit for backend operations and ManyChat for the frontend, this Chatbot emulates the persona of Marcus Aurelius, drawing on his work "Meditations" to deliver responses.

It is easier if you just fork it in Replit tbh: [repo](https://replit.com/@danielcarreonwo/METACHATBOT)  
Here you have the entire system: [Chatbot_System](https://www.figma.com/file/P5JSYAMUNJsRYqAzGK2VHV/Chatbot_System?type=whiteboard&t=vU2poAV7c6gdbqpO-6)

## Features
Emulates Marcus Aurelius' persona to provide philosophical advice and insights.
Backend built on Replit, leveraging the power of OpenAI's GPT-4 model.
Frontend interface managed through ManyChat, providing a seamless user experience.
Incorporates a webhook system for live human interaction when requested.
Integrates with the World Time API to provide timezone-specific time data.
Utilizes Airtable for database management to track conversations and users.

## Structure
The application consists of several Python modules:

`assistant.py`: Manages the creation or loading of the assistant's instance.  
`core_functions.py`: Contains the core functionalities including the OpenAI client initialization, version checking, database operations, and run status processing.  
`main.py`: The Flask server that handles the web routes for starting conversations, chatting, and checking run status.  
`prompt.py`: Defines the assistant's instructions and behavior to emulate Marcus Aurelius.  
`datetime.py`: Contains the configuration and callback function for obtaining the current time based on a given timezone.  

## Installation and Setup
To set up the project, follow these steps:

Clone the repository to your local machine or Replit instance.
Install the required dependencies by running pip install -r requirements.txt.
Set the necessary environment variables for OpenAI API Key, Airtable API Key, and Webhook URL.
Run main.py to start the Flask server.
Usage

## To interact with the Chatbot:

Start a conversation using the /start endpoint with platform and username parameters.
Send user inputs to the /chat endpoint with the thread_id received from the start.
Check the status of the conversation using the /check endpoint with thread_id and run_id.

License
This project is licensed under the MIT License - see the LICENSE file for details.
