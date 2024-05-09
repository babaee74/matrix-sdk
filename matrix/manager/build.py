from subprocess import Popen, PIPE
import os
from .server import *
import requests




def build_local(docker_path, tag="test:latest"):
    command = f"sudo docker build {docker_path}  --tag {tag}"
    print("running command->", command)
    p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True, bufsize=1000)
    for line in p.stdout:
        print(line)
    out, err = p.communicate()
    # err = err.decode("utf-8")
    if err!="":
        raise RuntimeError( "Test Error->\n {err}")

def build_request(repo_name, token):

    url_done = f"{SERVER_URI}{REPO_BUILD_URI}"
    resp = requests.post(
        url = url_done,
        headers={
            "Authorization":f"Bearer {token}"
        },
        data={
            "repo_name":repo_name
            }
        )

    if resp.status_code==200:
        resp_json = resp.json()
        print(resp_json)
    else:
        raise RuntimeError(f"Build failed with error {resp.status_code}, Please report this problem")