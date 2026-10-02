"""Code-owned declarations. Export via app.openapi(); never edit its generated output."""
import json
from pathlib import Path
import sys

# This example may be exported directly without installing an application package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from store import save, load


class ItemCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1)
    note: str | None = None


class Item(BaseModel):
    id: str
    name: str
    note: str | None


class MissingItem(BaseModel):
    detail: str


def create_app(database):
    app = FastAPI(title="Local item example", version="1.0.0", docs_url=None, redoc_url=None)

    @app.post("/items", operation_id="createItem", status_code=201, response_model=Item)
    def create_item(request: ItemCreate):
        return save(database, request.name, request.note)

    @app.get("/items/{item_id}", operation_id="getItem", response_model=Item,
             responses={404: {"model": MissingItem}})
    def get_item(item_id: str):
        found = load(database, item_id)
        if found is None:
            raise HTTPException(status_code=404, detail="missing item")
        return found

    return app


if __name__ == "__main__":
    # Schema export creates no database and executes no business request.
    print(json.dumps(create_app(None).openapi(), sort_keys=True, indent=2))
