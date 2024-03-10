import os


class PipelineException(Exception):
    """
    Raised by a [`Pipeline`] when handling __call__.

    Args:
        task (`str`): The task of the pipeline.
        model (`str`): The model used by the pipeline.
        reason (`str`): The error message to display.
    """

    def __init__(self, task: str, model: str, reason: str):
        super().__init__(reason)

        self.task = task
        self.model = model

def write_error(cwd, err):
    path = os.path.join(cwd, "error")
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "error.txt"), "w") as f:
        f.write(err)
    return True

