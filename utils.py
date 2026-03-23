from dotenv import load_dotenv
import os
import math
import subprocess
import base64
import uuid
import requests

load_dotenv()  # Carga variables desde .env

UPLOAD_DIR = "uploads"
CHUNK_DIR = "chunks"
COMPRESS_DIR = "compressed"
LINK_DIR = "links"
EXTRACT_DIR = "extracted"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHUNK_DIR, exist_ok=True)
os.makedirs(COMPRESS_DIR, exist_ok=True)
os.makedirs(LINK_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)

CHUNK_SIZE = 100 * 1024 * 1024

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")

BASE_URL = os.getenv("BASE_URL")

def save_file(file):
    path = os.path.join(UPLOAD_DIR, file.filename)
    with open(path, "wb") as f:
        f.write(file.file.read())
    return path

def split_file(filepath):
    chunks = []
    file_size = os.path.getsize(filepath)
    total_parts = math.ceil(file_size / CHUNK_SIZE)

    with open(filepath, "rb") as f:
        for i in range(total_parts):
            chunk_name = f"{os.path.basename(filepath)}.part{i}"
            chunk_path = os.path.join(CHUNK_DIR, chunk_name)
            with open(chunk_path, "wb") as chunk:
                chunk.write(f.read(CHUNK_SIZE))
            chunks.append(chunk_path)
    return chunks

def compress_split_7z(filename, chunks):
    archive_name = f"{filename}.7z"
    archive_path = os.path.join(COMPRESS_DIR, archive_name)
    cmd = ["7z", "a", "-v100m", archive_path] + chunks
    subprocess.run(cmd)

    parts = []
    i = 1
    while True:
        part = f"{archive_path}.{str(i).zfill(3)}"
        if os.path.exists(part):
            parts.append(part)
            i += 1
        else:
            break
    return parts

def delete_chunks(chunks):
    for c in chunks:
        if os.path.exists(c):
            os.remove(c)

def generate_link_id(filename):
    raw = f"{filename}-{uuid.uuid4()}"
    return base64.b64encode(raw.encode()).decode()

def create_txt(filename, link):
    name = os.path.splitext(filename)[0]
    txt_path = os.path.join(LINK_DIR, f"{name}.txt")
    with open(txt_path, "w") as f:
        f.write(link)
    return txt_path

def send_txt_to_telegram(txt_path):
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(txt_path, "rb") as f:
        requests.post(url, files={"document": f}, data={"chat_id": CHAT_ID})

def extract_7z(first_part):
    output_dir = os.path.join(EXTRACT_DIR, os.path.basename(first_part))
    os.makedirs(output_dir, exist_ok=True)
    subprocess.run(["7z", "x", first_part, f"-o{output_dir}", "-y"])
    files = os.listdir(output_dir)
    if files:
        return os.path.join(output_dir, files[0])
    return None