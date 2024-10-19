import os
import cv2
import numpy as np

def pick_screenshots(video_path: str, interval_seconds: int = 60):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    interval = int(fps * interval_seconds)
    frame_count = 0
    random_offset = np.random.randint(0, interval)
    keep_frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count != 0 and (frame_count - random_offset) % interval == 0:
            keep_frames.append(frame)
        frame_count += 1
    cap.release()
    return keep_frames

def save_screenshots(root_dir: str = './videos', interval_seconds: int = 60):
    videos = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if 'video.mp4' in filenames:
            videos.append(os.path.join(dirpath, 'video.mp4'))

    np.random.seed(42)
    num_samples = min(30, len(videos))
    sampled_videos = np.random.choice(videos, size=num_samples, replace=False)

    img_dir = os.path.join('eval', 'img')
    os.makedirs(img_dir, exist_ok=True)
    for video_i, video_path in enumerate(sampled_videos):
        print(f'processing {video_path}')
        screenshots = pick_screenshots(video_path, interval_seconds)
        for i, screenshot in enumerate(screenshots):
            cv2.imwrite(os.path.join('eval', 'img', f'test_{video_i:02d}_{i:03d}.png'), screenshot)

if __name__ == '__main__':
    import json
    import glob

    def create_test_json():
        img_dir = './eval/img'
        test_cases = []

        # Iterate through all PNG images in the directory
        for img_path in glob.glob(os.path.join(img_dir, '*.png')):
            # Create a test case for each image
            test_case = {
                "image_path": img_path,
                "expected": ""
            }
            test_cases.append(test_case)

        # Write the test cases to a JSON file
        with open('./eval/tests.json', 'w') as f:
            json.dump(test_cases, f, indent=2)

        print(f"Created test cases for {len(test_cases)} images in ./eval/tests.json")

    create_test_json()
    #save_screenshots()
