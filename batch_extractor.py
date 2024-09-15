import os
import argparse
from extractor import extract

def scan_and_extract(root_dir: str = './videos', interval: int = 5, debug: bool = False, force: bool = False):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if 'video.mp4' in filenames and ('extractions.json' not in filenames or force):
            video_dir = dirpath
            print(f"Processing: {video_dir}")
            extract(video_dir, interval, debug)

def main():
    parser = argparse.ArgumentParser(description='Batch extract text from videos without existing extractions.')
    parser.add_argument('--root_dir', default='./videos', help='Root directory to start scanning from')
    parser.add_argument('--interval', type=int, default=5, help='Interval in seconds between frame processing (default: 5)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode to store images for each text extraction')
    parser.add_argument('--force', action='store_true', help='Force extraction even if extractions.json already exists')
    args = parser.parse_args()

    scan_and_extract(args.root_dir, args.interval, args.debug, args.force)

if __name__ == "__main__":
    main()
