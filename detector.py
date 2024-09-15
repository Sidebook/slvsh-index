import argparse
from dataclasses import dataclass
import json
import os
from typing import List, Literal, Set

from extractor import FrameExtraction, VideoExtractions


def load_tricks() -> Set[str]:
    with open('./tricks.txt') as file:
        return {line.strip() for line in file.readlines() if line.strip()}

tricks = load_tricks()

def scan_directories(root_dir: str = './videos') -> List[str]:
    extraction_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if 'extractions.json' in filenames:
            extraction_files.append(os.path.join(dirpath, 'extractions.json'))
    return extraction_files


def analyse_trick(extraction: FrameExtraction):
    raw_tokens =extraction.get_all_tokens()
    processed_tokens = [process_token(token) for token in raw_tokens]
    known_tokens = [token for token in processed_tokens if token in tricks]
    valid = len(known_tokens) > 0 and len(known_tokens) >= len(processed_tokens) // 2

    if "REVENGE" in known_tokens:
        known_tokens.remove("REVENGE")

    return extraction, valid, known_tokens


def process_token(token: str) -> str:
    token = token.rstrip('.').rstrip(',')
    return token


def extract_tricks(extractions: VideoExtractions):
    frame_tricks = [analyse_trick(e) for e in extractions.extractions]

    info_path = os.path.join(os.path.dirname(extractions.video_path), 'video.info.json')
    with open(info_path, 'r') as f:
        video_info = json.load(f)
    upload_date = video_info.get('upload_date')

    tricks = []
    current_trick = None
    for extraction, valid, known_tokens in frame_tricks:
        if valid:
            if current_trick is not None:
                if len(set(current_trick["tokens"]).difference(known_tokens)) >= 2:
                    tricks.append(current_trick)
                    current_trick = None
            if current_trick is None:
                current_trick = {
                    "tokens": known_tokens,
                    "start": extraction.timestamp,
                    "title": extractions.title,
                    "url": f"{extractions.url}&t={int(max(extraction.timestamp - 2, 0))}",
                    "upload_date": upload_date,
                }
            else:
                current = current_trick["tokens"]
                next = known_tokens

                merged = current.copy()
                i = 0
                for token in next:
                    if token in merged:
                        i = max(merged.index(token), i)
                    if token not in merged:
                        merged.insert(i, token)

                # Update current_trick tokens with the merged list
                current_trick["tokens"] = merged
                current_trick["end"] = extraction.timestamp + 5
        else:
            if current_trick is not None:
                tricks.append(current_trick)
            current_trick = None

    if current_trick is not None:
        tricks.append(current_trick)

    # Convert tokens from set to list in-place for each trick
    for trick in tricks:
        if trick is not None and "tokens" in trick:
            trick["tokens"] = sorted(trick["tokens"])  # Sorting for consistent order

    return tricks

def main():
    parser = argparse.ArgumentParser(description='Scan directories for extractions.json files and process them.')
    parser.add_argument('--root_dir', default='./videos', help='Root directory to start scanning from')
    args = parser.parse_args()

    extraction_files = scan_directories(args.root_dir)
    
    all_tricks = []
    for file_path in extraction_files:
        print(f"Processing: {file_path}")
        with open(file_path) as file:
            try:
                extractions = VideoExtractions.from_json(file.read())
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        all_tricks.extend(extract_tricks(extractions))
    
    output_file = './slvsh_index.json'
    with open(output_file, 'w') as f:
        json.dump(all_tricks, f, indent=2)
    print(f"Saved detected tricks to: {output_file}")


if __name__ == "__main__":
    main()
