import typing
from typing import Callable
from enum import Enum
T = typing.TypeVar('T')
class Parser:
    def __init__(self):
        self.offset:int = 0
        self.state = None
    def __call__(self,str:str,pred:Callable[[str,int,int],bool],cont:Callable[[str,int,int],T])->T:
            for i in range(len(str)):
                if pred(str,self.offset,self.offset+i):
                    ret = cont(str,self.offset,self.offset+i)
                    self.offset = self.offset + i + 1 
                    return ret
        