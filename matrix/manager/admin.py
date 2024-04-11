
import pkg_resources
import shutil
import os
from zipfile import ZipFile

FRAMEWORKS = ["pt", "tf", "oth"]

def update_dockerfile(cwd, framework):
    matrix_dir = pkg_resources.resource_filename("matrix", '')
    if framework not in FRAMEWORKS:
        raise RuntimeError(f"Framework must be one of these: {FRAMEWORKS}")
    
    if framework=="pt":
        shutil.copy2(src=os.path.join(matrix_dir, "templates", "Dockerfile-pt"), dst=os.path.join(cwd, "Dockerfile"))
    elif framework=="tf":
        shutil.copy2(src=os.path.join(matrix_dir, "templates", "Dockerfile-tf"), dst=os.path.join(cwd, "Dockerfile"))
    else:
        shutil.copy2(src=os.path.join(matrix_dir, "templates", "Dockerfile-oth"), dst=os.path.join(cwd, "Dockerfile"))


def setup_project(cwd):
    matrix_dir = pkg_resources.resource_filename("matrix", '')

    project_name = input("Enter a name for your project:\n")

    action = input("You want to setup a Pipeline-based project(Enter yes/y) or a custom project(Enter No/n)? ")

    use_pipeline = False
    if action.lower() in ["yes", "y"]:
        use_pipeline = True

    framework = input("What framework are you going to use? enter (`pt` for pytorch), (`tf` for tensorflow), (`oth` for others) ")
    if framework not in FRAMEWORKS:
        raise RuntimeError(f"Enter one of these pleae: {FRAMEWORKS}")
    
    project_dir = os.path.join(cwd, project_name)
    os.makedirs(project_dir, exist_ok=True)

    zipfile_path = os.path.join(matrix_dir, "templates", "custom.zip")
    if use_pipeline:
        zipfile_path = os.path.join(matrix_dir, "templates", "pipeline_template.zip")
    
    with ZipFile(zipfile_path, 'r') as zip: 
        zip.extractall(path=project_dir) 
    if framework=="pt":
        shutil.copy2(src=os.path.join(matrix_dir, "templates", "Dockerfile-pt"), dst=os.path.join(project_dir, "Dockerfile"))
    elif framework=="tf":
        shutil.copy2(src=os.path.join(matrix_dir, "templates", "Dockerfile-tf"), dst=os.path.join(project_dir, "Dockerfile"))
    else:
        shutil.copy2(src=os.path.join(matrix_dir, "templates", "Dockerfile-oth"), dst=os.path.join(project_dir, "Dockerfile"))


    print("******************************************************************")
    print("***********Hooray! Enjoy!, If any bug: better call MrEsi**********")
    print("******************************************************************")