from fastapi import FastAPI, Query
from typing import List, Optional
import json
from math import ceil
from fastapi.responses import FileResponse

app = FastAPI()

# Load the JSON data
with open("slvsh_index.json", "r") as f:
    slvsh_index = sorted(json.load(f), key=lambda x: x.get('upload_date', ''), reverse=True)

@app.get("/search")
async def search_entries(
    tokens: List[str] = Query(..., description="List of tokens to search for"),
    exclude_tokens: List[str] = Query([], description="List of tokens to exclude")
):
    
    # Filter entries that contain all specified tokens in either tokens or title
    # and exclude entries that contain any of the excluded tokens
    filtered_entries = [
        entry for entry in slvsh_index
        if all(token.upper() in entry["tokens"] or token.upper() in entry["title"].upper() for token in tokens)
        and not any(exclude_token.upper() in entry["tokens"] or exclude_token.upper() in entry["title"].upper() for exclude_token in exclude_tokens)
    ]

    return filtered_entries

@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.get("/all_tokens")
async def get_all_tokens():
    # Extract all unique tokens from the slvsh_index and titles
    all_tokens = set()
    for entry in slvsh_index:
        all_tokens.update(entry["tokens"])
        all_tokens.update(entry["title"].upper().split())
    return sorted(list(all_tokens))

@app.get("/video/{video_id}")
async def get_video(video_id: str):
    return FileResponse(f"videos/{video_id}.mp4")
