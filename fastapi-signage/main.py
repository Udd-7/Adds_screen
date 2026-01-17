# from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
# from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware
# import shutil
# import os
# import time

# app = FastAPI()

# # ================= CORS =================
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ================= FOLDERS =================
# os.makedirs("uploads/images", exist_ok=True)
# os.makedirs("uploads/videos", exist_ok=True)
# os.makedirs("uploads/pdfs", exist_ok=True)
# os.makedirs("player", exist_ok=True)

# # ================= STATIC =================
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# app.mount("/player", StaticFiles(directory="player"), name="player")

# # ================= IN-MEMORY DB =================
# playlists = {}      # { deviceId: [ {type,url}, ... ] }
# active_ws = {}      # { deviceId: websocket }

# # ================= UPLOAD API =================
# @app.post("/api/upload")
# async def upload(file: UploadFile = File(...)):
#     ext = file.filename.split(".")[-1].lower()

#     if ext in ["jpg", "jpeg", "png", "gif"]:
#         folder = "uploads/images"
#         typ = "images"
#     elif ext in ["mp4", "mkv", "avi"]:
#         folder = "uploads/videos"
#         typ = "videos"
#     elif ext == "pdf":
#         folder = "uploads/pdfs"
#         typ = "pdfs"
#     else:
#         return {"error": "Unsupported file type"}

#     filename = f"{int(time.time()*1000)}_{file.filename}"
#     path = os.path.join(folder, filename)

#     with open(path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     return {
#         "filename": filename,
#         "type": typ,
#         "url": f"/uploads/{typ}/{filename}"
#     }

# # ================= ADD TO PLAYLIST (FIXED) =================
# @app.post("/api/playlist/add")
# async def add_playlist(data: dict):
#     device = data["deviceId"]
#     filename = data["filename"]
#     typ = data["type"]

#     # ✅ create playlist if not exists
#     if device not in playlists:
#         playlists[device] = []

#     item = {
#         "type": typ,
#         "url": f"/uploads/{typ}/{filename}"
#     }

#     # ✅ APPEND (NOT overwrite)
#     playlists[device].append(item)

#     # ✅ LIVE PUSH FULL PLAYLIST
#     if device in active_ws:
#         await active_ws[device].send_json(playlists[device])

#     return {
#         "status": "added",
#         "device": device,
#         "total_items": len(playlists[device])
#     }

# # ================= GET PLAYLIST =================
# @app.get("/api/playlist/{device}")
# def get_playlist(device: str):
#     return playlists.get(device, [])

# # ================= WEBSOCKET =================
# @app.websocket("/ws/{device}")
# async def websocket_endpoint(ws: WebSocket, device: str):
#     await ws.accept()
#     active_ws[device] = ws

#     # Send existing playlist on connect
#     if device in playlists:
#         await ws.send_json(playlists[device])

#     try:
#         while True:
#             await ws.receive_text()
#     except WebSocketDisconnect:
#         if device in active_ws:
#             del active_ws[device]
























# from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
# from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware
# import shutil, os, time, json, uuid

# app = FastAPI()

# # ================= CORS =================
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ================= CONSTANTS =================
# PLAYLIST_FILE = "playlist_data.json"

# # ================= HELPERS =================
# def load_playlists():
#     if os.path.exists(PLAYLIST_FILE):
#         with open(PLAYLIST_FILE, "r") as f:
#             return json.load(f)
#     return {}

# def save_playlists():
#     with open(PLAYLIST_FILE, "w") as f:
#         json.dump(playlists, f, indent=2)

# # ================= FOLDERS =================
# os.makedirs("uploads/images", exist_ok=True)
# os.makedirs("uploads/videos", exist_ok=True)
# os.makedirs("uploads/pdfs", exist_ok=True)
# os.makedirs("player", exist_ok=True)

# # ================= STATIC =================
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# app.mount("/player", StaticFiles(directory="player"), name="player")

# # ================= DATA =================
# playlists = load_playlists()     # 🔥 persistent
# active_ws = {}                   # deviceId → websocket

