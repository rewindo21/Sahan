from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from db.engine import Base, engine, get_db
from db.models import Analysis

from hezar.models import Model
from fastapi.middleware.cors import CORSMiddleware
model = Model.load("hezarai/bert-fa-sentiment-dksf")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class TextRequest(BaseModel):
    text: str


@app.post("/process-text/")
async def process_text(request: TextRequest, db: AsyncSession = Depends(get_db)):
    input_text = request.text

    res = model.predict([input_text])[0][0]
    print(res)
    new_record = Analysis(
        text=input_text,
        result=res['label'],
        accuracy=res['score']
    )

    async with db.begin():
        db.add(new_record)
        await db.flush()

    return {"processed_text": res['label'],"accuracy" : res['score']}

