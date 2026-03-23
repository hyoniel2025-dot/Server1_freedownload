from dotenv import load_dotenv
import os
from fastapi import Header, HTTPException

load_dotenv()  # Carga variables desde .env

API_KEY = os.getenv("API_KEY")

def verify_token(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="No autorizado")