# # ================= UPLOAD =================
# @app.post("/api/upload")
# async def upload(file: UploadFile = File(...)):
#     ext = file.filename.split(".")[-1].lower()

#     if ext in ["jpg", "jpeg", "png", "gif"]:
#         folder, typ = "uploads/images", "images"
#     elif ext in ["mp4", "mkv", "avi"]:
#         folder, typ = "uploads/videos", "videos"
#     elif ext == "pdf":
#         folder, typ = "uploads/pdfs", "pdfs"
#     else:
#         return {"error": "Unsupported file type"}

#     filename = f"{int(time.time()*1000)}_{file.filename}"
#     path = os.path.join(folder, filename)

#     with open(path, "wb") as f:
#         shutil.copyfileobj(file.file, f)

#     return {
#         "filename": filename,
#         "type": typ,
#         "url": f"/uploads/{typ}/{filename}"
#     }

# # ================= ADD PLAYLIST ITEM =================
# @app.post("/api/playlist/add")
# async def add_playlist(data: dict):
#     device = data["deviceId"]
#     filename = data["filename"]
#     typ = data["type"]
#     duration = data.get("duration", 10)  # ⏱ default 10 sec

#     if device not in playlists:
#         playlists[device] = []

#     item = {
#         "id": str(uuid.uuid4()),
#         "type": typ,
#         "url": f"/uploads/{typ}/{filename}",
#         "duration": duration
#     }

#     playlists[device].append(item)
#     save_playlists()

#     # 🔴 Live push
#     if device in active_ws:
#         await active_ws[device].send_json(playlists[device])

#     return {
#         "status": "added",
#         "total_items": len(playlists[device])
#     }

# # ================= UPDATE DURATION =================
# @app.post("/api/playlist/update-duration")
# async def update_duration(data: dict):
#     device = data["deviceId"]
#     item_id = data["itemId"]
#     duration = data["duration"]

#     if device not in playlists:
#         return {"error": "Device not found"}

#     for item in playlists[device]:
#         if item["id"] == item_id:
#             item["duration"] = duration
#             save_playlists()

#             if device in active_ws:
#                 await active_ws[device].send_json(playlists[device])

#             return {"status": "updated"}

#     return {"error": "Item not found"}

# # ================= REMOVE ONE ITEM =================
# @app.post("/api/playlist/remove")
# async def remove_item(data: dict):
#     device = data["deviceId"]
#     item_id = data["itemId"]

#     if device not in playlists:
#         return {"error": "Device not found"}

#     playlists[device] = [
#         item for item in playlists[device] if item["id"] != item_id
#     ]

#     save_playlists()

#     if device in active_ws:
#         await active_ws[device].send_json(playlists[device])

#     return {"status": "removed"}

# # ================= GET PLAYLIST =================
# @app.get("/api/playlist/{device}")
# def get_playlist(device: str):
#     return playlists.get(device, [])

# # ================= CLEAR PLAYLIST =================
# @app.post("/api/playlist/clear")
# async def clear_playlist(data: dict):
#     device = data["deviceId"]
#     playlists[device] = []
#     save_playlists()

#     if device in active_ws:
#         await active_ws[device].send_json([])

#     return {"status": "cleared"}

# # ================= WEBSOCKET =================
# @app.websocket("/ws/{device}")
# async def websocket_endpoint(ws: WebSocket, device: str):
#     await ws.accept()
#     active_ws[device] = ws

#     # 🔥 send stored playlist on connect
#     if device in playlists:
#         await ws.send_json(playlists[device])

#     try:
#         while True:
#             await ws.receive_text()
#     except WebSocketDisconnect:
#         if device in active_ws:
#             del active_ws[device]








































from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil, os, time, json, uuid

app = FastAPI()

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= CONSTANTS =================
PLAYLIST_FILE = "playlist_data.json"

# ================= HELPERS =================
def load_playlists():
    if os.path.exists(PLAYLIST_FILE):
        with open(PLAYLIST_FILE, "r") as f:
            return json.load(f)
    return {}

def save_playlists():
    with open(PLAYLIST_FILE, "w") as f:
        json.dump(playlists, f, indent=2)

