from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from db.engine import Base, engine, get_db
from db.models import Analysis

from hezar.models import Model
from fastapi.middleware.cors import CORSMiddleware
import logging
from http.client import HTTPException


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = Model.load("hezarai/bert-fa-sentiment-dksf")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class TextRequest(BaseModel):
    text: str


@app.post("/process-text/")
async def process_text(request: TextRequest, db: AsyncSession = Depends(get_db)):
    input_text = request.text

    try:
        res = model.predict([input_text])[0][0]
        logger.info(f"Prediction result: {res}")

        new_record = Analysis(
            text=input_text,
            result=res['label'],
            accuracy=res['score']
        )

        async with db.begin():
            db.add(new_record)
            await db.flush()

        return {"processed_text": res['label'], "accuracy": res['score']}

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")