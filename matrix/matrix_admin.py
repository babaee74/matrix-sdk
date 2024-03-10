# -*- coding: utf-8 -*-

import argparse
import os
from matrix.manager.admin import setup_project

def parse_cmd() -> dict:
    parser = argparse.ArgumentParser(
                        prog='Matrix Project Admin',
                        description='This script is Matrix Admin and it is used to do different task related for matrix including creating a new project')
    parser.add_argument('--startproject', action='store_true', help="If given, it will setup a project")
    args = parser.parse_args()
    
    return vars(args)

def main():
    cmds = parse_cmd()

    if cmds["startproject"]:
        setup_project(os.getcwd())
