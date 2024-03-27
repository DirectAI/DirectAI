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
from classification_on_collection import get_classifier_body, deploy_classifier, prep_classification_results_dir


load_dotenv()
DIRECTAI_CLIENT_ID = os.getenv("DIRECTAI_CLIENT_ID")
DIRECTAI_CLIENT_SECRET = os.getenv("DIRECTAI_CLIENT_SECRET")


@click.command()
@click.option('-h', '--host', default='https://api.alpha.directai.io', help='DirectAI Host')
@click.option('-d', '--data-dir', default='data', help='Directory for Input Data')
@click.option('-r', '--results-dir', default='results', help='Directory for Results')
@click.option('-f', '--config-file-paths', default=['configs/classifier.json', 'configs/alt_classifier.json'], help='File Path(s) for Classifier Configuration', multiple=True)
def main(host, data_dir, results_dir, config_file_paths):
    # Get Access Token
    access_token = get_directai_access_token(
        client_id=DIRECTAI_CLIENT_ID,
        client_secret=DIRECTAI_CLIENT_SECRET,
        auth_endpoint=host+"/token"
    )
    
    deployed_classifier_ids = []
    classifier_results_dirs = []
    if len(config_file_paths) > 0:
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        for config_file_path in config_file_paths:
            # Model Deployment Prep
            classifier_body = get_classifier_body(config_file_path)
            deployed_classifier_id = deploy_classifier(classifier_body, access_token)
            deployed_classifier_ids.append(deployed_classifier_id)
            # Results Directory Prep
            stripped_config_name = config_file_path.split("/")[-1].split(".")[0]
            classifier_results_dir = f"{results_dir}/{stripped_config_name}"
            classifier_results_dirs.append(classifier_results_dir)
            prep_classification_results_dir(classifier_body, classifier_results_dir)
    else:
        print("Please provide config file paths. Exiting.")
        return
    
    headers = {
        'Authorization': f"Bearer {access_token}"
    }
    
    # Compiled Results
    results = {}
    
    # Run Classification on Data Collection
    for filename in tqdm(os.listdir(data_dir)):
        if filename == '.DS_Store':
            continue
        params = {
            'deployed_ids': deployed_classifier_ids
        }
        file_data = get_file_data(f"{data_dir}/{filename}")
        classify_response = requests.post(
            f"{host}/multi_classify",
            headers=headers, 
            params=params,
            files=file_data
        )
        if classify_response.status_code != 200:
            raise ValueError(classify_response.json())
        results[filename] = classify_response.json()
        for classifier_results_dir, deployed_classifier_id in zip(classifier_results_dirs, deployed_classifier_ids):
            prediction = results[filename][deployed_classifier_id]['pred']
            stripped_config_name = config_file_path.split("/")[-1].split(".")[0]
            shutil.copy(
                f"{data_dir}/{filename}",
                f"{classifier_results_dir}/{prediction}/{filename}"
            )
    
    # Save Inference Results
    with open(f"{results_dir}/multi_classification_results.json", 'w') as f:
        json.dump(results, f)
    
if __name__ == '__main__':
    main()
    
    