import sys
import socket
import threading
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth_routes import router as auth_router
from app.api.profiles_routes import router as profiles_router
from app.api.referti_routes import router as referti_router
from app.api.analytics_routes import router as analytics_router
from app.api.chat_routes import router as chat_router
from app.api.settings_routes import router as settings_router
from app.api.export_routes import router as export_router
from app.api.updater_routes import router as updater_router
from app.api.mcp_routes import router as mcp_router
from app.api.fertility_routes import router as fertility_router
from app.config.settings import ensure_directories_exist

def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

app = FastAPI(
    title="Anamnesix API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(profiles_router)
app.include_router(referti_router)
app.include_router(analytics_router)
app.include_router(chat_router)
app.include_router(settings_router)
app.include_router(export_router)
app.include_router(updater_router)
app.include_router(mcp_router)
app.include_router(fertility_router)

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    frontend_path = Path(sys._MEIPASS) / "frontend"
else:
    frontend_path = Path(__file__).resolve().parent.parent / "frontend"

if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")

def start_backend_server(host: str, port: int) -> None:
    ensure_directories_exist()
    uvicorn.run(app, host=host, port=port, log_level="warning")

def launch_desktop() -> None:
    port = find_free_port()
    host = "127.0.0.1"

    server_thread = threading.Thread(
        target=start_backend_server,
        args=(host, port),
        daemon=True
    )
    server_thread.start()

    url = f"http://{host}:{port}/index.html"

    try:
        import webview
        webview.create_window(
            title="Anamnesix - Cartella Clinica Intelligente",
            url=url,
            width=1440,
            height=920,
            min_size=(1024, 700),
            text_select=True
        )
        webview.start()
    except Exception:
        import webbrowser
        webbrowser.open(url)
        server_thread.join()

if __name__ == "__main__":
    launch_desktop()
