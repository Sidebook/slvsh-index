from abc import abstractmethod
from typing import Callable

import cv2


class Recognizer:
    @abstractmethod
    def infer(self, image: cv2.typing.MatLike) -> str:
        pass

    @staticmethod
    def from_func(func: Callable[[str], str]) -> 'Recognizer':
        return FunctionRecognizer(func)


class FunctionRecognizer(Recognizer):
    def __init__(self, func: Callable[[str], str]):
        self.func = func

    def infer(self, image: cv2.typing.MatLike) -> str:
        return self.func(image)
