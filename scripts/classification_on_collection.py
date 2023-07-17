import os
import sys
import json
import requests
import shutil
import click

from dotenv import load_dotenv
from tqdm import tqdm

parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_directory)
from utils import get_directai_access_token, get_file_data


load_dotenv()
DIRECTAI_CLIENT_ID = os.getenv("DIRECTAI_CLIENT_ID")
DIRECTAI_CLIENT_SECRET = os.getenv("DIRECTAI_CLIENT_SECRET")
DIRECTAI_BASE_URL = "https://api.alpha.directai.io"

@click.command()
@click.option('-d', '--data-dir', default='data', help='Directory for Input Data')
@click.option('-r', '--results-dir', default='results', help='Directory for Results')
@click.option('-f', '--config-file-path', default='configs/classifier.json', help='File Path for Classifier Configuration')
@click.option('-c', '--classes', help='List of Classes to Predict', multiple=True)
def main(data_dir, results_dir, config_file_path, classes):
    if len(classes) > 0:
        classifier_configs = []
        for class_name in classes:
            classifier_configs.append({
                'name': class_name,
                'examples_to_include': [class_name],
                'examples_to_exclude': []
            })
        body = {'classifier_configs': classifier_configs}
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
    
    # Deploy Classifier
    deploy_response = requests.post(
        f"{DIRECTAI_BASE_URL}/deploy_classifier",
        headers=headers,
        json=body
    )
    if deploy_response.status_code != 200:
        raise ValueError(deploy_response.json()['message'])
    deployed_classifier_id = deploy_response.json()['deployed_id']

    
    # Compiled Results
    results = {}
    
    # Prepares Results Directory
    for config in body['classifier_configs']:
        label = config['name']
        class_dir = f"{results_dir}/{label}"
        if os.path.exists(class_dir):
            shutil.rmtree(class_dir) 
        os.makedirs(class_dir)
    
    # Run Classification on Data Collection
    for filename in tqdm(os.listdir(data_dir)):
        if filename == '.DS_Store':
            continue
        params = {
            'deployed_id': deployed_classifier_id
        }
        file_data = get_file_data(f"{data_dir}/{filename}")
        classify_response = requests.post(
            f"{DIRECTAI_BASE_URL}/classify",
            headers=headers, 
            params=params,
            files=file_data
        )
        if classify_response.status_code != 200:
            raise ValueError(classify_response.json())
        results[filename] = classify_response.json()
        prediction = results[filename]['pred']
        shutil.copy(
            f"{data_dir}/{filename}",
            f"{results_dir}/{prediction}/{filename}"
        )
    
    # Save Inference Results
    with open(f"{results_dir}/classification_results.json", 'w') as f:
        json.dump(results, f)
    
if __name__ == '__main__':
    main()
    
    