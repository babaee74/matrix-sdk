from omegaconf import OmegaConf
from matrix.utils.logging import logging

REQUIREMENTS = "requirements.py"

VERBOSE = False

# pt(pytorch), tf(tensorflow), ot(others)
FRAMEWORK = "pt"



# NOTE: This command will be append to python main.py
# example result-> python main.py --H 1024 --W 512
command = " --H {h} --W {w}" 


# OPTIONS: ["text", "image", "video", "audio", "json", "pdf", "generic"]
INPUT_TYPES = ["text", ]


# config file for the project
config_file = "utils/conf.yaml"

try:
    configs = OmegaConf.load(config_file)
except Exception as e:
    configs = {}
    logging.error(f"{config_file} does not exists")




#----------------------------------------------------------------------#
#------------------- Model constant params ----------------------------#
#----------------------------------------------------------------------#
# NOTE: Write your custom params here or in conf.yaml
# model params to be used inside pipeline.py
# another way of passing these params is through the config.yaml file
seed = 42
batch_size = 4



# pipeline params
# any parameter you think is necessary, these will be passed to pipeline.run()
# another way of passing these params is through the config.yaml file
preprocess_params = {}
forward_params = {}
postprocess_params = {}
