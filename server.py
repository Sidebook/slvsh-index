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
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page")
):
    
    # Filter entries that contain all specified tokens in either tokens or title
    return [entry for entry in slvsh_index
        if all(token.upper() in entry["tokens"] or token.upper() in entry["title"].upper() for token in tokens)]

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
