from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class Item(BaseModel):
    text: str = None
    is_done: bool = False

app = FastAPI()

items = []

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/items", response_model=list[Item])
def create_item(item: Item):
    items.append(item)
    return items

@app.get("/items", response_model=list[Item])
def read_items():
    return items

@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return items[item_id]
