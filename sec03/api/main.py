from datetime import datetime
import json

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import ValidationError

import api.schemas.message as message_schema


def load(app):
    try:
        with open("data.json", "rt", encoding="utf-8") as f:
            data_dict = json.load(f)
            app.state.messages = message_schema.Messages.model_validate(data_dict)
    except (FileNotFoundError, ValidationError):
        # ファイルが存在しない or ファイルがうまく読めない
        # →Default の Messages を作成する
        app.state.messages = message_schema.Messages()


async def save(app):
    with open("data.json", "wt", encoding="utf-8") as f:
        f.write(app.state.messages.model_dump_json(indent=4))


@asynccontextmanager
async def lifespan(app: FastAPI):
    load(app)
    yield
    await save(app)


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['null'],
    allow_methods=['*'],
)


@app.get("/", response_class=HTMLResponse)
async def get_client(request: Request):
    """Return client HTML"""
    data = ''
    with open('client.html', 'rt', encoding='utf-8') as f:
        data = f.read()
    server_ip, port = request.scope.get("server")
    data = data.replace("127.0.0.1:8000", f"{server_ip}:{port}")
    return data


@app.get("/message", response_model=message_schema.Message)
async def get_message():
    # 最新のメッセージを返す（末尾）
    if app.state.messages.messages:
        return app.state.messages.messages[-1]
    else:
        # メッセージがない場合は空のMessage を返す
        return message_schema.Message()


@app.post("/message", response_model=message_schema.Message)
async def post_message(message: message_schema.MessageBase):
    m = message_schema.Message(time=datetime.now(),
                               **message.model_dump())
    # リストの末尾に追加
    app.state.messages.messages.append(m)
    # JSONファイルに保存
    await save(app)
    return m
