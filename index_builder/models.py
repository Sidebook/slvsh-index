from pydantic import BaseModel
from typing import Optional
import os
import json
import cv2

RECOGNIZED_TEXT_FILE = 'texts.v1.json'


class RecognizedText(BaseModel):
    text: str
    timestamp: float


class SLVSHMatch(BaseModel):
    path: str
    video_id: str
    title: str
    url: str
    playlist: str
    upload_date: str
    texts: Optional[list[RecognizedText]] = None

    @staticmethod
    def load(dir_path: str) -> 'SLVSHMatch':
        with open(os.path.join(dir_path, 'video.info.json'), 'r') as f:
            info = json.load(f)

        texts = None
        if os.path.exists(os.path.join(dir_path, RECOGNIZED_TEXT_FILE)):
            with open(os.path.join(dir_path, RECOGNIZED_TEXT_FILE), 'r') as f:
                texts = [RecognizedText(**text) for text in json.load(f)]

        return SLVSHMatch(
            path=dir_path,
            video_id=info['id'],
            title=info['title'],
            playlist=info['playlist'],
            url=f"https://www.youtube.com/watch?v={info['id']}",
            upload_date=info['upload_date'],
            texts=texts
        )

    def write(self) -> None:
        if self.texts:
            with open(os.path.join(self.path, RECOGNIZED_TEXT_FILE), 'w') as f:
                json.dump([text.model_dump()
                          for text in self.texts], f, indent=2)

    def get_video_path(self) -> str:
        return os.path.join(self.path, 'video.mp4')

    def get_video(self) -> cv2.VideoCapture:
        return cv2.VideoCapture(self.get_video_path())

    def is_valid(self) -> bool:
        if 'Teaser' in self.title:
            return False

        if self.playlist == 'SLVSH - Shorts':
            return False

        vs_strings = [' v.s.', ' vs. ', ' vs ', ' VS. ']
        return any(vs_string in self.title for vs_string in vs_strings)


class Trick(BaseModel):
    components: list[str]
    start: float
    end: float
    source: SLVSHMatch
