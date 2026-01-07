from fastapi import FastAPI
from routers import users, decks
import uvicorn

app = FastAPI()

app.include_router(users.router)
app.include_router(decks.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Precon League API! Author: @atauln on Github"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)