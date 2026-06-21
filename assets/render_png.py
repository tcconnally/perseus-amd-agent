#!/usr/bin/env python3
"""Render architecture diagram to PNG thumbnail."""
import os, threading, time
import http.server, socketserver
from pathlib import Path
from playwright.sync_api import sync_playwright

ASSETS_DIR = Path(__file__).resolve().parent
HTML_FILE = ASSETS_DIR / "architecture.html"
PNG_FILE = ASSETS_DIR / "thumbnail.png"

os.chdir(str(ASSETS_DIR))

# Start HTTP server (file:// won't execute fonts/JS in headless Chromium)
httpd = socketserver.TCPServer(("", 9879), http.server.SimpleHTTPRequestHandler)
t = threading.Thread(target=httpd.serve_forever, daemon=True)
t.start()
print("HTTP server on :9879")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 1050})
    page.goto("http://localhost:9879/architecture.html", wait_until="domcontentloaded", timeout=15000)
    time.sleep(2)  # Let fonts render
    page.screenshot(path=str(PNG_FILE), full_page=True)
    browser.close()
    httpd.shutdown()

size_kb = PNG_FILE.stat().st_size / 1024
print(f"[OK] Thumbnail: {PNG_FILE} ({size_kb:.0f} KB)")

# Verify PNG
with open(PNG_FILE, 'rb') as f:
    header = f.read(8)
    assert header[:4] == b'\x89PNG', "Invalid PNG header"
    print(f"   Valid PNG — {size_kb:.0f} KB")
