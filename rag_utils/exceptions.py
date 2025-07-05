

class EmbedMaxConnectionTimeout(Exception):
    def __init__(self,text):
        super().__init__()
        self.text = text
        
        
        
class EmbedMethodException(Exception):
    def __init__(self,exception_message,text):
        super().__init__()
        self.exception_message = exception_message
        self.text = text