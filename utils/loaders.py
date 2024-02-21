import json
import glob
import mimetypes
import os



SUPPORTED_TYPES = ["text", "image", "video", "audio", "json", "pdf"]

def json_loader(path):
    """
        load a json file from the given path

        path: str, path to the file
    """
    with open(path, "r") as f:
        txt = f.read()
    return json.loads(txt)

def text_loader(path, split_lines=False):
    """
        load lines of a text file without \n at the end of the lines
        split_lines: if True, splits the lines for the text files else it will return each file as a full sentence

        Return:
            list of strings
    """
    with open(path, "r") as f:
        content = f.read()
        if split_lines:
            content = content.splitlines()
        else:
            content = [content.replace("\n", " ")]
    return content


def image_loader(path, pil=False):
    """
     Load an image from a file. This is a wrapper around PIL or cv2
     
     Args:
     	 path: Path to the image file
     	 pil: If True the image is loaded in PIL
     
     Returns: 
     	 A PIL Image object or cv2 numpy array
    """
    if pil:
        from PIL import Image
        return Image.open(path).convert("RGB")
    else:
        import cv2
        img = cv2.imread(path)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    

def video_loader(path, iterator=False):
    """
     Load video from path. If iterator is True yield each frame instead of the capture object
     
     Args:
     	 path: path to video file to load
     	 iterator: if True yield frame by frame
     
     Returns: 
     	 tuple of ret and frame (ret, frame) or just capture object
    """
    import cv2
    cap = cv2.VideoCapture(path) 
    if not iterator:
        return cap 
    else:
        frame_count = 0
        while 1:
            ret, frame = cap.read()
            if not ret:
                print(f"yield {frame_count} frame(s)")
                break
            yield ret, frame


def audio_loader(path, sr=22050, mono=False):
    """
     Load audio from a file. This is a convenience function for librosa
     
     Args:
     	 path: Path to audio file. It can be a file or URL.
     	 sr: Sample rate of audio file. Default is 22050 Hz.
     	 mono: If True the audio is mono.
     
     Returns: 
     	 Tuple of audio and
    """
    import librosa

    audio, sr = librosa.load(path, sr=sr, mono=mono)
    return (audio, sr)


def auto_file_loader(path, types, pil=False):
    """
        path: directory to load files from
        types: types of files we want to load, options: ["text", "image", "video", "audio", "json", "pdf", "generic"]
        pil: if True -> the loader will load the images in PIL format
        split_lines: if True, splits the lines for the text files else it will return each file as a full sentence
        NOTE: if the file type is generic or pdf, the path to the file will be returned, since you need to load them in your special format

        Return:
            a dictionary of shape {"type":list(), ...}
            the list will contain object of proper type
            image -> list of cv2 numpy arrays
            text -> list of strings
            video -> list of cv2 capture objects
            audio -> list of tuples -> (np array, sampling rate)
            json -> list of dictionaries
    """

    data = {}

    files = glob.glob(os.path.join(path, "*"))
    for file in files:
        gtype = mimetypes.guess_type(file)[0]
        group_, type_ = gtype.split("/")
        if group_!="application":
            type_ = group_
        
        if type_=="text" and "text" in types:
            if type_ not in data.keys():
                data[type_] = []
            content = text_loader(file, split_lines=False)
            data[type_] += content
        elif type_=="image" and "image" in types:
            if type_ not in data.keys():
                data[type_] = []
            img = image_loader(file, pil=pil)
            data[type_].append(img)
        elif type_=="video" and "video" in types:
            if type_ not in data.keys():
                data[type_] = []
            cap = video_loader(file, iterator=False)
            data[type_].append(cap)
        elif type_=="audio" and "audio" in types:
            if type_ not in data.keys():
                data[type_] = []
            audio = audio_loader(file, sr=22050, mono=False)
            data[type_].append(audio)
        elif type_=="json" and "json" in types:
            if type_ not in data.keys():
                data[type_] = []
            obj = json_loader(file)
            data[type_].append(obj)
        elif type_=="pdf" and "pdf" in types:
            if type_ not in data.keys():
                data[type_] = []
            data[type_].append(file)
        else:
            if type_ not in SUPPORTED_TYPES and "generic" in types:
                if type_ not in data.keys():
                    data[type_] = []
                data[type_].append(file)
    return data


