from fastapi import FastAPI
from routers import users, decks, snapshots, cards
import uvicorn
import os

def _build_servers_from_env() -> list | None:
    api_url = os.getenv("API_URL", "").strip()
    # Only use servers entry when a fully-qualified URL is provided (starts with http:// or https://)
    if api_url.lower().startswith("http://") or api_url.lower().startswith("https://"):
        return [{"url": api_url, "description": "Current API server"}]
    return None


app = FastAPI(
    title="Precon League API",
    description="Internal API for @atauln's MTG Preconstructed Deck League",
    version="1.0.0",
    servers=_build_servers_from_env() or None,
)

app.include_router(users.router)
app.include_router(decks.router)
app.include_router(snapshots.router)
app.include_router(cards.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Precon League API! Author: @atauln on Github"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)