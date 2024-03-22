import os
import requests
import time
from copy import deepcopy

from dotenv import load_dotenv
load_dotenv()

from utils import get_directai_access_token
from scripts.rtsp_rebroadcast import stop_rtsp_inference, record_annotated_stream_via_hls, DIRECTAI_BASE_URL, DIRECTAI_STREAM_URL, DIRECTAI_CLIENT_ID, DIRECTAI_CLIENT_SECRET, HLS_OUTPUT_DIR
from scripts.classification_on_collection import deploy_classifier


CLASSIFIER_CONFIG = {
    "classifier_configs": [
        {
            "name": "thumbs up",
            "examples_to_include": [
                "thumbs up", "person giving thumbs up"
            ],
            "examples_to_exclude": []
        },
        {
            "name": "thumbs down",
            "examples_to_include": [
                "thumbs down", "person giving thumbs down"
            ],
        },
        {
            "name": "peace sign",
            "examples_to_include": [
                "peace sign", "person giving peace sign"
            ],
        },
        {
            "name": "no gesture",
            "examples_to_include": [
                "person"
            ],
            "examples_to_exclude": [
                "person making a gesture"
            ]
        }
    ]
}


STREAMING_CLASSIFIER_CONFIG = {
    "stream_url": "YOUR_RTSP_URL", ## TO MODIFY ##
    "webhook_url": "WEBHOOK_TO_SEND_DETECTION_RESULTS", ## TO MODIFY ##
    "rebroadcast_annotations": "True",
    "deployed_id": None  # This will be filled in automatically
}


def start_rtsp_inference(access_token):
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    classifier_id = deploy_classifier(CLASSIFIER_CONFIG, access_token)
    streaming_classifier_config = deepcopy(STREAMING_CLASSIFIER_CONFIG)
    streaming_classifier_config["deployed_id"] = classifier_id
    response = requests.post(
        f"{DIRECTAI_BASE_URL}/run_classifier_on_url_stream",
        headers=headers,
        json=streaming_classifier_config
    )
    response_json = response.json()
    tracker_instance_id = response_json["tracker_instance_id"]
    print(f"View stream here: {DIRECTAI_STREAM_URL}/{tracker_instance_id}")
    return tracker_instance_id


if __name__ == '__main__':
    access_token = get_directai_access_token(DIRECTAI_CLIENT_ID, DIRECTAI_CLIENT_SECRET)
    tracker_instance_id = start_rtsp_inference(access_token)
    
    if HLS_OUTPUT_DIR is not None:
        # wait for the stream to start
        print("Waiting 10 seconds for stream to start so we can record it...")
        time.sleep(10)
        try:
            print("Recording stream...")
            record_annotated_stream_via_hls(f"{DIRECTAI_STREAM_URL}/{tracker_instance_id}", HLS_OUTPUT_DIR)
        except Exception as e:
            print(f"Error recording stream: {e}")
    else:
        print("HLS_OUTPUT_DIR not set. Not recording stream.")
        
    try:
        print("Press CTRL-C to stop stream.")
        while True:
            pass
    except KeyboardInterrupt:
        response = stop_rtsp_inference(access_token,tracker_instance_id)
        if "OK" in response["message"]:
            print("Stream inference stopped successfully.")