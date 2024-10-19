from pydantic import BaseModel


class Example(BaseModel):
    image_path: str
    expected: str
