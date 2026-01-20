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
# SCREENS_FILE deprecated

# ================= HELPERS =================
def load_playlists():
    data = {}
    if os.path.exists(PLAYLIST_FILE):
        with open(PLAYLIST_FILE, "r") as f:
            try:
                data = json.load(f)
            except:
                data = {}

    # MIGRATION/NORMALIZATION
    normalized_data = {}
    
    # Try to recover legacy location data if screens.json still exists
    legacy_locations = {}
    if os.path.exists("screens.json"):
        try:
            with open("screens.json", "r") as f:
                legacy_locations = json.load(f)
        except:
            pass

    for dev, content in data.items():
        if isinstance(content, list):
            # OLD Format: list of items. Recover location.
            loc = legacy_locations.get(dev, "Unknown Location")
            if len(content) > 0 and "location" in content[0]:
                loc = content[0]["location"] # Grab from first item if it was embedded
                
            normalized_data[dev] = {
                "location": loc,
                "items": content
            }
        elif isinstance(content, dict):
            # NEW Format: already nested
            normalized_data[dev] = content
        else:
            # Fallback
            normalized_data[dev] = {"location": "Unknown Location", "items": []}
            
    return normalized_data

def save_playlists():
    # Store directly in the nested format as requested
    with open(PLAYLIST_FILE, "w") as f:
        json.dump(playlists, f, indent=2)
    
    # Also keep screens.json updated for backward compatibility or metadata tools
    metadata = {dev: data.get("location", "Unknown Location") for dev, data in playlists.items()}
    with open("screens.json", "w") as f:
        json.dump(metadata, f, indent=2)

def try_delete_file(file_url):
    """Checks if file is used in any playlist. If not, deletes it."""
    is_used = False
    for dev, data in playlists.items():
        # Support both old list (during migration logic if needed) and new dict
        items = data if isinstance(data, list) else data.get("items", [])
        
        for item in items:
            if item["url"] == file_url:
                is_used = True
                break
        if is_used:
            break

    if not is_used:
        try:
            # Decode URL (e.g. %20 -> space)
            relative_path = unquote(file_url.lstrip("/"))
            file_path = relative_path.replace("/", os.sep)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"TRASH: Deleted unused file {file_path}")
        except Exception as e:
            print(f"ERROR: Could not delete {file_url}: {e}")

# ================= FOLDERS =================
os.makedirs("uploads/images", exist_ok=True)
os.makedirs("uploads/videos", exist_ok=True)
os.makedirs("uploads/pdfs", exist_ok=True)
os.makedirs("player", exist_ok=True)

# ================= STATIC =================
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/player", StaticFiles(directory="player"), name="player")


# ================= DATA =================
PLAYLIST_FILE = "playlist_data.json"
GROUPS_FILE = "groups.json"

