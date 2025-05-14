import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
api_token = os.getenv('CE_API_TOKEN')

# Get the base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def post_bulk_publish(payload):
    """
    Sends a POST request to the bulk publish endpoint with the given payload.
 
    Args:
        payload (dict): The JSON payload to be sent in the POST request.
 
    Returns:
        Response object: The HTTP response object from the server.
    """
    # Endpoint URL
    url = "https://sandbox.credentialengine.org/assistant/SupportService/bulkpublish"
 
    # Headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"APIToken {api_token}",
        "PublishForOrganizationIdentifier": "ce-3508747f-4ca5-412f-bd38-6b0fb2d1132c"
    }
 
    try:
        # Make the POST request
        print(f"{payload}")
        response = requests.post(url, headers=headers, json=json.loads(payload))
 
        # Check response status
        if response.status_code == 200:
            print("Request successful!")
            if not os.path.exists(os.path.join(BASE_DIR, 'uploads')):
                os.makedirs(os.path.join(BASE_DIR, 'uploads'))
            
            # Save the publish log to a file
            publish_log_path = os.path.join(BASE_DIR, 'uploads', 'publish_log.json')
            with open(publish_log_path, "w") as json_file:
                json.dump(response.json(), json_file, indent=2)
        else:
            print(f"Request failed with status code {response.status_code}")
            print("Response:", response.text)
 
        return response
 
    except Exception as e:
        print("An error occurred:", e)
        return None