from subprocess import Popen, PIPE
import importlib.util as implib
from ..utils.logging import logging
from ..utils.loaders import auto_file_loader
import os

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
                if err!="":
                    raise RuntimeError( "Package could not be installed, ERROR->\n {err}")

def test_main(cwd, image, device, framework, types_):
    input_dir = os.path.join(cwd, "samples")
    inputs = auto_file_loader(input_dir, types_)

    if not inputs:
        raise RuntimeError(f"No samples provided for automatic testing")
    
    if set(types_) != set(list(inputs.keys())):
        raise RuntimeError(f"Wrong inputs has been loaded! check auto_file_loader")
    
    # if install:
    #     read_requirements(path=requirements)
    
    
    output_dir = os.path.join(cwd, "results")
    os.makedirs(output_dir, exist_ok=True)
    
    weights_dir = os.path.join(cwd, "weights")
    if device in [-1, "cpu"]:
        command = f"sudo docker run --mount type=bind,source={input_dir},target=/app/data/ --mount type=bind,source={output_dir},target=/app/results/ --mount type=bind,source={weights_dir},target=/app/weights/ {image} python3 main.py --input_dir /app/data --output_dir /app/results --device {device} --framework {framework}"
    else:
        command = f"sudo docker run --gpus all --mount type=bind,source={input_dir},target=/app/data/ --mount type=bind,source={output_dir},target=/app/results/ --mount type=bind,source={weights_dir},target=/app/weights/ {image} python3 main.py --input_dir /app/data --output_dir /app/results --device {device} --framework {framework}"
    
    print("running command->", command)
    p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    for line in p.stdout:
        print(line)
    out, err = p.communicate()
    print(p.returncode)
    # err = err.decode("utf-8")
    if p.returncode and err!="":
        if not ("warning" in err.lower()):
            raise RuntimeError( f"Test Error->\n {err}")
    