def load_groups():
    if os.path.exists(GROUPS_FILE):
        try:
            with open(GROUPS_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_groups(groups_data):
    with open(GROUPS_FILE, "w") as f:
        json.dump(groups_data, f, indent=2)

playlists = load_playlists()     # persistent playlist (Single Source of Truth)
groups = load_groups()           # { groupName: ["SCREEN_1", ...] }
active_ws = {}                   # deviceId → websocket
emergency_state = None           # {type, content, style} or None
stream_state = None              # {url, targets: []} or None

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

# ================= LOGIN API =================
@app.post("/api/login")
async def login(data: dict):
    username = data.get("username")
    password = data.get("password")

    if username == "admin" and password == "Admin@123":
        return {"status": "ok", "token": "dummy-auth-token-123"}
    
    return {"error": "Invalid credentials", "status": "error"}

# ================= EMERGENCY API =================
@app.post("/api/emergency/active")
async def emergency_active(data: dict):
    global emergency_state
    emergency_state = data
    
    # Broadcast to ALL screens
    payload = {"event": "emergency", "data": emergency_state}
    for device, ws in active_ws.items():
        try:
            await ws.send_json(payload)
        except:
            pass
            
    return {"status": "active"}

@app.post("/api/emergency/clear")
async def emergency_clear():
    global emergency_state
    emergency_state = None
    
    # Broadcast Stop
    payload = {"event": "emergency_stop"}
    for device, ws in active_ws.items():
        try:
            await ws.send_json(payload)
        except:
            pass
            
    return {"status": "cleared"}

# ================= SCREEN MANAGEMENT API =================
@app.get("/api/screens")
def get_screens():
    # Construct screen list from playlists data
    result = {}
    for dev, data in playlists.items():
        result[dev] = {
            "id": dev,
            "location": data.get("location", "Unknown Location")
        }
    return result

@app.post("/api/screens/add")
async def add_screen(data: dict):
    # Expects: {"number": 1, "location": "Lobby"}
    try:
        num = int(data.get("number"))
        location = data.get("location", "Unknown Location")
        
        device_id = f"SCREEN_{num}"
        
        if device_id in playlists:
           return {"error": "Screen already exists", "status": "error"}
            
        playlists[device_id] = {
            "location": location,
            "items": []
        }
        save_playlists()
            
        return {"status": "ok", "device_id": device_id}
        
    except ValueError:
        return {"error": "Invalid screen number", "status": "error"}

@app.post("/api/screens/delete")
async def delete_screen(data: dict):
    device_id = data.get("deviceId")
    
    if device_id not in playlists:
        return {"error": "Screen not found", "status": "error"}
    
    del playlists[device_id]
    save_playlists()
    
    # Close WebSocket cleanup (simplified to avoid race conditions)
    # The player will naturally disconnect or just stop receiving updates
    if device_id in active_ws:
        try:
            # Just remove from active list, don't await close to prevent hanging
            # await active_ws[device_id].close() 
            del active_ws[device_id]
        except:
            pass
        
        
    return {"status": "deleted", "device_id": device_id}

# ================= GROUPS API =================
@app.get("/api/groups")
def get_groups():
    return groups

@app.post("/api/groups/add")
async def add_group(data: dict):
    name = data.get("name")
    devices = data.get("devices", [])
    
    if not name:
        return {"error": "Missing group name", "status": "error"}
    
    groups[name] = devices
    save_groups(groups)
    return {"status": "ok", "name": name}

@app.delete("/api/groups/{name}")
async def delete_group(name: str):
    if name in groups:
        del groups[name]
        save_groups(groups)
        return {"status": "ok"}
    return {"error": "Group not found", "status": "error"}

# ================= STREAM API =================
@app.get("/api/stream/status")
def get_stream_status():
    return stream_state

@app.post("/api/stream/start")
async def start_stream(data: dict):
    global stream_state
    stream_state = {
        "url": data.get("url"),
        "targets": data.get("targets", []) # empty means ALL
    }
    
    payload = {"event": "stream_start", "data": stream_state}
    
    # Broadcast
    for device, ws in active_ws.items():
        # If targets is empty, send to all. Otherwise only if in list.
        if not stream_state["targets"] or device in stream_state["targets"]:
            try:
                await ws.send_json(payload)
            except:
                pass
                
    return {"status": "started", "state": stream_state}

@app.post("/api/stream/stop")
async def stop_stream():
    global stream_state
    stream_state = None
    
    payload = {"event": "stream_stop"}
    for device, ws in active_ws.items():
        try:
            await ws.send_json(payload)
        except:
            pass
            
    return {"status": "stopped"}

# ================= ADD PLAYLIST ITEM =================
@app.post("/api/playlist/add")
async def add_playlist(data: dict):
    device = data["deviceId"]
    filename = data["filename"]
    typ = data["type"]
    duration = data.get("duration", 10)

    # STRICT VALIDATION: Screen must exist in our single-source-of-truth
    if device not in playlists:
        return {"error": "Device NOT registered. Please add screen first."}

    # Access the "items" list safely
    if "items" not in playlists[device]:
        playlists[device]["items"] = []

    item = {
        "id": str(uuid.uuid4()),
        "type": typ,
        "url": f"/uploads/{typ}/{filename}",
        "duration": duration,
        "show_count": 0
    }

    playlists[device]["items"].append(item)
    save_playlists()

    if device in active_ws:
        await active_ws[device].send_json(playlists[device]["items"])

    return {
        "status": "added",
        "total_items": len(playlists[device]["items"])
    }

# ================= UPDATE DURATION =================
@app.post("/api/playlist/update-duration")
async def update_duration(data: dict):
    device = data["deviceId"]
    item_id = data["itemId"]
    duration = data["duration"]

    if device not in playlists:
        return {"error": "Device not found"}
        
    items = playlists[device].get("items", [])

    for item in items:
        if item["id"] == item_id:
            item["duration"] = duration
            save_playlists()

            if device in active_ws:
                await active_ws[device].send_json(items)

            return {"status": "updated"}

    return {"error": "Item not found"}

# ================= REMOVE ONE ITEM =================
@app.post("/api/playlist/remove")
async def remove_item(data: dict):
    device = data["deviceId"]
    item_id = data["itemId"]

    if device not in playlists:
        return {"error": "Device not found"}

    items = playlists[device].get("items", [])
    
    # 1. Find the item to be removed
    item_to_remove = None
    for item in items:
        if item["id"] == item_id:
            item_to_remove = item
            break
    
    if not item_to_remove:
        return {"error": "Item not found"}

    # 2. Remove from playlist
    playlists[device]["items"] = [
        item for item in items if item["id"] != item_id
    ]
    save_playlists()

    # 3. Smart Delete Check
    try_delete_file(item_to_remove["url"])

    if device in active_ws:
        await active_ws[device].send_json(playlists[device]["items"])

    return {"status": "removed"}

# ================= CLEAR PLAYLIST =================
@app.post("/api/playlist/clear")
async def clear_playlist(data: dict):
    device = data["deviceId"]
    if device not in playlists:
         return {"error": "Device not found"}

    old_items = playlists[device].get("items", [])
    playlists[device]["items"] = []
    save_playlists()

    # Check deletion for all cleared items
    for item in old_items:
        try_delete_file(item["url"])

    if device in active_ws:
        await active_ws[device].send_json([])

    return {"status": "cleared"}

# ================= GET PLAYLIST =================
@app.get("/api/playlist/{device}")
def get_playlist(device: str):
    data = playlists.get(device, {})
    return data.get("items", [])

# ================= EXPORT ALL DATA =================
@app.get("/api/export")
def export_data():
    return playlists

# ================= INCREMENT SHOW COUNT =================
@app.post("/api/playlist/increment-show")
async def increment_show(data: dict):
    device = data["deviceId"]
    item_id = data["itemId"]

    if device not in playlists:
        return {"error": "Device not found"}

    items = playlists[device].get("items", [])
    
    for item in items:
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
        await ws.send_json(playlists[device].get("items", []))

    # 🔥 Send emergency state if active
    if emergency_state:
        await ws.send_json({"event": "emergency", "data": emergency_state})

    # 🔥 Send stream state if active
    if stream_state:
        if not stream_state["targets"] or device in stream_state["targets"]:
            await ws.send_json({"event": "stream_start", "data": stream_state})

    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        if device in active_ws:
            del active_ws[device]

# ================= STATIC (Catch-All) =================
# Must be at the end to avoid intercepting API/WS routes
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
