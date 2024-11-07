from fastapi import FastAPI, Query
from typing import List, Optional
import json
from math import ceil
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


index_path = os.path.join(os.path.dirname(__file__), "../slvsh_index.json")

# Load the JSON data
with open(index_path, "r") as f:
    slvsh_index = sorted(json.load(f), key=lambda x: x.get(
        'upload_date', ''), reverse=True)


def get_common_tricks():
    trick_count = {}
    for entry in slvsh_index:
        for component in entry["components"]:
            trick_count[component] = trick_count.get(component, 0) + 1
    freq = sorted(trick_count.items(), key=lambda x: x[1], reverse=True)
    return [comp for comp, count in freq]


common_tricks = get_common_tricks()


def tokenize(text: str):
    return [token.strip().lower() for token in text.removesuffix(".").replace(",", " ").split()]


def title_search(candidates, query: str):
    for trick in candidates:
        if query.lower() in trick['title'].lower():
            yield trick
            continue


def exact_search(candidates, query: str, ignore_order=False):
    tokenized_query = tokenize(query)
    for trick in candidates:
        for component in trick['components']:
            tokenized_component = tokenize(component)
            if ignore_order:
                if set(tokenized_component) == set(tokenized_query):
                    yield trick
                    break
            else:
                if tokenized_component == tokenized_query:
                    yield trick
                    break


def fuzzy_search(candidates, query: str):
    tokenized_query = set(tokenize(query))
    for trick in candidates:
        for component in trick['components']:
            if len(tokenized_query - set(tokenize(component))) == 0:
                yield trick
                break


def search(
    trick_query: str,
    title_query: Optional[str] = None,
    allow_additions: bool = True,
):
    candidates = slvsh_index
    if title_query:
        candidates = title_search(candidates, title_query)

    if trick_query:
        if allow_additions:
            yield from fuzzy_search(candidates, trick_query)
        else:
            yield from exact_search(candidates, trick_query, ignore_order=True)
    else:
        yield from candidates


@app.get("/api/search")
async def search_entries(
    trick_query: str = Query(default=""),
    title_query: Optional[str] = Query(default=None),
    allow_additions: bool = Query(default=True),
    page: int = Query(default=0, ge=0),
    page_size: int = Query(default=20, ge=1, le=100),
):
    all_results = list(
        search(trick_query.strip(), title_query.strip(), allow_additions))
    page_results = all_results[page * page_size:(page + 1) * page_size]

    return {
        "results": page_results,
        "page": page,
        "page_size": page_size,
        "max_page": ceil(len(all_results) / page_size) - 1,
        "count": len(all_results),
    }


@app.get("/api/common_tricks")
async def get_common_tricks():
    return common_tricks
