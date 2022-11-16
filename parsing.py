import typing
from typing import Callable
from enum import Enum
T = typing.TypeVar('T')
class Parser:
    def __init__(self,text):
        self.offset:int = 0
        self.text:str = text
    def __call__(self,cont:Callable[[str,int,int],T])->T:
            for i in range(len(self.text)):
                res = cont(self.text,self.offset,self.offset+i)
                if res != None:
                    self.offset = self.offset + i + 1 
                    return res
        