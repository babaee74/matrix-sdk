from matrix.neo import AbstractModel
from typing import Any, Dict



def load_model(configs):
    """
        configs:
            the model configs stored inside the conf.yaml file

        Return model:
            This Function needs to return a torch, tensorflow or sklearn model.
            the returned model will be fed into the pipeline to be run by the pipeline
    """
    model = None

    #========================== TODO =====================================
        
    raise NotImplementedError("you need to complete the load_model function")
    
    return model
    #======================== END TODO ===================================  
    


class Pipeline(AbstractModel):
    def __init__(self, loaded_model, device, framework, **kwargs) -> None:
        """
            For better code clearance, override init() method instead of dangling the code inside this __init__ function
        """
        
        super().__init__(loaded_model, device, framework, **kwargs)
        self.init(**kwargs)


    def init(self, **kwargs):
        """
            NOTE: This model is called inside __init__ in order to perform your initialization on instantiation

            You need to override this method in order to initialize any objects needed, eg. models, embeddings, ...

            You usually use the params given on instantiation

            you can access model, device, framework with self.model, self.device, self.framework respectively
            also, args and kwargs are accessible through the input arguments and also through self.args and self.kwargs
        """
        
        #========================== TODO =====================================
        
        raise NotImplementedError("init not implemented")

        #======================== END TODO ===================================

    def preprocess(self, input_: Any, **preprocess_parameters: Dict):
        """
            You need to override this method in order to do any preprocess

            post process usually is applied to the information given through given 'inputs'
            but other possible arguments could be pass using *args or **kwargs

            the order of execution when in the pipeline is:
                preprocess() -> forward() -> post_process()

            NOTE: **preprocess_parameters give you the flexibility to specify any arguments
                    these preprocess_parameters are the same as the one passed to the run function
            Return:
                the return values is the user choice, the return values usually is used as forward input
                if model has multiple inputs, use dict to return them
        """


        #========================== TODO =====================================

        raise NotImplementedError("preprocess not implemented")

        #======================== END TODO ===================================
    
    def forward(self, model_inputs: Dict[str, Any], **forward_parameters: Dict):
        """
            You need to override this method in order to call your main model, or main process

            the main model input is usually the output of the preprocess()
            NOTE: **forward_parameters is a dict to pass extra keyword arguments to the forward function
                    these forward_parameters are the same as the one passed to the run function

            the order of execution when in the pipeline is:
                preprocess() -> forward() -> post_process()
            
            NOTE: **forward_parameters give you the flexibility to specify any arguments
        """
        

        #========================== TODO =====================================

        raise NotImplementedError("forward not implemented")

        #======================== END TODO ===================================
    
    def post_process(self, output_dir, *f_args, **f_kwargs):
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
        

        #========================== TODO =====================================

        raise NotImplementedError("post_process not implemented")

        #======================== END TODO ===================================


