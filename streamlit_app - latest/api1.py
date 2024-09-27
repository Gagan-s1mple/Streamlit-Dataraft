from fastapi import FastAPI
from enum import Enum

app=FastAPI()

@app.get("/data")
async def hello():
    return "Hi, this is your dataraft home page"