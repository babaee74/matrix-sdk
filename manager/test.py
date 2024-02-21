from subprocess import Popen, PIPE
import importlib.util as implib
from ..utils.logging import logging
from ..utils.loaders import auto_file_loader
import time


def read_requirements(path="requirements.txt"):

    with open(path, "r") as f:
        requirements = f.read().splitlines()
    
    if not requirements:
        raise RuntimeError("Requirements.txt is empty!")
    
    for r in requirements:
        if "-e " not in r: #and len(r.split("-"))==1:
            rclean = r.split("==")[0]
            rclean = rclean.split(">=")[0]
            rclean = rclean.split("<=")[0]
            _pkg_available = implib.find_spec(rclean) is not None
            if not _pkg_available:
                print(f"{r} is not installed, starting to install...")
                p = Popen(f"pip install {r}", shell=True, stdout=PIPE, stderr=PIPE)
                out, err = p.communicate()
                err = err.decode("utf-8")
                out = out.decode("utf-8")
                print(out)
                print(err)
                # if err!="":
                #     raise RuntimeError(f"Package could not be installed, ERROR->\n {err}")

def test_main(input_dir, output_dir, device, framework, types_, install=False, requirements="requirements.txt"):
    inputs = auto_file_loader(input_dir, types_)

    if not inputs:
        raise RuntimeError(f"inputs is empty")
    
    if types_!=list(inputs.keys()):
        raise RuntimeError(f"Wrong inputs has been loaded! check auto_file_loader")
    
    if install:
        read_requirements(path=requirements)
    
    p = Popen(f"python3 main.py --input_dir {input_dir} --output_dir {output_dir} --device {device} --framework {framework}", shell=True, stdout=PIPE, stderr=PIPE)

    # for line in iter(p.stdout.readline, b''):
    #     print(line.rstrip())
    out, err = p.communicate()
    err = err.decode("utf-8")
    if err!="":
        raise RuntimeError( f"Test Error->\n {err}")
    
