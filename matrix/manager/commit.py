from .server import *
import requests
import os
import hashlib
from tqdm import tqdm
import json
from zipfile import ZipFile


def delete_repo(repo_name, token=None):
    """
     Delete a repo from the server. This is a blocking call so you don't have to worry about waiting for the server to respond before deleting the repo
     
     Args:
     	 repo_name: The name of the repo to delete
     	 token: The token to use for the request. If None a RuntimeError will be raised
     
     Returns: 
     	 True if the repo was deleted raise RuntimeError if there were any error
    """
    if token is None:
        raise RuntimeError("You need to provide a token authentication")
    
    url = f"{SERVER_URI}{REPO_DELETE_URI}"
    resp = requests.post(
        url,
        headers={"Authorization":f"Bearer {token}"},
        data={"repo_name": repo_name}
    )

    if resp.status_code==200:
        print(f"Repo {repo_name} deleted from the server!")
        return True
    else:
        raise RuntimeError(f"Repo Deletion encountered an error-> status code: {resp.status_code}, body: {resp.content}")



def chunkify(file_name, size=1024*1024):
    with open(file_name, "rb") as f:
        while content := f.read(size):
            yield content
   


def zipify(directory_path, zip_path):
    EXCLUDE_DIR_NAME = [".matrix_temp", "__pycache__", "output", "results", "data"]
    EXCLUDE_DIR_ABS = [os.path.join(directory_path, name) for name in EXCLUDE_DIR_NAME]
    os.makedirs(zip_path, exist_ok=True
                )
    zip_file_name = os.path.join(zip_path,"repo.zip")
    with ZipFile(zip_file_name, 'w') as zipf:
        for root, dirs, files in os.walk(directory_path):
            exclude = False
            for exc in EXCLUDE_DIR_ABS:
                if exc in root:
                    exclude = True
                    break
            if exclude:
                continue
            
            print(f"Zipping {root}...")
            for file in files: 
                zipf.write(os.path.join(root, file), 
                           os.path.relpath(os.path.join(root, file), directory_path))
    return zip_file_name


def upload_repo(cwd, token=None, settings=None):
    if token is None:
        raise RuntimeError("You need to provide a token authentication")
    
    """
    settings sample:
    {
        "repo_name":"text2image2:latest",
        "price": 0,
        "framework":"pt",
        "title":"تبدیل متن به تصویر",
        "input_type":str(["text",]),
        "output_type":str(["image",]),
    }
    """
    if settings is None:
        raise RuntimeError("You need to provide the repo settings")
    
    
    history_file = os.path.join(cwd, ".matrix_temp", "hist.json")

    content = {}
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as f:
                content = json.loads(f.read())
        except:
            content = {}
    
    upload_id = None
    offset = 0

    zip_exists = False
    file_path = os.path.join(cwd, ".matrix_temp", "repo.zip")
    if os.path.exists(file_path):
        zip_exists = True
    
    use_hist = False
    if content and zip_exists:
            action = input("This directory has already been zipped and sent partially to server \ndo you want to continue(Enter yes/y)? or start over(Enter no/n)?")
            
            if action.lower() in ["yes", "y"]:
                use_hist = True
    
    if use_hist:
        upload_id = content.get("upload_id", None)
        offset = content.get("offset", None)
        if upload_id is None or offset is None:
            upload_id = None
            offset = 0
            use_hist = False

    if not use_hist:
        zipping_dir = os.path.join(cwd, ".matrix_temp")
        file_path = zipify(directory_path=cwd, zip_path=zipping_dir)

    
    url = f"{SERVER_URI}{UPLOAD_REPO_URI}"

    size = 1024*1024 # 1MB
    chunks = chunkify(file_path, size=size)
    
    total = os.path.getsize(file_path)

    chunk_count = total//size+1
    
    md5_hash = hashlib.md5()

    index = 0
    for chunk in tqdm(chunks, total=chunk_count):
        md5_hash.update(chunk)

        if upload_id is None:
            """
            resp={
                "upload_id": "5230ec1f59d1485d9d7974b853802e31",
                "offset": 1024*1024,
                "expires": "2013-07-18T17:56:22.186Z"
            }
            """
            
            resp = requests.post(
                url = url,
                headers={
                    "Content-Range": "bytes {}-{}/{}".format(offset, offset + len(chunk) - 1, total),
                    "Authorization":f"Bearer {token}"
                },
                files={'file': chunk}
            )

            if resp.status_code==200:
                resp_json = resp.json()
                upload_id = resp_json["upload_id"]
                offset = resp_json["offset"]
                with open(history_file, "w") as f:
                    f.write(json.dumps({"upload_id":upload_id, "offset": offset}))
            else:
                raise RuntimeError(f"Upload Failed with {resp.status_code}")
        else:
            if index==offset:
                resp = requests.post(
                    url = url,
                    headers={
                        "Content-Range": "bytes {}-{}/{}".format(offset, offset + len(chunk) - 1, total),
                        "Authorization":f"Bearer {token}"
                    },
                    data={"upload_id": upload_id},
                    files={'file': chunk}
                )
                
                if resp.status_code==200:
                    resp_json = resp.json()
                    offset = resp_json["offset"]
                    with open(history_file, "w") as f:
                        f.write(json.dumps({"upload_id":upload_id, "offset": offset}))
                else:
                    raise RuntimeError(f"Upload Failed with {resp.status_code}")

        index += len(chunk)
        
    
    url_done = f"{SERVER_URI}{UPLOAD_REPO_DONE_URI}"
    resp = requests.post(
        url = url_done,
        headers={
            "Authorization":f"Bearer {token}"
        },
        data={
            'md5': md5_hash.hexdigest(), 
            "upload_id": upload_id, 
            "settings":json.dumps(settings)
            }
        )

    if resp.status_code==200:
        resp_json = resp.json()
        print(resp_json)
    else:
        raise RuntimeError(f"Upload Failed with {resp.status_code}, details:{resp.content}")
    


