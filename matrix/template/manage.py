import argparse
import os
from matrix.manager.test import test_main
import settings

def parse_cmd() -> dict:
    parser = argparse.ArgumentParser(
                        prog='Matrix Project Manager',
                        description='This script is an interface between matrix-admin and your project. and it works as manager of your project.')
    
    parser.add_argument('--test_gpu', action='store_true', help="if given, the project will be tested on GPU")
    parser.add_argument('--test_cpu', action='store_true', help="if given, the project will be tested on CPU")
    parser.add_argument('--commit', action='store_true', help="if given, the project will be uploaded to matrix repository")
    parser.add_argument('--build', action='store_true', help="if given, the project will be built and converted to an API")

    args = parser.parse_args()
    return vars(args)

if __name__=="__main__":
    cmds = parse_cmd()
    input_dir = os.path.join(os.getcwd(), "data")
    output_dir = os.path.join(os.getcwd(), "results")
    if cmds["test_gpu"]:
        test_main(
            input_dir=input_dir,
            output_dir=output_dir,
            device=0,
            framework=settings.FRAMEWORK,
            types_=settings.INPUT_TYPES,
            install=True
        )
    elif cmds["test_cpu"]:
        test_main(
            input_dir=input_dir,
            output_dir=output_dir,
            device="cpu",
            framework=settings.FRAMEWORK,
            types_=settings.INPUT_TYPES,
            install=True
        )
    elif cmds["commit"]:
        pass
    elif cmds["build"]:
        pass
    else:
        print("No valid argument given!")
