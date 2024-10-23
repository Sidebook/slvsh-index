import os
from .models import SLVSHMatch
from typing import Optional

def load_slvsh_matches(
    root_dir: str = './videos',
    k: Optional[int] = None
) -> list[SLVSHMatch]:
    results = []
    for dirpath, _, filenames in os.walk(root_dir):
        if 'video.mp4' in filenames and 'video.info.json' in filenames:
            try:
                match = SLVSHMatch.load(dirpath)
                if match.is_valid():
                    results.append(match)
                    if k and len(results) >= k:
                        break
                else:
                    print(f"Skipped {dirpath}")
            except Exception as e:
                raise RuntimeError(f"Error loading match from {dirpath}: {str(e)}")
    return results

