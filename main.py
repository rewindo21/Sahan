from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import Base, engine, get_db, SessionLocal

from db.models import Analysis

app = FastAPI()


@app.on_event("startup")
async def init_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class TextRequest(BaseModel):
    text: str


@app.post("/process-text/")
async def process_text(request: TextRequest, db: AsyncSession = Depends(get_db)):
    input_text = request.text

    processed_text = input_text.upper()  # Example processing

    new_record = Analysis(
        text=input_text,
        result=processed_text,
        accuracy=100  # Example accuracy value
    )

    async with db.begin():
        db.add(new_record)
        await db.flush()

    return {"processed_text": processed_text}
