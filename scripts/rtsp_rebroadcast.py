import os
import requests
import time

from dotenv import load_dotenv
load_dotenv()

from utils import get_directai_access_token

## TO MODIFY ##
# NOTE: for the object tracker, as opposed to the object detector, objects are not mutually exclusive
# which means if we want the same object to not be detected twice, we need to set up the exclusions

REBROADCAST_FORMAT = "webrtc"

DETECTOR_CONFIGS = [
    {
        "name": "cell phone",
        "incs": ["cell phone"],
        "excs": ["wallet"]
    },
    {
        "name": "wallet",
        "incs": ["wallet"],
        "excs": ["cell phone"],
        
    }
]

TRACKER_CONFIG = {
    "rebroadcast_format": REBROADCAST_FORMAT,
    "stream_url": "rtsp://100.66.146.61:8554/isaac_webcam", ## TO MODIFY ##
    "webhook_url": "WEBHOOK_TO_SEND_DETECTION_RESULTS", ## TO MODIFY ##
    "tracker_config": {
        "rebroadcast_annotations": "True",
        "detectors": DETECTOR_CONFIGS
    }
}

DIRECTAI_CLIENT_ID = os.getenv("DIRECTAI_CLIENT_ID")
DIRECTAI_CLIENT_SECRET = os.getenv("DIRECTAI_CLIENT_SECRET")
DIRECTAI_BASE = "100.66.146.61"
DIRECTAI_BASE_URL = f"http://{DIRECTAI_BASE}:8000"
if REBROADCAST_FORMAT == "rtsp":
    DIRECTAI_STREAM_URL = f"rtsp://{DIRECTAI_BASE}:8554"
else:
    DIRECTAI_STREAM_URL = f"{DIRECTAI_BASE}:8889"

HLS_OUTPUT_DIR = None ## TO MODIFY ##


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
    print(f"View stream here: {DIRECTAI_STREAM_URL}/{tracker_instance_id}")
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


def record_annotated_stream_via_hls(rtsp_url, hls_output_dir):
    if hls_output_dir is None:
        raise ValueError("HLS Output Directory not set.")
    
    # make the directory if it doesn't exist
    if not os.path.exists(hls_output_dir):
        os.makedirs(hls_output_dir)
    # empty it if it does
    else:
        for file in os.listdir(hls_output_dir):
            file_path = os.path.join(hls_output_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
    
    # switch to running the ffmpeg command to transmux the broadcasted stream to HLS
    os.system(f"ffmpeg -rtsp_transport tcp -i {rtsp_url} -f hls -hls_time 5 -hls_list_size 0 -hls_segment_filename '{hls_output_dir}/segment_%05d.ts' {hls_output_dir}/playlist.m3u8")


if __name__ == '__main__':
    access_token = get_directai_access_token(DIRECTAI_CLIENT_ID, DIRECTAI_CLIENT_SECRET)
    tracker_instance_id = start_rtsp_inference(access_token)
    
    if HLS_OUTPUT_DIR is not None and REBROADCAST_FORMAT == "rtsp":
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
    