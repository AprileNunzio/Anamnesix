import os
import sys

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w", encoding="utf-8")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w", encoding="utf-8")
if sys.stdin is None:
    sys.stdin = open(os.devnull, "r", encoding="utf-8")

import socket
import threading
import time
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
from app.api.body_composition_routes import router as body_composition_router
from app.api.health_metrics_routes import router as health_metrics_router
from app.api.job_routes import router as job_router
from app.config.settings import ensure_directories_exist, BASE_DIR
from app.biomarkers.scanner import biomarker_auto_scanner

def find_free_port(start_port: int = 24680) -> int:
    for p in range(start_port, start_port + 100):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("127.0.0.1", p))
            s.close()
            return p
        except OSError:
            s.close()
            continue
    return 24680

def wait_for_server(host: str, port: int, timeout: float = 25.0) -> bool:
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=0.2):
                return True
        except OSError:
            time.sleep(0.1)
    return False

app = FastAPI(
    title="Anamnesix API Enterprise",
    version="1.1.3",
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
app.include_router(body_composition_router)
app.include_router(health_metrics_router)
app.include_router(job_router)

@app.on_event("startup")
def startup_event():
    ensure_directories_exist()
    try:
        biomarker_auto_scanner.scan_and_register_all()
    except Exception as err:
        log_file = BASE_DIR / "startup_error.log"
        log_file.write_text(str(err), encoding="utf-8")

user_docs_frontend = BASE_DIR / "frontend"
if user_docs_frontend.exists() and (user_docs_frontend / "index.html").exists():
    frontend_path = user_docs_frontend
elif getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    frontend_path = Path(sys._MEIPASS) / "frontend"
else:
    frontend_path = Path(__file__).resolve().parent.parent / "frontend"

if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")

server_error_log = []

def start_backend_server(host: str, port: int) -> None:
    ensure_directories_exist()
    try:
        config = uvicorn.Config(
            app,
            host=host,
            port=port,
            log_level="critical",
            log_config=None,
            access_log=False,
            loop="asyncio"
        )
        server = uvicorn.Server(config)
        server.run()
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        server_error_log.append(err_msg)
        crash_file = BASE_DIR / "server_crash.txt"
        crash_file.write_text(err_msg, encoding="utf-8")

def launch_desktop() -> None:
    host = "127.0.0.1"
    port = find_free_port()

    server_thread = threading.Thread(
        target=start_backend_server,
        args=(host, port),
        daemon=True
    )
    server_thread.start()

    is_ready = wait_for_server(host, port, timeout=30.0)

    try:
        import webview
        if is_ready:
            webview.create_window(
                title="Anamnesix Enterprise - Cartella Clinica Intelligente",
                url=f"http://{host}:{port}/index.html",
                width=1440,
                height=920,
                min_size=(1024, 700),
                text_select=True
            )
        else:
            err_detail = server_error_log[0] if server_error_log else "Timeout di connessione: il server ASGI locale non ha risposto entro 30 secondi sulla porta specificata."
            crash_file = BASE_DIR / "connection_error.txt"
            crash_file.write_text(err_detail, encoding="utf-8")
            error_html = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<title>Anamnesix Enterprise - Diagnostica Avvio</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; color: #0f172a; padding: 40px; margin: 0; }}
.card {{ background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 32px; max-width: 820px; margin: 0 auto; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
h2 {{ color: #dc2626; margin-top: 0; font-size: 22px; }}
p {{ font-size: 14px; color: #475569; line-height: 1.6; }}
pre {{ background: #0f172a; color: #f8fafc; padding: 18px; border-radius: 6px; font-size: 12px; overflow-x: auto; white-space: pre-wrap; }}
.btn {{ background: #0284c7; color: #ffffff; border: none; padding: 10px 24px; border-radius: 6px; font-weight: 600; cursor: pointer; text-decoration: none; display: inline-block; }}
.btn:hover {{ background: #0369a1; }}
</style>
</head>
<body>
<div class="card">
<h2>Anamnesix Enterprise - Inizializzazione Server Locale</h2>
<p>Il backend clinico locale su <strong>{host}:{port}</strong> non ha completato l'avvio entro 30 secondi.</p>
<p>Registro diagnostico rilevato:</p>
<pre>{err_detail}</pre>
<button class="btn" onclick="window.location.reload();">Ricarica Connessione</button>
</div>
</body>
</html>"""
            webview.create_window(
                title="Anamnesix Enterprise - Diagnostica Avvio",
                html=error_html,
                width=1000,
                height=650,
                min_size=(800, 500),
                text_select=True
            )
        webview.start()
    except Exception:
        import webbrowser
        if is_ready:
            webbrowser.open(f"http://{host}:{port}/index.html")
        server_thread.join()

if __name__ == "__main__":
    launch_desktop()