# ================= FOLDERS =================
os.makedirs("uploads/images", exist_ok=True)
os.makedirs("uploads/videos", exist_ok=True)
os.makedirs("uploads/pdfs", exist_ok=True)
os.makedirs("player", exist_ok=True)

# ================= STATIC =================
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/player", StaticFiles(directory="player"), name="player")

# ================= DATA =================
playlists = load_playlists()     # persistent playlist
active_ws = {}                   # deviceId → websocket

# ================= UPLOAD =================
@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1].lower()

    if ext in ["jpg", "jpeg", "png", "gif"]:
        folder, typ = "uploads/images", "images"
    elif ext in ["mp4", "mkv", "avi"]:
        folder, typ = "uploads/videos", "videos"
    elif ext == "pdf":
        folder, typ = "uploads/pdfs", "pdfs"
    else:
        return {"error": "Unsupported file type"}

    filename = f"{int(time.time()*1000)}_{file.filename}"
    path = os.path.join(folder, filename)

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {
        "filename": filename,
        "type": typ,
        "url": f"/uploads/{typ}/{filename}"
    }

# ================= ADD PLAYLIST ITEM =================
@app.post("/api/playlist/add")
async def add_playlist(data: dict):
    device = data["deviceId"]
    filename = data["filename"]
    typ = data["type"]
    duration = data.get("duration", 10)

    if device not in playlists:
        playlists[device] = []

    item = {
        "id": str(uuid.uuid4()),
        "type": typ,
        "url": f"/uploads/{typ}/{filename}",
        "duration": duration,
        "show_count": 0      # 🔥 COUNT FIELD
    }

    playlists[device].append(item)
    save_playlists()

    if device in active_ws:
        await active_ws[device].send_json(playlists[device])

    return {
        "status": "added",
        "total_items": len(playlists[device])
    }

# ================= UPDATE DURATION =================
@app.post("/api/playlist/update-duration")
async def update_duration(data: dict):
    device = data["deviceId"]
    item_id = data["itemId"]
    duration = data["duration"]

    if device not in playlists:
        return {"error": "Device not found"}

    for item in playlists[device]:
        if item["id"] == item_id:
            item["duration"] = duration
            save_playlists()

            if device in active_ws:
                await active_ws[device].send_json(playlists[device])

            return {"status": "updated"}

    return {"error": "Item not found"}

# ================= REMOVE ONE ITEM =================
@app.post("/api/playlist/remove")
async def remove_item(data: dict):
    device = data["deviceId"]
    item_id = data["itemId"]

    if device not in playlists:
        return {"error": "Device not found"}

    playlists[device] = [
        item for item in playlists[device] if item["id"] != item_id
    ]

    save_playlists()

    if device in active_ws:
        await active_ws[device].send_json(playlists[device])

    return {"status": "removed"}

# ================= CLEAR PLAYLIST =================
@app.post("/api/playlist/clear")
async def clear_playlist(data: dict):
    device = data["deviceId"]
    playlists[device] = []
    save_playlists()

    if device in active_ws:
        await active_ws[device].send_json([])

    return {"status": "cleared"}

# ================= GET PLAYLIST =================
@app.get("/api/playlist/{device}")
def get_playlist(device: str):
    return playlists.get(device, [])

# ================= INCREMENT SHOW COUNT =================
@app.post("/api/playlist/increment-show")
async def increment_show(data: dict):
    device = data["deviceId"]
    item_id = data["itemId"]

    if device not in playlists:
        return {"error": "Device not found"}

    for item in playlists[device]:
        if item["id"] == item_id:
            if "show_count" not in item:
                item["show_count"] = 0

            item["show_count"] += 1
            save_playlists()

            return {
                "status": "ok",
                "itemId": item_id,
                "show_count": item["show_count"]
            }

    return {"error": "Item not found"}


# ================= WEBSOCKET =================
@app.websocket("/ws/{device}")
async def websocket_endpoint(ws: WebSocket, device: str):
    await ws.accept()
    active_ws[device] = ws

    if device in playlists:
        await ws.send_json(playlists[device])

    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        if device in active_ws:
            del active_ws[device]
