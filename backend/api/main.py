from __future__ import annotations

import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from api.routes import alerts, cascade, chatbot, emergency, predict, routing, signals
from api.state import get_full_state
from api.websocket import ConnectionManager

app = FastAPI(title="HackZilla Traffic AI", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router, prefix="/api/predict", tags=["predict"])
app.include_router(cascade.router, prefix="/api/cascade", tags=["cascade"])
app.include_router(routing.router, prefix="/api/route", tags=["routing"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(emergency.router, prefix="/api/emergency", tags=["emergency"])
app.include_router(signals.router, prefix="/api/signals", tags=["signals"])
app.include_router(chatbot.router, prefix="/api/chat", tags=["chat"])

manager = ConnectionManager()


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "service": "HackZilla Traffic AI"}


@app.get("/api/state")
async def state() -> dict:
    return get_full_state()


@app.websocket("/ws/live")
async def live_updates(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.send_json(get_full_state())
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
