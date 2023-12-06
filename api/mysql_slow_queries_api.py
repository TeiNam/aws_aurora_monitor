import os
from fastapi import FastAPI, Query, Depends
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from modules.mongodb_connector import MongoDBConnector

app = FastAPI()

MONGODB_COLLECTION_NAME = os.getenv("MONGODB_SLOWLOG_COLLECTION_NAME")
kst_delta = timedelta(hours=9)


class Item(BaseModel):
    instance: str
    pid: int
    user: str
    host: str
    db: str
    time: int
    sql_text: str
    start: datetime = Field(alias="start")
    end: datetime = Field(alias="end")


def get_database():
    return MongoDBConnector.get_database()


@app.get("/items/")
async def get_items(days: int = Query(None, alias="days"), db=Depends(get_database)):
    collection = db[MONGODB_COLLECTION_NAME]
    items = []
    query = {}
    sort = [("_id", -1)]

    if days is not None:
        target_date = datetime.utcnow() - timedelta(days=days)
        query = {"start": {"$gte": target_date}}

    async for item in collection.find(query).sort(sort):
        item['_id'] = str(item['_id'])
        if 'start' in item:
            item['start'] = item['start'] + kst_delta
        if 'end' in item:
            item['end'] = item['end'] + kst_delta
        items.append(Item(**item))

    return items
