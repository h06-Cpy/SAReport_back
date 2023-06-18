from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware

from database import get_db, Session
from out_scheme import ReportDataModel
from process_report_data import get_report_data_model
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

app = FastAPI()
origins = ['http://localhost:5173']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)
# app.mount("/assets", StaticFiles(directory="frontend/dist/assets"))

@app.get('/api', response_model=ReportDataModel)
def report_data(session: Session = Depends(get_db)):
    return get_report_data_model(session)

# @app.get("/")
# def index():
#     return FileResponse("frontend/dist/index.html")