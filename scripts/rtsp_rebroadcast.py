import os
import requests

from dotenv import load_dotenv
load_dotenv()

## TO MODIFY ##
DETECTOR_CONFIGS = [
    {
        "name": "cell phone",
        "incs": ["cell phone"],
        "excs": ["wallet"]
    },
    {
        "name": "wallet",
        "incs": ["wallet"],
        "excs": [],
        
    }
]

TRACKER_CONFIG = {
    "stream_url": "rtsp://your_raw_stream_here", ## TO MODIFY ##
    "webhook_url": "WEBHOOK_TO_SEND_DETECTION_RESULTS", ## TO MODIFY ##
    "tracker_config": {
        "rebroadcast_annotations": "True",
        "detectors": DETECTOR_CONFIGS
    }
}

load_dotenv()
DIRECTAI_CLIENT_ID = os.getenv("DIRECTAI_CLIENT_ID")
DIRECTAI_CLIENT_SECRET = os.getenv("DIRECTAI_CLIENT_SECRET")
DIRECTAI_BASE_URL = "https://api.alpha.directai.io"
DIRECTAI_STREAM_URL = "https://watch.directai.io"

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


def start_rtsp_inference(access_token):
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    response = requests.post(
        f"{DIRECTAI_BASE_URL}/run_tracker_on_url_stream",
        headers=headers,
        json=TRACKER_CONFIG
    )
    response_json = response.json()
    tracker_instance_id = response_json["tracker_instance_id"]
    print(f"View stream here: rtsp://{DIRECTAI_STREAM_URL}/{tracker_instance_id}")
    return tracker_instance_id

def stop_rtsp_inference(access_token, tracker_instance_id):
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    response = requests.post(
        f"{DIRECTAI_BASE_URL}/stop_tracker?tracker_instance_id={tracker_instance_id}",
        headers=headers
    )
    return response.json()
   

if __name__ == '__main__':
    access_token = get_directai_access_token(DIRECTAI_CLIENT_ID, DIRECTAI_CLIENT_SECRET)
    tracker_instance_id = start_rtsp_inference(access_token)
    try:
        print("Press CTRL-C to stop stream.")
        while True:
            pass
    except KeyboardInterrupt:
        response = stop_rtsp_inference(access_token,tracker_instance_id)
        if "OK" in response["message"]:
            print("Stream inference stopped successfully.")
    