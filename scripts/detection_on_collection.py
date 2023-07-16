import os
import sys
import argparse
import json
import requests
import cv2

from dotenv import load_dotenv
from tqdm import tqdm

parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_directory)
from utils import (
    get_directai_access_token, 
    get_file_data, 
    display_bounding_boxes
)


load_dotenv()
DIRECTAI_CLIENT_ID = os.getenv("DIRECTAI_CLIENT_ID")
DIRECTAI_CLIENT_SECRET = os.getenv("DIRECTAI_CLIENT_SECRET")
DIRECTAI_BASE_URL = "https://api.alpha.directai.io"
DEFAULT_OBJECT_DETECTION_THRESHOLD = 0.1
DEFAULT_NMS_THRESHOLD = 0.4

def main():
    # Initialize the parser
    parser = argparse.ArgumentParser(description="Detection on Data Collection.")
    parser.add_argument("-d", "--data_dir", help="Directory for Input Data", default="data")
    parser.add_argument("-r", "--results_dir", help="Directory for Results", default="results")
    parser.add_argument("-f", "--config_file_path", help="File Path for Detection Configuration", default="configs/detector.json" )
    parser.add_argument("-c", "--classes", help="List of Classes to Detect", default="")
    parser.add_argument('-b', '--bounding_box_drawing', action='store_true', default=False, help='Flag to draw bounding boxes on images')
    
    # Parse the arguments
    args = parser.parse_args()
    if args.classes != "":
        classes_list = eval(args.classes)
        detector_configs = [{
            'name': class_name,
            'examples_to_include': [class_name],
            'examples_to_exclude': [],
            'detection_threshold': DEFAULT_OBJECT_DETECTION_THRESHOLD
        } for class_name in classes_list]
        body = {
            'detector_configs': detector_configs,
            'nms_threshold': DEFAULT_NMS_THRESHOLD
        }
    else:
        with open(args.config_file_path) as f:
            body = json.loads(f.read())
    
    # Get Access Token
    access_token = get_directai_access_token(
        client_id=DIRECTAI_CLIENT_ID,
        client_secret=DIRECTAI_CLIENT_SECRET
    )
    
    headers = {
        'Authorization': access_token
    }
    
    # Deploy Detector
    deploy_response = requests.post(
        f"{DIRECTAI_BASE_URL}/deploy_detector",
        headers=headers,
        json=body
    )
    if deploy_response.status_code != 200:
        raise ValueError(deploy_response.json())
    deployed_detector_id = deploy_response.json()

    
    # Compiled Results
    results = {}
    
    # Run Classification on Data Collection
    for filename in tqdm(os.listdir(args.data_dir)):
        if filename == '.DS_Store':
            continue
        params = {
            'deployed_id': deployed_detector_id
        }
        file_data = get_file_data(f"{args.data_dir}/{filename}")
        response = requests.post(
            f"{DIRECTAI_BASE_URL}/detect",
            headers=headers, 
            params=params,
            files=file_data
        )
        dets = response.json()
        
        
        cv2_img = cv2.imread(f"{args.data_dir}/{filename}")
        drawn_image = display_bounding_boxes(cv2_img, dets[0])
        
        if args.bounding_box_drawing:
            cv2.imwrite(f'results/annotated_{filename}'.format(), drawn_image)
        results[filename] = dets[0]
    
    # Save Inference Results
    with open(f"{args.results_dir}/detection_results.json", 'w') as f:
        json.dump(results, f)
    
if __name__ == '__main__':
    main()
    
    