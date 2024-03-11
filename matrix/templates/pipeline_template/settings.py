from omegaconf import OmegaConf
from matrix.utils.logging import logging
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("MATRIX_TOKEN")
# Write a title for your repo, this title will be shown to users on the website
# Using Persian preferred
TITLE = "عنوانی وارد نشده است"
# This is the tag that will be used by users to run your model API.
# It should be a unique name for your repo
DOCKER_TAG = "name:latest"
DEBUG = True # True if you want to debug it on the local machine

# Log verbosity
VERBOSE = False

# pt(pytorch), tf(tensorflow), oth(others), the Docker file should be reconfigured if you change it
FRAMEWORK = "pt"


# NOTE: This command will be append to python main.py
# example result-> python main.py --H 1024 --W 512
command = " --H {h} --W {w}" 


# OPTIONS: ["text", "image", "video", "audio", "json", "pdf", "generic"]
INPUT_TYPES = ["text", ]


# config file for the project
# NOTE: configs should be constant like, height, width, hidden units size, ...
config_file = "configs/stable-diffusion/v1-inference.yaml"

try:
    configs = OmegaConf.load(config_file)
except Exception as e:
    configs = {}
    logging.error(f"{config_file} does not exists")



#----------------------------------------------------------------------#
#------------------- Model constant params ----------------------------#
#----------------------------------------------------------------------#
# NOTE: Write your custom params here or in conf.yaml

seed = 42
ckpt = "weights/model.ckpt" # this is a sample

# pipeline params
# any parameter you think is necessary, these will be passed to pipeline.run()
preprocess_params = {}
forward_params = {}
postprocess_params = {}

