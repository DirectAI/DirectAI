import requests
import os
import sys
import hashlib
import cv2

parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_directory)

# get the authorization token
def get_directai_access_token(
    client_id,
    client_secret,
    auth_endpoint = "https://api.alpha.directai.io/token"
):
    params = {
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(auth_endpoint,params=params)
    if response.status_code != 200:
        raise ValueError("Invalid DirectAI Credentials")
    return response.json()["access_token"]

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

def get_color(class_id):
    # Use a hash function to generate a unique and stable color for each class_id
    hash_object = hashlib.md5(class_id.encode())
    hex_dig = hash_object.hexdigest()
    r = int(hex_dig[0:2], 16)
    g = int(hex_dig[2:4], 16)
    b = int(hex_dig[4:6], 16)
    color = (b, g, r)  # OpenCV uses BGR format

    return color

def display_bounding_boxes(image, dets):
    # image is assumed to be an OpenCV image
    colors = {}
    for bbox in dets:
        tlbr = bbox['tlbr']
        score = bbox['score']
        label = bbox['class']
        top_left = (int(tlbr[0]), int(tlbr[1]))
        bottom_right = (int(tlbr[2]), int(tlbr[3]))
        
        if label not in colors:
            colors[label] = get_color(label)
        color = colors[label]
        cv2.rectangle(image, top_left, bottom_right, color, 3)
        cv2.putText(image, f'{label} {score:.2f}', (top_left[0], top_left[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 3)
    
    return image