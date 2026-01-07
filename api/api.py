from fastapi import FastAPI
from routers import users
import uvicorn

app = FastAPI()

user_routers = users.router
app.include_router(user_routers)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Precon League API! Author: @atauln on Github"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)