"""
scripts/capture_ui_screenshots.py
Automates starting the FastAPI backend and Next.js frontend,
then uses Playwright with Microsoft Edge to capture pixel-perfect,
high-resolution UI screenshots of all key KRISHI Intelligence pages
for academic project report Chapter 4 and presentation viva slides.
"""

import os
import sys
import time
import subprocess
import urllib.request
from playwright.sync_api import sync_playwright

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "docs", "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PYTHON_EXE = sys.executable
FRONTEND_DIR = os.path.join(WORKSPACE_DIR, "frontend")
FARM_ID = "514da77c-6548-43a5-ab8b-26237a58ee74" # Verified Lucknow Wheat Farm in krishi.db


def wait_for_url(url, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False


def capture_all():
    print("Step 1: Starting FastAPI Backend on port 8000...")
    backend_proc = subprocess.Popen(
        [PYTHON_EXE, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=WORKSPACE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    print("Step 2: Starting Next.js Production Server on port 3000...")
    frontend_proc = subprocess.Popen(
        ["npm.cmd", "start"],
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    try:
        print("Waiting for Backend (http://127.0.0.1:8000/docs)...")
        if not wait_for_url("http://127.0.0.1:8000/docs", timeout=25):
            raise RuntimeError("Backend failed to start on port 8000")
        print("Backend is LIVE!")

        print("Waiting for Frontend (http://127.0.0.1:3000)...")
        if not wait_for_url("http://127.0.0.1:3000", timeout=35):
            raise RuntimeError("Frontend failed to start on port 3000")
        print("Frontend is LIVE!")

        pages_to_capture = [
            (
                f"http://127.0.0.1:3000/farm/{FARM_ID}",
                "fig_4_1_ui_dashboard.png",
                "Farm Executive Dashboard with Telemetry Meters & Risk Scores"
            ),
            (
                f"http://127.0.0.1:3000/farm/{FARM_ID}/digital-twin",
                "fig_4_2_ui_digital_twin.png",
                "Living Farm Digital Twin with GDD Phenology & Stress Vectors"
            ),
            (
                f"http://127.0.0.1:3000/farm/{FARM_ID}/market",
                "fig_4_3_ui_market.png",
                "Market Intelligence with XGBoost 30-Day Forecast & Sell/Hold Advisory"
            ),
            (
                f"http://127.0.0.1:3000/farm/{FARM_ID}/soil",
                "fig_4_4_ui_soil.png",
                "Granular Soil Intelligence Center & OCR Confirmation Gate"
            ),
            (
                f"http://127.0.0.1:3000/farm/{FARM_ID}/decision",
                "fig_4_5_ui_decision.png",
                "Multi-Factor Decision Center with Prioritized Action Cards"
            ),
            (
                f"http://127.0.0.1:3000/farm/{FARM_ID}/weather",
                "fig_4_6_ui_weather.png",
                "Agro-Meteorological Radar & Precipitation Risk Forecast"
            ),
        ]

        print("Step 3: Launching Playwright with Edge browser...")
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="msedge", headless=True)
            context = browser.new_context(
                viewport={"width": 1440, "height": 900},
                device_scale_factor=1.5
            )
            page = context.new_page()

            for url, filename, desc in pages_to_capture:
                print(f"Navigating to {url} ({desc})...")
                page.goto(url, wait_until="networkidle", timeout=30000)
                # Allow any client hydration or animations to settle
                time.sleep(2.5)

                out_path = os.path.join(OUTPUT_DIR, filename)
                page.screenshot(path=out_path, full_page=False)
                print(f"  [SAVED] {out_path} ({os.path.getsize(out_path)} bytes)")

            browser.close()
            print("All screenshots successfully captured!")

    finally:
        print("Cleaning up background servers...")
        try:
            backend_proc.terminate()
            backend_proc.kill()
        except Exception:
            pass
        try:
            frontend_proc.terminate()
            frontend_proc.kill()
            # On windows npm start spawns node, let's ensure port 3000 & 8000 are freed
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(frontend_proc.pid)], capture_output=True)
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(backend_proc.pid)], capture_output=True)
        except Exception:
            pass
        print("Cleanup complete.")


if __name__ == "__main__":
    capture_all()
