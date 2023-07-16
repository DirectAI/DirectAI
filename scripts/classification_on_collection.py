import os
import sys
import argparse
import json
import requests

from dotenv import load_dotenv
from tqdm import tqdm

parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_directory)
from utils import get_directai_access_token, get_file_data


load_dotenv()
DIRECTAI_CLIENT_ID = os.getenv("DIRECTAI_CLIENT_ID")
DIRECTAI_CLIENT_SECRET = os.getenv("DIRECTAI_CLIENT_SECRET")
DIRECTAI_BASE_URL = "https://api.alpha.directai.io"

def main():
    # Initialize the parser
    parser = argparse.ArgumentParser(description="Classification on Data Collection.")
    parser.add_argument("-d", "--data_dir", help="Directory for Input Data", default="data")
    parser.add_argument("-r", "--results_dir", help="Directory for Results", default="results")
    parser.add_argument("-f", "--config_file_path", help="File Path for Classifier Configuration", default="configs/classifier.json" )
    parser.add_argument("-c", "--classes", help="List of Classes to Predict", default="")
    
    # Parse the arguments
    args = parser.parse_args()
    if args.classes != "":
        classes_list = eval(args.classes)
        classifier_configs = [{
            'name': class_name,
            'examples_to_include': [class_name],
            'examples_to_exclude': []
        } for class_name in classes_list]
        body = {'classifier_configs': classifier_configs}
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
    
    # Deploy Classifier
    deploy_response = requests.post(
        f"{DIRECTAI_BASE_URL}/deploy_classifier",
        headers=headers,
        json=body
    )
    if deploy_response.status_code != 200:
        raise ValueError(deploy_response.json()['message'])
    deployed_classifier_id = deploy_response.json()

    
    # Compiled Results
    results = {}
    
    # Run Classification on Data Collection
    for filename in tqdm(os.listdir(args.data_dir)):
        if filename == '.DS_Store':
            continue
        params = {
            'deployed_id': deployed_classifier_id
        }
        file_data = get_file_data(f"{args.data_dir}/{filename}")
        response = requests.post(
            f"{DIRECTAI_BASE_URL}/classify",
            headers=headers, 
            params=params,
            files=file_data
        )
        results[filename] = response.json()
    
    # Save Inference Results
    with open(f"{args.results_dir}/classification_results.json", 'w') as f:
        json.dump(results, f)
    
if __name__ == '__main__':
    main()
    
    