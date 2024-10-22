from typing import List
import cv2
import pytesseract
import argparse
import numpy as np
import os
import json

from dataclasses import dataclass, asdict
from abc import abstractmethod
from typing import Callable
import json


VERSION = "0.0.1"

@dataclass
class FrameExtraction:
    timestamp: float
    text: str
    frame_number: int

    def get_all_tokens(self):
        return [token for token in self.text.strip().replace(',', ' ').replace('.', ' ').split() if token]

@dataclass
class VideoExtractions:
    title: str
    video_path: str
    url: str
    extractions: List[FrameExtraction]
    extractor_version: str = '0.0.0'

    def to_json(self):
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        data['extractions'] = [FrameExtraction(**e) for e in data['extractions']]
        return cls(**data)

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

class TesseractPreFindRectangleRecognizer(Recognizer):
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.debug_folder = None

    def set_debug_folder(self, folder: str):
        self.debug_folder = folder

    def whiten_red_and_green(self, image: cv2.typing.MatLike) -> cv2.typing.MatLike:
        # BGRからHSV色空間に変換
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 緑色の範囲を定義（HSV色空間）
        lower_green = np.array([40, 40, 40])
        upper_green = np.array([80, 255, 255])
        
        # 赤色の範囲を定義（HSV色空間）- 明るい赤のみ
        lower_red2 = np.array([170, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        # マスクの作成
        mask_green = cv2.inRange(hsv_image, lower_green, upper_green)
        mask_red2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask_green, mask_red2)
        # 結果画像の作成
        result = image.copy()
        result[mask > 0] = [255, 255, 255]
        
        if self.debug and self.debug_folder:
            result_path = os.path.join(self.debug_folder, "whiten_result.png")
            cv2.imwrite(result_path, result)
            
            masked_image = cv2.bitwise_and(image, image, mask=mask)
            masked_path = os.path.join(self.debug_folder, "masked_image.png")
            cv2.imwrite(masked_path, masked_image)
        
        return result

    def find_text_region(self, image: cv2.typing.MatLike) -> tuple:
        height, width = image.shape[:2]
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY) #真っ白の四角を対象にする
        
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if self.debug and self.debug_folder:
            gray_path = os.path.join(self.debug_folder, "gray_image.png")
            cv2.imwrite(gray_path, gray)
            binary_path = os.path.join(self.debug_folder, "binary_image.png")
            cv2.imwrite(binary_path, binary)
        
        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > width * 0.05 and h > height * 0.9:
                # 右端または左端にアラインされているか確認
                if x < width * 0.05 or x + w > width * 0.95:
                    text_regions.append((x, y, w, h))
        
        if text_regions:
            # 幅が最大のものを選択
            return max(text_regions, key=lambda r: r[2])
        
        return None

    def infer(self, image: cv2.typing.MatLike, image_name: str) -> str:
        height, width = image.shape[:2]
        roi = image[int(height * 0.87):int(height * 0.93), int(width * 0.035):int(width * 0.965)]
        
        original_roi = roi.copy()
        roi = self.whiten_red_and_green(roi)
        
        text_region = self.find_text_region(roi)
        config='--psm 7 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,. /"'

        if text_region is None:
            return ""
        else:
            x, y, w, h = text_region
            target_image = original_roi[y:y+h, x:x+w]

        extracted_text = pytesseract.image_to_string(target_image, config=config).strip()

        if self.debug and self.debug_folder:
            # 抽出されたテキストを含む画像を作成
            text_image = np.zeros_like(roi)
            cv2.putText(text_image, extracted_text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
             
            # target_imageをroiと同じサイズにリサイズ
            target_image_resized = cv2.resize(target_image, (roi.shape[1], roi.shape[0]))
             
            # 元画像に縦に積み重ねる
            stacked_image = cv2.vconcat([
                roi,
                target_image_resized,
                text_image
            ])
            
            # 積み重ねた画像を保存
            stacked_image_path = os.path.join(self.debug_folder, f"{image_name}_debug.png")
            cv2.imwrite(stacked_image_path, stacked_image)

        return extracted_text


def extract_text_from_video(video_path, interval_seconds=5, debug=False) -> list[FrameExtraction]:
    debug_folder = os.path.join(os.path.dirname(video_path), 'debug') if debug else None
    if debug:
        os.makedirs(debug_folder, exist_ok=True)
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError(f"Error: Could not open video file {video_path}")

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)  # Frames per second
    interval = int(fps * interval_seconds)  # Convert seconds to frames

    frame_count = 0
    keep_frames = []
    keep_frame_num = 5
    keep_frame_interval = 10
    extractions = []

    recognizer = TesseractPreFindRectangleRecognizer(debug=debug)
    if debug:
        recognizer.set_debug_folder(debug_folder)

    while True:
        # Read the next frame
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % keep_frame_interval == 0:
            keep_frames.append(frame)

        if len(keep_frames) > keep_frame_num:
            keep_frames = keep_frames[1:]
        
        if len(keep_frames) < keep_frame_num:
            continue

        # Process every nth frame where n is the interval
        if frame_count % interval == 0:

            minutes = int(frame_count / fps // 60)
            seconds = int(frame_count / fps % 60)
            timestamp_str = f"{minutes:02d}:{seconds:02d}"

            # TesseractPreFindRectangleRecognizerを使用してテキストを抽出
            extracted_text = recognizer.infer(frame, timestamp_str).strip()

            extraction = FrameExtraction(
                timestamp=frame_count / fps,
                text=extracted_text,
                frame_number=frame_count
            )

            extractions.append(extraction)

            print(f"時間: {timestamp_str}, 抽出されたテキスト: {extracted_text}")

            tokens = extracted_text.strip().split()

        frame_count += 1

    cap.release()
    return extractions


def extract(
    video_dir: str,
    interval: int = 5,
    debug: bool = False
):
    with open(os.path.join(video_dir, 'video.info.json')) as f:
        meta = json.load(f)

    try:
        title = meta['title']
        url = meta['webpage_url']
    except KeyError:
        raise RuntimeError('Failed to read video metadata')

    video_path = os.path.join(video_dir, 'video.mp4')

    # Extract text from the video
    extractions = extract_text_from_video(video_path, interval, debug)

    result = VideoExtractions(
        title=title,
        video_path=video_path,
        url=url,
        extractions=extractions,
        extractor_version=VERSION
    )
    
    output_filename = os.path.join(video_dir, 'extractions.json')

    with open(output_filename, 'w') as json_file:
        json.dump(asdict(result), json_file, indent=2)



if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Extract text from video frames at specified intervals.')
    parser.add_argument('video_dir', type=str, help='Directory containing video file')
    parser.add_argument('--interval', type=int, default=5, help='Interval in seconds between frame processing (default: 5)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode to store images for each text extraction in ./debug folder')

    # Parse arguments
    args = parser.parse_args()

    extract(args.video_dir, args.interval, args.debug)

    print(f"Text extraction complete: {args.video_dir}")

