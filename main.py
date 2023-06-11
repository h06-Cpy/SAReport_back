from fastapi import FastAPI

from database import Session

app = FastAPI()
session = Session()

@app.get('/')
def hi():
    return 'hi'
