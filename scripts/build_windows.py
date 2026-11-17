import os
import sys
import subprocess
from pathlib import Path

def build():
    root_dir = Path(__file__).resolve().parent.parent
    dist_dir = root_dir / "dist"
    build_dir = root_dir / "build"
    main_script = root_dir / "app" / "main.py"
    frontend_dir = root_dir / "frontend"

    dist_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--name=Anamnesix",
        "--onefile",
        "--windowed",
        f"--add-data={frontend_dir}{os.pathsep}frontend",
        "--collect-all=app",
        "--collect-all=uvicorn",
        "--collect-all=fastapi",
        "--collect-all=starlette",
        "--collect-all=multipart",
        "--collect-all=argon2",
        "--collect-all=cryptography",
        "--collect-all=reportlab",
        "--collect-all=pydantic",
        "--hidden-import=uvicorn.logging",
        "--hidden-import=uvicorn.loops",
        "--hidden-import=uvicorn.loops.auto",
        "--hidden-import=uvicorn.protocols",
        "--hidden-import=uvicorn.protocols.http",
        "--hidden-import=uvicorn.protocols.http.auto",
        "--hidden-import=uvicorn.protocols.websockets",
        "--hidden-import=uvicorn.protocols.websockets.auto",
        "--hidden-import=uvicorn.lifespan",
        "--hidden-import=uvicorn.lifespan.on",
        "--hidden-import=cryptography",
        "--hidden-import=argon2",
        "--hidden-import=reportlab",
        "--hidden-import=pypdf",
        "--hidden-import=cv2",
        "--hidden-import=pytesseract",
        "--hidden-import=fitz",
        "--hidden-import=multipart",
        "--hidden-import=python_multipart",
        "--hidden-import=app.api.body_composition_routes",
        "--hidden-import=app.api.health_metrics_routes",
        "--hidden-import=app.api.job_routes",
        "--hidden-import=app.api.fertility_routes",
        "--hidden-import=app.biomarkers.scanner",
        "--hidden-import=app.jobs.job_manager",
        "--hidden-import=app.imaging.image_analyzer",
        "--hidden-import=app.fertility.checkup_engine",
        "--hidden-import=app.fertility.report_generator",
        "--hidden-import=app.fertility.imaging_analyzer",
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
        str(main_script)
    ]

    subprocess.check_call(cmd, cwd=str(root_dir))

if __name__ == "__main__":
    build()
