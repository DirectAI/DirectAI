# DirectAI
## computer vision without training data

### Startup Instructions
- This was tested with `Python` 3.11.2.
- Make sure to add your credentials after running `cp .env.template .env`. See [API docs](https://api.alpha.directai.io/docs) for instructions on credential generation.
- Install requirements via `pip install -r requirements.txt`. We specify package versions and can't guarantee performance with different versions.

### Running Classification
- **Quickstart**: From the root directory, execute `python scripts/classification_on_collection.py`.
- Add image data that you're interested in running a classification model on to the `data` folder. 
- You can specify classes of interest via the command line (e.g. `-c dog -c cat`) or with a filepath that points to a json (e.g. `configs/classifier.json`). 
- Arguments:
    - `-d` or `--data_dir` specifies the "Directory for Input Data". It defaults to "data". We accept `.png` and `.jpg` image formats. We've added a few samples from [Pexels](https://www.pexels.com/) to the folder already! 
    - `-r` or `--results_dir` specifies the "Directory for Results". It defaults to "results". We write `classification_results.json` to this directory. It specifies classification scores and ultimate class prediction for each input image.
    - `-f` or `--config_file_path` specifies the "File Path for Classifier Configuration". It defaults to "configs/classifier.json".
    - `-c` or `--classes` specifies the "List of Classes to Predict". If this is defined, it will replace the `config_file_path` argument. We expect each class to be of the form `-c {CLASS_NAME}`. 
        - Repeat as necessary (e.g. `python scripts/classification_on_collection.py -c dog -c parrot -c cat -c bear`)

### Running Multi-Classification
- **Quickstart**: From the root directory, execute `python scripts/multi_classify_on_collection.py`.
- Add image data that you're interested in running multiple parallel classification models on to the `data` folder. 
- You can specify multiple classifiers of interest with several filepaths that point to a json (e.g. `configs/classifier.json` & `configs/alt_classifier.json`). 
- Arguments:
    - `-d` or `--data_dir` specifies the "Directory for Input Data". It defaults to "data". We accept `.png` and `.jpg` image formats. We've added a few samples from [Pexels](https://www.pexels.com/) to the folder already! 
    - `-r` or `--results_dir` specifies the "Directory for Results". It defaults to "results". We write `multi_classification_results.json` to this directory. It specifies classification scores and ultimate class prediction for each input image.
    - `-f` or `--config_file_paths` specifies the "File Path(s) for Classifier Configuration". It defaults to [`configs/classifier.json`, `configs/alt_classifier.json`].
        - Repeat as necessary (e.g. `python scripts/multi_classify_on_collection.py -f configs/classifier.json -f configs/alt_classifier.json -f configs/my_third_classifier.json`)

### Running Detection
- **Quickstart**: From the root directory, execute `python scripts/detection_on_collection.py -b`.
- Add image data that you're interested in running a detection model on to the `data` folder. 
- You can specify objects of interest via the command line (e.g. `-c dog -c cat`) or with a filepath that points to a json (e.g. `configs/detector.json`). 
- Arguments:
    - `-d` or `--data_dir` specifies the "Directory for Input Data". It defaults to "data". We accept `.png` and `.jpg` image formats. We've added a few samples from [Pexels](https://www.pexels.com/) to the folder already! 
    - `-r` or `--results_dir` specifies the "Directory for Results". It defaults to "results". We write `detection_results.json` to this directory. It specifies classification scores and ultimate class prediction for each input image.
    - `-f` or `--config_file_path` specifies the "File Path for Classifier Configuration". It defaults to "configs/classifier.json".
    - `-c` or `--classes` specifies the "List of Classes to Predict". If this is defined, it will replace the `config_file_path` argument. We expect each class to be of the form `-c {CLASS_NAME}`. 
        - Repeat as necessary (e.g. `python scripts/detection_on_collection.py -c dog -c parrot -c cat -c bear`)
    - `-b` or `--bounding_box_drawing` is a "Flag to draw bounding boxes on images". If used, it will save annotated images to the `results_dir` folder. 

### Failure Modes
DirectAI's models work well for objects and categories that can be *succintly described in natural language*. If you notice a failure mode that isn't resolved by adding descriptions to `examples_to_include` and/or `examples_to_exclude`, please create an Issue or reach out directly! 

### Contact Us
- Email: `ben@directai.io`
- Synchronous Meeting: [Calendly](https://calendly.com/directai/demo)
- Check out our [website](https://directai.io)!
