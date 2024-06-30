import requests
from .server import *
import os
import json
from urllib.parse import urlparse, parse_qs
import mimetypes



def get_repo_list(pprint=False):
    """
    check status of your request
    task_id: id of your request
    """
    url = f"{SERVER_URI}{REPO_LIST_URI}"
    
    resp = requests.get(url)
    
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to fetch teh status, ERR_CODE: {resp.status_code}, \nDetails: {resp.json()}")
    
    if pprint:
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(resp.json())

    return resp.json()
    

class Client:
    """
    Class for client api connection
    """
    def __init__(self, api_key, repository_name) -> None:
        
        self.api_key = api_key
        self.repository_name = repository_name

    def upload_files(self, files_path):
        """
        files_path: path to files that you wish to be uploaded, any type of file can be uploaded
        """
        url = f"{SERVER_URI}{UPLOAD_FILES_URI}"

        files = []
        for path in files_path:
            if not os.path.exists(path):
                raise RuntimeError(f"File {path} does not exists")
            files.append(("files", open(path, "rb")))
            
        resp = requests.post(
            url,
            headers={
                        "Authorization":f"Bearer {self.api_key}"
                    }, 
            files=files)
        
        if resp.status_code != 201:
            raise RuntimeError(f"Failed to upload the files, ERR_CODE: {resp.status_code}")
        
        return resp.json()["file_indices"]

    def call(self, data):
        """
        calls the api for your data
        data:
            {
                "repo_name": str, author_username/repo_name,
                inputs: dict, {"text":text, "file_ids":[file_id1, file_id2, ....]}
            }
            NOTE: repo_name is the name of the api repository you wish to be called
        """
        url = f"{SERVER_URI}{MODEL_REQUEST_URI}"
        resp = requests.post(
            url, 
            json=data,
            headers={
                        "Authorization":f"Bearer {self.api_key}"
                    })
        
        if resp.status_code!=200:
            raise RuntimeError(f"Request faild, ERR_CODE : {resp.status_code}, \nDetails: {resp.json()}")
        
        request_id = resp.json()["task_id"]
        print(f"Request is Running with request_id={request_id}")
        return resp.json()

    def request_status(self, task_id):
        """
        check status of your request
        task_id: id of your request
        """
        url = f"{SERVER_URI}{REQUEST_RESULT_URI}"
        
        resp = requests.post(
            url, 
            json={"task_id":task_id},
            headers={
                        "Authorization":f"Bearer {self.api_key}"
                    })
        
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch teh status, ERR_CODE: {resp.status_code}, \nDetails: {resp.content}")
        
        return resp.json()
    
    def download_file(self, file_info):
        """
        Download files from file url returned as result of your request (in case of SUCCESS)
        file_info= {
            'type': 'image/png', 
            'url': 'https://api.matrixai.name/repo/download/?task_id=2fdc1bd8-1de2-471b-a193-7700b30f731a&output_id=92bf6594-547c-3e6a-a3a2-57156bd20dcf'
        }
        """
        
        file_url = file_info["url"]
        resp = requests.get(
            file_url, 
            headers={
                        "Authorization":f"Bearer {self.api_key}"
                    })
        
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to download the file, ERR_CODE: {resp.status_code}")
        
        parsed_url = urlparse(file_url)
        query_params = parse_qs(parsed_url.query)
        file_id = query_params.get("output_id", None)
        if file_id is None:
            file_id = query_params.get("file_id", None)
        
        if file_id is None:
            raise RuntimeError("Wrong URL Pattern")
        
        file_id = file_id[0]

        file_type = file_info['type']
        file_extension = mimetypes.guess_extension(file_type)

        if not file_extension:
            file_extension = '.bin'
        
        file_name = f"{file_id}{file_extension}"
        with open(file_name, 'wb') as f:
            f.write(resp.content)
        
        print(f"Saved file to {file_name}")
        

