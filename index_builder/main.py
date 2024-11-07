from .download import download_youtube_channel
from .loader import load_slvsh_matches
from .aggregate import aggregate
from .recognize import recognize_text
import argparse
import logging
import json


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--force', action='store_true', default=False)
    parser.add_argument('step', type=str, default='all', choices=['download', 'recognize', 'aggregate', 'all'])
    args = parser.parse_args()

    if args.step == 'download' or args.step == 'all':
        download_youtube_channel()
    if args.step == 'recognize' or args.step == 'all':
        for m in load_slvsh_matches():
            if m.texts is None or args.force:
                recognize_text(m)

    if args.step == 'aggregate' or args.step == 'all':
        all_tricks = []
        for m in load_slvsh_matches():
            all_tricks.extend(aggregate(m))

        with open('slvsh_index.json', 'w') as f:
            json.dump([{
                'components': t.components,
                'start': t.start,
                'end': t.end,
                'title': t.source.title,
                'url': f'https://www.youtube.com/watch?v={t.source.video_id}&t={int(t.start)}',
                'video_id': t.source.video_id,
                'upload_date': t.source.upload_date
            } for t in all_tricks], f, indent=2)
