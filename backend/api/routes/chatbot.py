from __future__ import annotations

import os

import anthropic
from fastapi import APIRouter
from pydantic import BaseModel

from api.state import get_full_state

router = APIRouter()


class ChatMessage(BaseModel):
    text: str


@router.post("/")
async def chat(message: ChatMessage) -> dict:
    state = get_full_state()
    hotspots = [k for k, v in state["locations"].items() if v["congestion"] in ["High", "Very High"]]
    if not os.getenv("ANTHROPIC_API_KEY"):
        return {
            "response": (
                f"Current hotspots: {', '.join(hotspots[:5]) or 'none'}. "
                "For India Gate to IGI Airport, use the green-corridor route via central Delhi "
                "and avoid DND/Akshardham due to active phantom/cascade risk."
            ),
            "mode": "offline-demo",
        }

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        system=(
            "You are an AI traffic assistant for Delhi-NCR. Use live hotspots and "
            f"alerts to answer. Hotspots: {hotspots}. Alerts: {state['alerts'][:5]}"
        ),
        messages=[{"role": "user", "content": message.text}],
    )
    return {"response": response.content[0].text, "mode": "anthropic"}
