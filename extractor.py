from typing import List
import cv2
import pytesseract
import argparse
import numpy as np
import os
import json
from dataclasses import dataclass

from dataclasses import dataclass, asdict
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


def extract_text_from_video(video_path, interval_seconds=5, debug=False) -> list[FrameExtraction]:
    debug_folder = "./debug"
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

    while True:
        # Read the next frame
        ret, frame = cap.read()

        if not ret:
            break

        height, width = frame.shape[:2]
        roi = frame[int(height * 0.87):int(height * 0.93), :]

        if frame_count % keep_frame_interval == 0:
            keep_frames.append(roi)

        if len(keep_frames) > keep_frame_num:
            keep_frames = keep_frames[1:]
        
        if len(keep_frames) < keep_frame_num:
            continue

        # Process every nth frame where n is the interval
        if frame_count % interval == 0:

            minutes = int(frame_count / fps // 60)
            seconds = int(frame_count / fps % 60)
            timestamp_str = f"{minutes:02d}:{seconds:02d}"

            # Convert ROI to grayscale
            gray_frame = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            # Apply thresholding to make the text more prominent
            _, thresh_image = cv2.threshold(roi, 150, 255, cv2.THRESH_BINARY_INV)

            # Apply OCR to the cropped area
            config='--psm 7 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,. "'
            extracted_text = pytesseract.image_to_string(thresh_image, config=config).strip()

            extraction = FrameExtraction(
                timestamp=frame_count / fps,
                text=extracted_text,
                frame_number=frame_count
            )

            extractions.append(extraction)

            print(f"Time: {timestamp_str}, Extracted Text: {extracted_text}")

            # If debug mode is enabled, store extracted_text in json file
            if debug:

                debug_folder = os.path.join(os.path.dirname(video_path), 'debug')
                os.makedirs(debug_folder, exist_ok=True)
                
                # Create an image with detected text
                text_image = np.zeros_like(gray_frame)

                cv2.putText(text_image, extracted_text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                
                # Create an image with timestamp
                timestamp_image = np.zeros_like(gray_frame)
                cv2.putText(timestamp_image, timestamp_str, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                
                # Stack the images vertically
                stacked_image = cv2.vconcat([
                    gray_frame,
                    cv2.cvtColor(thresh_image, cv2.COLOR_BGR2GRAY),
                    text_image,
                    timestamp_image
                ])
                
                # Save the stacked image
                stacked_image_path = os.path.join(debug_folder, f"{timestamp_str}_debug.png")
                cv2.imwrite(stacked_image_path, stacked_image)

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

