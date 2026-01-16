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







































from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import time

app = FastAPI()

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= FOLDERS =================
os.makedirs("uploads/images", exist_ok=True)
os.makedirs("uploads/videos", exist_ok=True)
os.makedirs("uploads/pdfs", exist_ok=True)
os.makedirs("player", exist_ok=True)

# ================= STATIC =================
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/player", StaticFiles(directory="player"), name="player")

# ================= IN-MEMORY =================
playlists = {}      # { deviceId: [ {type,url}, ... ] }
active_ws = {}      # { deviceId: websocket }

# ================= UPLOAD =================
@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1].lower()

    if ext in ["jpg", "jpeg", "png", "gif"]:
        folder = "uploads/images"
        typ = "images"
    elif ext in ["mp4", "mkv", "avi"]:
        folder = "uploads/videos"
        typ = "videos"
    elif ext == "pdf":
        folder = "uploads/pdfs"
        typ = "pdfs"
    else:
        return {"error": "Unsupported file type"}

    filename = f"{int(time.time()*1000)}_{file.filename}"
    path = os.path.join(folder, filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": filename,
        "type": typ,
        "url": f"/uploads/{typ}/{filename}"
    }

# ================= ADD TO PLAYLIST =================
@app.post("/api/playlist/add")
async def add_playlist(data: dict):
    device = data["deviceId"]
    filename = data["filename"]
    typ = data["type"]

    if device not in playlists:
        playlists[device] = []

    item = {
        "type": typ,
        "url": f"/uploads/{typ}/{filename}"
    }

    # 🔒 Prevent duplicate items
    if item not in playlists[device]:
        playlists[device].append(item)

    # 🔥 Push FULL playlist (append-safe)
    if device in active_ws:
        await active_ws[device].send_json(playlists[device])

    return {
        "status": "added",
        "device": device,
        "total_items": len(playlists[device])
    }

# ================= GET PLAYLIST =================
@app.get("/api/playlist/{device}")
def get_playlist(device: str):
    return playlists.get(device, [])

# ================= CLEAR PLAYLIST (OPTIONAL) =================
@app.post("/api/playlist/clear")
async def clear_playlist(data: dict):
    device = data["deviceId"]
    playlists[device] = []

    if device in active_ws:
        await active_ws[device].send_json([])

    return {"status": "cleared", "device": device}

# ================= WEBSOCKET =================
@app.websocket("/ws/{device}")
async def websocket_endpoint(ws: WebSocket, device: str):
    await ws.accept()
    active_ws[device] = ws
    print("Screen connected:", device)

    # Send existing playlist once
    if device in playlists:
        await ws.send_json(playlists[device])

    try:
        while True:
            await ws.receive_text()  # keep alive
    except WebSocketDisconnect:
        if device in active_ws:
            del active_ws[device]
        print("Screen disconnected:", device)
