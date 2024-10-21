import cv2
from pydantic import BaseModel
import os
import json

example_file_path = os.path.join(
    os.path.dirname(__file__), "assets", "examples_with_case_number.json")

class ExampleWithCaseNumber(BaseModel):
    image_path: str
    expected: str
    case_number: int

    def get_image(self) -> cv2.typing.MatLike:
        return cv2.imread(self.image_path)

    def get_case_number(self) -> int:
        return self.case_number


def load_examples_with_case_number() -> list[ExampleWithCaseNumber]:
    with open(example_file_path) as f:
        raw_examples = json.load(f)
    return [ExampleWithCaseNumber(**example) for example in raw_examples]
