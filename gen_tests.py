import os
import cv2
import numpy as np

def pick_screenshots(video_path: str, interval_seconds: int = 400):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    interval = int(fps * interval_seconds)
    random_offset = np.random.randint(0, interval)
    keep_frames = []

    # Seek to the random offset
    frame_count = random_offset
    while True:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count)
        ret, frame = cap.read()
        if not ret:
            break
        keep_frames.append(frame)
        frame_count += interval
    cap.release()
    return keep_frames

def save_screenshots(root_dir: str = './videos', interval_seconds: int = 400):
    videos = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if 'video.mp4' in filenames:
            videos.append(os.path.join(dirpath, 'video.mp4'))

    np.random.seed(42)
    num_samples = min(200, len(videos))
    sampled_videos = np.random.choice(videos, size=num_samples, replace=False)

    img_dir = os.path.join('eval', 'img')
    os.makedirs(img_dir, exist_ok=True)
    i = 0
    for video_path in sampled_videos:
        print(f'processing {video_path}')
        screenshots = pick_screenshots(video_path, interval_seconds)
        for screenshot in screenshots:
            cv2.imwrite(os.path.join('slvsh-tr', 'slvsh_tr', 'assets', 'img', f'test_{i:04d}.png'), screenshot)
            i += 1

if __name__ == '__main__':
    save_screenshots()
