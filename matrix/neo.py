from contextlib import contextmanager
from .utils.auxiliary import is_tf_available, is_torch_available, is_sklearn_available
from typing import Any, Dict, List, Optional, Tuple, Union
from abc import ABC, abstractmethod
from packaging import version
from .utils.logging import logging


GenericTensor = Union[List["GenericTensor"], "torch.Tensor", "tf.Tensor"]


if is_tf_available():
    import tensorflow as tf

if is_torch_available():
    import torch

class AbstractModel(ABC):
    """
        NOTE: Override init() in order to use __init__ functionality method if needed

        Parameters:
            params: dict, containing any param to initialize the model, params like device, ...
                {"param1":value1, "param2":value2, ...}

            info: dict, {"text":text, "files":[path1, path2, ....], "ndarray":[array1, array2,...]}
                this argument specifies inputs for the process, including text, files(images, pdf, ...), numpy ndarray ...
            
            *args: extra arguments with no name
                a tuple with the exact given order
                if you are inheriting this class, the *args will be available as self.args
                Example Usage:
                    abstract_model = AbstractModel(info, embeddings, sanitizer, ...)
            
            **kwargs: Keyword arguments
                any argument with a name, you can iterate over this like
                if you are inheriting this class, the kwargs will be available as self.kwargs
                Example Usage:
                    abstract_model = AbstractModel(info, *args, embeddings=embeddings, sanitizer=sanitizer, ...)
    """

    def __init__(self, loaded_model, device, framework, **kwargs) -> None:
        if not (is_torch_available() or is_tf_available() or is_sklearn_available()):
            raise logging.warning("At least needs torch, tensorflow or sklearn installed")
        
        if framework=="pt":
            if not is_torch_available():
                raise RuntimeError("Framework set to torch but torch is not available")
        elif framework=="tf":
            if not is_tf_available():
                raise RuntimeError("Framework set to tensorflow but tensorflow is not available")
        
        self.model = loaded_model
        self.framework = framework
        self.kwargs = kwargs # a dictionary of given keyword arguments, {embeddings:embeddings, sanitizer:sanitizer, ...}
        
        # initiating the device
        try:
            d = int(device)
            device = d
        except ValueError:
            pass

        if isinstance(device, str) and (device is None or device=="" or "cpu" in device.lower()):
            device = -1
        

        if self.framework == "pt":
            if isinstance(device, torch.device):
                self.device = device
            elif isinstance(device, str):
                self.device = torch.device(device)
            elif device < 0:
                self.device = torch.device("cpu")
            else:
                self.device = torch.device(f"cuda:{device}")
                
            if self.device.type=="cuda":
                if not torch.cuda.is_available():
                    raise RuntimeError("Torch Device type set to cuda but cuda is not available")
                self.model.to(device)
            self.model.eval()
            
        elif self.framework == "tf":
            self.device = device if device>=0 else -1
            
    @contextmanager
    def device_placement(self):
        """
        Context Manager allowing tensor allocation on the user-specified device in framework agnostic way.

        Returns:
            Context manager

        Examples:

        ```python
        # Explicitly ask for tensor allocation on CUDA device :0
        pipe = pipeline(..., device=0)
        with pipe.device_placement():
            # Every framework specific tensor allocation will be done on the request device
            output = pipe(...)
        ```"""
        if self.framework == "tf":
            with tf.device("/CPU:0" if self.device == -1 else f"/device:GPU:{self.device}"):
                yield
        else:
            if self.device.type == "cuda":
                torch.cuda.set_device(self.device)

            yield
    
    @abstractmethod
    def preprocess(self, input_: Any, **preprocess_parameters: Dict):
        """
            You need to override this method in order to do any preprocess

            post process usually is applied to the information given through given 'inputs'
            but other possible arguments could be pass using *args or **kwargs

            the order of execution when in teh pipeline is:
                preprocess() -> forward() -> post_process()

            NOTE: **preprocess_parameters give you the flexibility to specify any arguments
                    these preprocess_parameters are the same as the one passed to the run function
            Return:
                the return values is the user choice, the return values usually is used as forward input
                if model has multiple inputs, use dict to return them
        """
        raise NotImplementedError("preprocess not implemented")
    
    @abstractmethod
    def forward(self, model_inputs: Dict[str, Any], **forward_parameters: Dict):
        """
            You need to override this method in order to call your main model, or main process

            the main model input is usually the output of the preprocess()
            NOTE: **forward_parameters is a dict to pass extra keyword arguments to the forward function
                    these forward_parameters are the same as the one passed to the run function

            the order of execution when in teh pipeline is:
                preprocess() -> forward() -> post_process()
            
            NOTE: **forward_parameters give you the flexibility to specify any arguments
        """
        raise NotImplementedError("forward not implemented")

    def get_inference_context(self):
        inference_context = (
            torch.inference_mode
            if version.parse(version.parse(torch.__version__).base_version) >= version.parse("1.9.0")
            else torch.no_grad
        )
        return inference_context

    def _ensure_tensor_on_device(self, inputs, device):

        if isinstance(inputs, dict):
            return {name: self._ensure_tensor_on_device(tensor, device) for name, tensor in inputs.items()}
        elif isinstance(inputs, list):
            return [self._ensure_tensor_on_device(item, device) for item in inputs]
        elif isinstance(inputs, tuple):
            return tuple([self._ensure_tensor_on_device(item, device) for item in inputs])
        elif isinstance(inputs, torch.Tensor):
            if device == torch.device("cpu") and inputs.dtype in {torch.float16, torch.bfloat16}:
                inputs = inputs.float()
            return inputs.to(device)
        else:
            return inputs

    def _forward(self, model_inputs, **forward_params):
        """
            this will run the forward function that you implemented and also handles the device 
            if handle_device is set to True when calling the 'run' function
            if handle_device is False, you need to handle inference mode inside forward() function
        """
        if self.framework in ["pt", "tf"]:
            with self.device_placement():
                if self.framework == "tf":
                    model_inputs["training"] = False
                    model_outputs = self.forward(model_inputs, **forward_params)
                else:
                    inference_context = self.get_inference_context()
                    with inference_context():
                        model_inputs = self._ensure_tensor_on_device(model_inputs, device=self.device)
                        model_outputs = self.forward(model_inputs, **forward_params)
                        model_outputs = self._ensure_tensor_on_device(model_outputs, device=torch.device("cpu"))

            return model_outputs
        else:
            return self.forward(model_inputs, **forward_params)
        
    @abstractmethod
    def post_process(self, outputs_, *f_args, **f_kwargs):
        """
            You need to override this method in order to post process the output of your models.
            
            outputs_: the inputs are the forward() output
            
            the order of execution when in teh pipeline is:
                preprocess() -> forward() -> post_process()

            NOTE:  the "self.output_dir" is always given, in order to save the results in the specified directory
            
            NOTE: that *f_args, **kw_args give you the flexibility to specify any arguments

            NOTE: You need to save the output of the preprocess in the given output_dir as files
                For example, when the output is a text:
                    # name could be anything, the extension should be 'text' or 'txt'
                    file_name = "name.txt" # or "name.text"
                    with open(os.path.join(output_dir, file_name), 'w'):
                        f.write(text)
                
                When the output is an image:
                    # name could be anything, but the extension should be a valid image extension
                    file_name = "name.jpg" # or "name.png"
                    cv2.imwrite(file_name, image)
        """
        raise NotImplementedError("post_process not implemented")

    def run(self, inputs, preprocess_params, forward_params, postprocess_params):
        """
            Run the model and save the output. This is the entry point for the model to be executed.
            
            Args:
                inputs: Dictionary of the Input data to be passed to the model.
                preprocess_params: Dictionary of preprocessing parameters. These are used to preprocess the model's inputs before it is called.
                forward_params: Dictionary of forward processing parameters. These are used to forward the model's inputs.
                postprocess_params: Dictionary of postprocessing parameters. These are used to save the model's outputs after it is called.
            
            Returns: 
                A dictionary of outputs generated by the preprocessed model's output
        """
        if inputs is not None and len(inputs)==0:
            raise RuntimeError("the `inputs` dict is empty")
        model_inputs = self.preprocess(inputs, **preprocess_params)
        model_outputs = self.forward(model_inputs, **forward_params)
        model_outputs = self.post_process(model_outputs, **postprocess_params)
        return model_outputs




