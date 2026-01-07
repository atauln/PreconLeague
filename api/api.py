from fastapi import FastAPI
from routers import users, decks, snapshots, cards
import uvicorn

app = FastAPI(
    title="Precon League API",
    description="Internal API for @atauln's MTG Preconstructed Deck League",
    version="1.0.0",
)

app.include_router(users.router)
app.include_router(decks.router)
app.include_router(snapshots.router)
app.include_router(cards.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Precon League API! Author: @atauln on Github"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)