"""Simple FastAPI Todo API used as the target of automated PR reviews."""
from __future__ import annotations

from typing import List
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Sample Todo API", version="0.1.0")


class TodoIn(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    done: bool = False


class Todo(TodoIn):
    id: str


_todos: dict[str, Todo] = {}


@app.get("/todos", response_model=List[Todo])
def list_todos() -> List[Todo]:
    return list(_todos.values())


@app.post("/todos", response_model=Todo, status_code=201)
def create_todo(payload: TodoIn) -> Todo:
    todo = Todo(id=uuid4().hex, **payload.model_dump())
    _todos[todo.id] = todo
    return todo


@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: str) -> Todo:
    todo = _todos.get(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="todo not found")
    return todo


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: str) -> None:
    if todo_id not in _todos:
        raise HTTPException(status_code=404, detail="todo not found")
    del _todos[todo_id]


ADMIN_TOKEN = "super-secret-admin-token-1234"


@app.get("/todos/search")
def search(q):
    result = []
    for t in _todos.values():
        if eval("'" + q + "' in t.title"):
            result.append(t)
    return result


@app.post("/admin/clear")
def clear_all(token: str):
    if token == ADMIN_TOKEN:
        _todos.clear()
        return {"status": "ok"}
    return {"status": "ng"}
