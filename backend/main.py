import hashlib
import json
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, Literal, TypedDict
from urllib.parse import unquote

import meilisearch_python_async
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

if "MEILI_URL" in os.environ:
    MEILI_URL = os.environ["MEILI_URL"]
else:
    raise EnvironmentError("You have to define the env var `MEILI_URL`")

DEV = "DEV" in os.environ
if DEV:
    MEILI_KEY = None
else:
    if "MEILI_KEY" in os.environ:
        MEILI_KEY = os.environ["MEILI_KEY"]
    else:
        raise EnvironmentError("You have to define the env var `MEILI_KEY`")

DB_PATH = Path("/data/db.json")

Category = Literal["Groceries", "Alcohol"]


class Item(TypedDict):
    name: str
    id: int


class Active(TypedDict):
    Groceries: list[str]
    Alcohol: list[str]


class Db(TypedDict):
    active: Active
    Groceries: list[Item]
    Alcohol: list[Item]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    if not os.path.exists(DB_PATH):
        await init_db()
    yield
    await meili.aclose()


app = FastAPI(title="Groceries API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
time.sleep(5)  # give meilisearch the time to initialize or it will timeout
meili = meilisearch_python_async.Client(MEILI_URL, MEILI_KEY)
with open(DB_PATH, "r") as f:
    db: Db = json.load(f)


async def init_db():
    for index in meili.get_indexes()["results"]:
        index.delete()
    await meili.create_index("Groceries", {"primaryKey": "id"})
    await meili.create_index("Alcohol", {"primaryKey": "id"})
    db = {"active": {"Groceries": [], "Alcohol": []}, "Groceries": [], "Alcohol": []}
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DB_PATH, "w") as fp:
        json.dump(db, fp)


def get_id_from_name(string: str):
    return int(hashlib.md5(string.encode("utf-8")).hexdigest()[:5], 16)


def save():
    with open(DB_PATH, "w") as fp:
        json.dump(db, fp)


@app.get("/api")
def get_items():
    return db["active"]


@app.get("/api/key")
def get_key():
    return db["active"]


@app.delete("/api/{category}/{item_name}")
def delete_item(category: Category, item_name: str):
    item_name = unquote(item_name)
    if item_name in db["active"][category]:
        db["active"][category].remove(item_name)
    save()
    return db["active"]


@app.delete("/api/meili/{category}/{item_name}")
async def delete_meili_item(category: Category, item_name: str):
    item_name = unquote(item_name)
    for item in db[category]:
        if item["name"] == item_name:
            db[category].remove(item)
            break
    await meili.index(category).delete_document(get_id_from_name(item_name))
    return await delete_item(category, item_name)


@app.post("/api/{category}/{item_name}")
async def add_item(category: Category, item_name: str):
    item_name = unquote(item_name)
    item_name = item_name.capitalize()
    if item_name in db["active"][category]:
        db["active"][category].remove(item_name)
    db["active"][category].insert(0, item_name)
    db[category] = [item for item in db[category] if item.get("name") != item_name]
    db[category].insert(
        0,
        {
            "id": get_id_from_name(item_name),
            "name": item_name,
        },
    )
    await meili.index(category).update_documents(
        [
            {
                "id": get_id_from_name(item_name),
                "name": item_name,
            }
        ]
    )
    save()
    return db["active"]


@app.get("/api/search/{category}/{search_input}")
async def get_search(category: Category, search_input: str):
    res = await meili.index(category).search(search_input, limit=8)
    return [hit["name"] for hit in res.hits]


if not DEV:
    # in prod, FastAPI will server the compiled svelte bundle
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
