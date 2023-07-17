# DirectAI
## computer vision without training data

### Startup Instructions
- This was tested with `Python` 3.11.2 & `pip` 23.0.1. 
- Make sure to add your credentials after running `cp .env.template .env`.
- Install requirements via `pip install -r requirements.txt`. We specify package versions and can't guarantee performance with different versions.

### Running Classification
- **Quickstart**: From the root directory, execute `python scripts/classification_on_collection`.
- Add image data that you're interested in running a classification model on to the `data` folder. 
- You can specify classes of interest via the command line (e.g. `-c dog -c cat`) or with a filepath that points to a json (e.g. `configs/classifier.json`). 
- Arguments:
    - `-d` or `"--data_dir` specifies the "Directory for Input Data". It defaults to "data". We accept `.png` and `.jpg` image formats. We've added a few samples from [this dataset](https://universe.roboflow.com/roboflow-100/furniture-ngpea) to the folder already! 
    - `-r` or `"--results_dir` specifies the "Directory for Results". It defaults to "results". We write `classification_results.json` to this directory. It specifies classification scores and ultimate class prediction for each input image.
    - `-f` or `"--config_file_path` specifies the "File Path for Classifier Configuration". It defaults to "configs/classifier.json".
    - `-c` or `"--classes` specifies the "List of Classes to Predict". If this is defined, it will replace the `config_file_path` argument. We expect each class to be of the form `-c {CLASS_NAME}`. 
        - Repeat as necessary (e.g. `python scripts/classification_on_collection -c dog -c parrot -c cat -c bear`)

### Running Detection
- **Quickstart**: From the root directory, execute `python scripts/detection_on_collection -b`.
- Add image data that you're interested in running a detection model on to the `data` folder. 
- You can specify bojects of interest via the command line (e.g. `-c dog -c cat`) or with a filepath that points to a json (e.g. `configs/detector.json`). 
- Arguments:
    - `-d` or `"--data_dir` specifies the "Directory for Input Data". It defaults to "data". We accept `.png` and `.jpg` image formats. We've added a few samples from [this dataset](https://universe.roboflow.com/roboflow-100/furniture-ngpea) to the folder already! 
    - `-r` or `"--results_dir` specifies the "Directory for Results". It defaults to "results". We write `detection_results.json` to this directory. It specifies classification scores and ultimate class prediction for each input image.
    - `-f` or `"--config_file_path` specifies the "File Path for Classifier Configuration". It defaults to "configs/classifier.json".
    - `-c` or `"--classes` specifies the "List of Classes to Predict". If this is defined, it will replace the `config_file_path` argument. We expect each class to be of the form `-c {CLASS_NAME}`. 
        - Repeat as necessary (e.g. `python scripts/classification_on_collection -c dog -c parrot -c cat -c bear`)
    - `-b` or `"--bounding_box_drawing` is a "Flag to draw bounding boxes on images". If used, it will save annotated images to the `results_dir` folder. 
