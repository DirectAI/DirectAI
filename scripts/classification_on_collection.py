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

def get_classifier_body(config_file_path, class_name=None):
    if (class_name is not None) and len(class_name) > 0:
        classifier_configs = []
        for single_class in class_name:
            classifier_configs.append({
                'name': single_class,
                'examples_to_include': [single_class],
                'examples_to_exclude': []
            })
        body = {'classifier_configs': classifier_configs}
    else:
        with open(config_file_path) as f:
            body = json.loads(f.read())
    
    return body

def deploy_classifier(host, body, access_token):
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    
    # Deploy Classifier
    deploy_response = requests.post(
        f"{host}/deploy_classifier",
        headers=headers,
        json=body
    )
    if deploy_response.status_code != 200:
        raise ValueError(deploy_response.json()['message'])
    deployed_classifier_id = deploy_response.json()['deployed_id']
    
    return deployed_classifier_id

def prep_classification_results_dir(body, results_dir):
    # Prepares Results Directory
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    for config in body['classifier_configs']:
        label = config['name']
        class_dir = f"{results_dir}/{label}"
        if os.path.exists(class_dir):
            shutil.rmtree(class_dir) 
        os.makedirs(class_dir)

@click.command()
@click.option('-h', '--host', default='https://api.alpha.directai.io', help='DirectAI Host')
@click.option('-d', '--data-dir', default='data', help='Directory for Input Data')
@click.option('-r', '--results-dir', default='results', help='Directory for Results')
@click.option('-f', '--config-file-path', default='configs/classifier.json', help='File Path for Classifier Configuration')
@click.option('-c', '--class-name', help='Class to Predict', multiple=True)
def main(host, data_dir, results_dir, config_file_path, class_name):
    # Get Access Token
    access_token = get_directai_access_token(
        client_id=DIRECTAI_CLIENT_ID,
        client_secret=DIRECTAI_CLIENT_SECRET,
        auth_endpoint=host+"/token"
    )
    
    classifier_body = get_classifier_body(config_file_path, class_name)
    deployed_classifier_id = deploy_classifier(host, classifier_body, access_token)
    prep_classification_results_dir(classifier_body, results_dir)
    # Compiled Results
    results = {}
    
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    
    # Run Classification on Data Collection
    for filename in tqdm(os.listdir(data_dir)):
        if filename == '.DS_Store':
            continue
        params = {
            'deployed_id': deployed_classifier_id
        }
        file_data = get_file_data(f"{data_dir}/{filename}")
        classify_response = requests.post(
            f"{host}/classify",
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
    
    