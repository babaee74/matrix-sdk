import argparse
import os

def parse_cmd() -> dict:
    parser = argparse.ArgumentParser(
                        prog='Matrix Project Admin',
                        description='This script is Matrix Admin and it is used to do different task related for matrix including creating a new project',
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
    pass