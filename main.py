from fastapi import FastAPI
import models
from database import engine
from routers import auth, vacation
from starlette import status
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/pdfs", StaticFiles(directory="pdfs"), name="pdfs")

@app.get("/")
def root():
    return RedirectResponse("/vacation", status_code=status.HTTP_302_FOUND)

app.include_router(auth.router)
app.include_router(vacation.router)