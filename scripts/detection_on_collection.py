import os
import sys
import json
import requests
import cv2
import click

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


@click.command()
@click.option('-d', '--data-dir', default='data', help='Directory for Input Data')
@click.option('-r', '--results-dir', default='results', help='Directory for Results')
@click.option('-f', '--config-file-path', default='configs/detector.json', help='File Path for Classifier Configuration')
@click.option('-b', '--bounding-box-drawing', is_flag=True, default=False, help='Flag to draw bounding boxes on images')
@click.option('-c', '--class-name', help='Class to Predict', multiple=True)
def main(data_dir, results_dir, config_file_path, bounding_box_drawing, class_name):
    if len(class_name) > 0:
        detector_configs = []
        for single_class in class_name:
            detector_configs.append({
                'name': single_class,
                'examples_to_include': [single_class],
                'examples_to_exclude': [],
                'detection_threshold': DEFAULT_OBJECT_DETECTION_THRESHOLD
            })
        body = {
            'detector_configs': detector_configs,
            'nms_threshold': DEFAULT_NMS_THRESHOLD
        }
    else:
        with open(config_file_path) as f:
            body = json.loads(f.read())
    
    # Get Access Token
    access_token = get_directai_access_token(
        client_id=DIRECTAI_CLIENT_ID,
        client_secret=DIRECTAI_CLIENT_SECRET,
        auth_endpoint=DIRECTAI_BASE_URL+"/token"
    )
    
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    
    # Deploy Detector
    deploy_response = requests.post(
        f"{DIRECTAI_BASE_URL}/deploy_detector",
        headers=headers,
        json=body
    )
    if deploy_response.status_code != 200:
        raise ValueError(deploy_response.json())
    deployed_detector_id = deploy_response.json()['deployed_id']

    
    # Compiled Results
    results = {}
    
    # Run Classification on Data Collection
    for filename in tqdm(os.listdir(data_dir)):
        if filename == '.DS_Store':
            continue
        params = {
            'deployed_id': deployed_detector_id
        }
        file_data = get_file_data(f"{data_dir}/{filename}")
        detect_response = requests.post(
            f"{DIRECTAI_BASE_URL}/detect",
            headers=headers, 
            params=params,
            files=file_data
        )
        if detect_response.status_code != 200:
            raise ValueError(detect_response.json())
        dets = detect_response.json()
        
        cv2_img = cv2.imread(f"{data_dir}/{filename}")
        drawn_image = display_bounding_boxes(cv2_img, dets[0])
        
        if bounding_box_drawing:
            cv2.imwrite(f'{results_dir}/annotated_{filename}'.format(), drawn_image)
        results[filename] = dets[0]
    
    # Save Inference Results
    with open(f"{results_dir}/detection_results.json", 'w') as f:
        json.dump(results, f)
    
if __name__ == '__main__':
    main()
    
    