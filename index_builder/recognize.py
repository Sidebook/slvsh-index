from .models import SLVSHMatch, RecognizedText
from slvsh_tr import RegionalTesseractRecognizer
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from .loader import load_slvsh_matches
import logging

logger = logging.getLogger(__name__)

def recognize_text(
    slvsh_match: SLVSHMatch,
    interval_second: float = 1.0,
    write: bool = True
) -> list[RecognizedText]:
    logger.info(f"Running recognize_text: {slvsh_match.title}")
    screenshots = []
    video = slvsh_match.get_video()
    fps = video.get(cv2.CAP_PROP_FPS)

    interval_frames = int(interval_second * fps)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    total_screenshots = int(total_frames / interval_frames)

    logger.info(f"Collecting {total_screenshots} screenshots out of {total_frames} frames")

    for frame_count in range(total_frames):
        ret, frame = video.read()
        if not ret:
            break
        
        if frame_count % interval_frames == 0:
            timestamp = frame_count / fps
            screenshots.append((timestamp, frame))

    video.release()

    
    recognizer = RegionalTesseractRecognizer()
    logger.info(f"Running {recognizer.__class__.__name__} on {len(screenshots)} screenshots.")

    def process_image(args):
        timestamp, frame = args
        text = recognizer.infer(frame)
        return RecognizedText(text=text, timestamp=timestamp)

    recognized_texts = []
    with ThreadPoolExecutor() as executor:
        future_to_image = {executor.submit(process_image, screenshot): screenshot for screenshot in screenshots}
        for future in as_completed(future_to_image):
            result = future.result()
            if result:
                recognized_texts.append(result)

    recognized_texts.sort(key=lambda x: x.timestamp)

    logger.info(f"Text recognition completed.")
    if write:
        logger.info(f"Writing results to {slvsh_match.path}")
        SLVSHMatch(
            **{
                **slvsh_match.model_dump(),
                'texts':recognized_texts
            }
        ).write()

    return recognized_texts


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    m = load_slvsh_matches(k=1)[0]
    recognized_texts = recognize_text(m)
    print("--------------------- result ---------------------")
    for text in recognized_texts:
        print(f"{text.timestamp:0.1f}: {text.text}")
