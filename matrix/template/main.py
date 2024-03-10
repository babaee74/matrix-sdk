from utils.pipeline import Pipeline, load_model
import argparse
from matrix.utils.loaders import auto_file_loader
from settings import configs, INPUT_TYPES, preprocess_params, forward_params, postprocess_params
import os

def parse_cmd() -> dict:
    parser = argparse.ArgumentParser(
                        prog='Matrix Pipeline Runner',
                        description='This Script runs the whole model pipeline, it is the interface between our engine and your code')
    parser.add_argument('--input_dir', default="data", help="The directory that contains input files (text, image, pdf, other files)")
    parser.add_argument('--output_dir', default="results", help="The directory that the results should be saved in any form (text, image, pdf, ...)")
    parser.add_argument('--device', default="cpu", help="the target device, cpu or cuda or an int")
    parser.add_argument('--framework', default="pt", help="`pt` for pytorch, `tf` for tensorflow or `custom` for custom frameworks ")

    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)

    return vars(args)


if __name__=="__main__":

    model = load_model(config=configs)
    args = parse_cmd()
    device = args.pop("device")
    framework = args.pop("framework")
    kwargs = {**args, **configs}
    
    # this will automatically load inputs for you 
    # if you have any generic input type, the path to the file will be given
    inputs = auto_file_loader(args["input_dir"], INPUT_TYPES)

    pipeline = Pipeline(model, device, framework, **kwargs)
    outputs = pipeline.run(inputs, preprocess_params, forward_params, postprocess_params)
