from matrix.client.request import Client
import time

MATRIX_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ0MzcxMjY0LCJpYXQiOjE3MTI4MzUyNjQsImp0aSI6ImJlNGFkM2Q3ZTBlZTQ2MjY4YjA0NmQ4MmViMmE3N2ZmIiwiZW1haWwiOiJtcmVzaTFAZ21haWwuY28ifQ.TozAR0xfVP2jRuF-KBjbjwG2EEyKXlg64KbU-LY5CY4"
client = Client(MATRIX_TOKEN, "mresi1/text2image")

files = [
    "/home/market/market-place/samples/Screenshot from 2024-01-06 02-41-36.png",
    "/home/market/market-place/samples/-2111889661_-1943223779.pdf"
]
# indices = client.upload_files(files)
# print(indices)

inputs = {
    "repo_name": "mresi1/text2image2",
    "inputs": {"text":"picture of a rabbit eating banana"}
}
# resp = client.call(inputs)
# print(resp)
# time.sleep(10)
resp = client.request_status(task_id="2fdc1bd8-1de2-471b-a193-7700b30f731a")
print(resp)

client.download_file(resp["outputs"]["files"][0])
