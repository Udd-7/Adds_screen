const express = require("express");
const multer = require("multer");
const cors = require("cors");
const path = require("path");
const fs = require("fs");

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static("public"));


// =========================
// Ensure upload folders exist
// =========================
["uploads/videos", "uploads/images", "uploads/pdfs", "uploads/temp"].forEach(dir => {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
});

// =========================
// Serve uploaded files
// =========================
app.use("/uploads", express.static("uploads"));

// =========================
// Multer Storage Logic
// =========================
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase();
    let folder = "uploads/temp";

    if ([".mp4", ".mkv", ".avi"].includes(ext)) folder = "uploads/videos";
    else if ([".jpg", ".jpeg", ".png", ".gif"].includes(ext)) folder = "uploads/images";
    else if ([".pdf"].includes(ext)) folder = "uploads/pdfs";

    cb(null, folder);
  },

  filename: (req, file, cb) => {
    const unique = Date.now() + "-" + file.originalname.replace(/\s+/g, "_");
    cb(null, unique);
  }
});

const upload = multer({ storage });

// =========================
// Upload API
// =========================
app.post("/api/upload", upload.single("file"), (req, res) => {
  if (!req.file) return res.status(400).json({ error: "No file uploaded" });

  res.json({
    status: "success",
    filename: req.file.filename,
    type: path.extname(req.file.filename).toLowerCase(),
    url: `http://localhost:5000/${req.file.path.replace(/\\/g, "/")}`
  });
});

// =========================
// List all uploaded files
// =========================
app.get("/api/files", (req, res) => {
  const videos = fs.readdirSync("uploads/videos");
  const images = fs.readdirSync("uploads/images");
  const pdfs = fs.readdirSync("uploads/pdfs");

  res.json({ videos, images, pdfs });
});

// =========================
// Device Register
// =========================
let devices = {};

app.post("/api/register", (req, res) => {
  const { deviceId } = req.body;
  if (!deviceId) return res.status(400).json({ error: "deviceId required" });

  devices[deviceId] = { lastSeen: Date.now() };
  res.json({ status: "registered", deviceId });
});

// =========================
// Playlist System
// =========================
let playlists = {};

// Add media to playlist
app.post("/api/playlist/add", (req, res) => {
  const { deviceId, filename, type } = req.body;

  if (!deviceId || !filename || !type) {
    return res.status(400).json({ error: "Missing deviceId, filename or type" });
  }

  if (!playlists[deviceId]) playlists[deviceId] = [];

  playlists[deviceId].push({
    type,
    url: `http://localhost:5000/uploads/${type}/${filename}`
  });

  res.json({ status: "added", playlist: playlists[deviceId] });
});

// Get playlist for a device
app.get("/api/playlist/:deviceId", (req, res) => {
  res.json(playlists[req.params.deviceId] || []);
});

// =========================
// Start Server
// =========================
app.listen(5000, () => console.log("🚀 Smart Signage Server running on port 5000"));
