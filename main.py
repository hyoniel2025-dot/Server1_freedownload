from dotenv import load_dotenv
import os
from fastapi import FastAPI, UploadFile, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, File
from utils import (
    save_file, split_file, compress_split_7z,
    delete_chunks, generate_link_id,
    create_txt, send_txt_to_telegram,
    extract_7z
)
from auth import verify_token

load_dotenv()  # Carga variables desde .env

Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload")
def upload(file: UploadFile, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    path = save_file(file)
    chunks = split_file(path)
    parts = compress_split_7z(file.filename, chunks)
    delete_chunks(chunks)

    link_id = generate_link_id(file.filename)
    link = f"{os.getenv('BASE_URL')}/{link_id}"

    txt_path = create_txt(file.filename, link)
    send_txt_to_telegram(txt_path)  # ⚠️ funciona solo si BOT_TOKEN y CHAT_ID están rellenos

    new_file = File(
        filename=file.filename,
        path=path,
        size=os.path.getsize(path),
        chunks="|".join(chunks),
        compressed_parts="|".join(parts),
        link_id=link_id
    )
    db.add(new_file)
    db.commit()
    return {"msg": "ok", "link": link}

@app.get("/{link_id}")
def download(link_id: str, db: Session = Depends(get_db)):
    file = db.query(File).filter(File.link_id == link_id).first()
    if not file:
        return {"error": "Link inválido"}
    parts = file.compressed_parts.split("|")
    extracted = extract_7z(parts[0])
    return FileResponse(extracted, filename=file.filename)