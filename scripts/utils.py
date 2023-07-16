import requests
import os
import sys

parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_directory)

# get the authorization token
def get_directai_access_token(
    client_id,
    client_secret,
    auth_endpoint = "https://oauth.directai.io/token"
):
    body = {
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(auth_endpoint,json=body)
    response_json = response.json()
    if response_json['statusCode'] != 200:
        raise ValueError("Invalid DirectAI Credentials")
    return response.json()["body"]["access_token"]

def get_file_data(fp):
    # Open the file in binary mode
    suffix = fp.split('.')[-1].lower()
    
    if suffix == 'jpeg' or suffix == 'jpg':
        image_type = 'image/jpg'
    elif suffix == 'png':
        image_type = 'image/png'
    else:
        raise ValueError(f"{fp} is an unsupported image type")
    
    with open(fp, 'rb') as f:
        file_data = f.read()

    # Create the files dictionary
    files = {
        'data': (fp, file_data, image_type),
    }
    return files