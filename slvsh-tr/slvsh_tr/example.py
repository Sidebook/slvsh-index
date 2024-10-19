import cv2
from pydantic import BaseModel
import os
import json

example_file_path = os.path.join(
    os.path.dirname(__file__), "assets", "examples.json")

class Example(BaseModel):
    image_path: str
    expected: str
    def get_image(self) -> cv2.typing.MatLike:
        return cv2.imread(self.image_path)


def load_examples() -> list[Example]:
    with open(example_file_path) as f:
        raw_examples = json.load(f)
    return [Example(**example) for example in raw_examples]
