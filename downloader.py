import yt_dlp
import argparse
import os

def download_youtube_channel(channel_url, output_dir='./videos'):
    # Set up yt-dlp options
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{output_dir}/%(title)s/video.%(ext)s',
        'ignoreerrors': True,  # Continue on download errors
        'quiet': False,  # Show progress
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',  # Preferred video format
        }],
        'writeinfojson': True,
        'download_archive': os.path.join(output_dir, 'downloaded_videos.txt'),  # Keep track of downloaded videos
    }

    try:
        # Download all videos from the channel, skipping previously downloaded ones
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([channel_url])
    except Exception as e:
        print(f"Error downloading videos: {e}")


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Download all videos from a YouTube channel, skipping previously downloaded ones.')
    parser.add_argument('--channel_url', type=str, default='https://www.youtube.com/channel/UCwYNq_huF2CYE4WcFKKvmkg', help='URL of the YouTube channel to download')
    parser.add_argument('--output_dir', default='./videos', type=str, help='Output directory for downloaded videos')

    # Parse arguments
    args = parser.parse_args()

    # Download the videos
    download_youtube_channel(args.channel_url, args.output_dir)
