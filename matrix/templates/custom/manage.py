import argparse
import os
from matrix.manager.test import test_main
from matrix.manager.build import build_local, build_request
from matrix.manager.commit import upload_repo, delete_repo
import settings

def parse_cmd() -> dict:
    parser = argparse.ArgumentParser(
                        prog='Matrix Project Manager',
                        description='This script is an interface between matrix-admin and your project. and it works as manager of your project.')
    
    parser.add_argument('--test_gpu', action='store_true', help="if given, the project will be tested on GPU")
    parser.add_argument('--test_cpu', action='store_true', help="if given, the project will be tested on CPU")
    parser.add_argument('--commit', action='store_true', help="if given, the project will be uploaded to matrix repository")
    parser.add_argument('--build_local', action='store_true', help="if given, the project will be built on your local machine")
    parser.add_argument('--build', action='store_true', help="if given, the project will be built and converted to an API")
    parser.add_argument('--delete', action='store_true', help="if given, The Repository and its API will be deleted from the server")
    # parser.add_argument('--install', action='store_true', help="if given, The REQUIREMENTS will be installed")

    args = parser.parse_args()
    return vars(args)

if __name__=="__main__":
    cmds = parse_cmd()
    cwd = os.path.dirname(os.path.abspath(__file__))
    if cmds["test_gpu"]:
        test_main(
            cwd=cwd,
            image=settings.DOCKER_TAG,
            device=0,
            framework=settings.FRAMEWORK,
            types_=settings.INPUT_TYPES
        )
    elif cmds["test_cpu"]:
        test_main(
            cwd=cwd,
            image=settings.DOCKER_TAG,
            device="cpu",
            framework=settings.FRAMEWORK,
            types_=settings.INPUT_TYPES
        )
    elif cmds["commit"]:
        repo_info = {
            "repo_name":settings.DOCKER_TAG,
            "framework":settings.FRAMEWORK,
            "title":settings.TITLE,
            "input_type":str(settings.INPUT_TYPES)
        }
        upload_repo(cwd=cwd, token=settings.TOKEN, settings=repo_info)
    elif cmds["delete"]:
        delete_repo(settings.DOCKER_TAG, token=settings.TOKEN)
    elif cmds["build_local"]:
        build_local(docker_path=cwd, tag=settings.DOCKER_TAG)
    elif cmds["build"]:
        build_request(settings.DOCKER_TAG, token=settings.TOKEN)
    else:
        print("No valid argument given!")
