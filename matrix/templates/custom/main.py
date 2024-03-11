from utils.pipeline import Pipeline, load_model
import argparse
from matrix.utils.loaders import auto_file_loader
from matrix.utils.errors import write_error
from settings import configs, INPUT_TYPES, preprocess_params, forward_params, postprocess_params, DEBUG
import os

def parse_cmd() -> dict:
    parser = argparse.ArgumentParser(
                        prog='Matrix Pipeline Runner',
                        description='This script modifies settings.py IPs before using setup.sh',
                        epilog='-i, --ip for allowed hosts')
    parser.add_argument('--input_dir', default="data", help="The directory that contains input files (text, image, pdf, other files)")
    parser.add_argument('--output_dir', default="results", help="The directory that the results should be saved in any form (text, image, pdf, ...)")
    parser.add_argument('--device', default="cpu", help="the target device, cpu or cuda or an int")
    parser.add_argument('--framework', default="pt", help="`pt` for pytorch, `tf` for tensorflow or `custom` for custom frameworks ")

    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)

    return vars(args)


if __name__=="__main__":

    # Please do not remove the try-except clause
    # the error will be checked automatically and send to you if any error happened
    try:
        model = load_model(config=configs)
        args = parse_cmd()
        device = args.pop("device")
        framework = args.pop("framework")
        kwargs = {**args, **configs}
        
        ########################## TODO ####################################################
        """
        This a custom project, you can change this, but make sure you use the input arguments:
        input_dir, output_dir, device, and framework
        these are the argument that will be passed to your project by the API
        NOTE: DO NOT USE CUSTOM VALUE FOR ANY OF THE ABOVE ARGUMENTS
        """

        # This line will automatically load the inputs of type INPUT_TYPES from the given input_dir commandline argument
        # if a file is generic like csv, excel, .whatever, it will return the path to the file
        inputs = auto_file_loader(args["input_dir"], INPUT_TYPES)
        
        # RUN your model here and make sure that you save the results: text, image, video, anything, to the given output_dir

        ######################## END TODO #####################################################
    except Exception as e:

        """
        Please do not change this
        This will catch the errors and send it via email later to you
        """
        cwd = os.path.dirname(os.path.abspath(__file__))
        write_error(cwd=cwd, err=str(e))
        if DEBUG:
            raise RuntimeError("Error happened->", e)


