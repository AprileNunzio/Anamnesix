import os
import sys
import json
import io
import zipfile
import subprocess
import httpx
from pathlib import Path
from typing import Dict, Any, Optional
from app.config.settings import CONFIG_DIR, BASE_DIR, GITHUB_REPO, ensure_directories_exist

VERSION_FILE_PATH = CONFIG_DIR / "version.json"

class GitHubAutoUpdater:
    def __init__(self, repo: str = GITHUB_REPO):
        self.repo = repo
        self.api_url = f"https://api.github.com/repos/{self.repo}/commits/main"
        self.archive_url = f"https://api.github.com/repos/{self.repo}/zipball/main"
        self.release_url = f"https://api.github.com/repos/{self.repo}/releases/latest"

    def get_local_commit(self) -> Dict[str, Any]:
        ensure_directories_exist()
        if VERSION_FILE_PATH.exists():
            try:
                return json.loads(VERSION_FILE_PATH.read_text(encoding="utf-8"))
            except Exception:
                return {"sha": "initial", "date": "", "message": ""}
        return {"sha": "initial", "date": "", "message": ""}

    def save_local_commit(self, sha: str, date: str, message: str) -> None:
        ensure_directories_exist()
        payload = {"sha": sha, "date": date, "message": message}
        VERSION_FILE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    async def check_for_updates(self) -> Dict[str, Any]:
        local_info = self.get_local_commit()
        headers = {"User-Agent": "Anamnesix-Desktop-Updater"}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(self.api_url, headers=headers)
                if res.status_code == 200:
                    commit_data = res.json()
                    remote_sha = commit_data.get("sha", "")
                    commit_msg = commit_data.get("commit", {}).get("message", "")
                    commit_date = commit_data.get("commit", {}).get("committer", {}).get("date", "")

                    has_update = (remote_sha != local_info.get("sha")) and (local_info.get("sha") != "initial" or remote_sha != "")
                    return {
                        "has_update": has_update,
                        "current_sha": local_info.get("sha"),
                        "remote_sha": remote_sha,
                        "message": commit_msg,
                        "date": commit_date
                    }
                return {
                    "has_update": False,
                    "error": f"Codice di risposta GitHub {res.status_code}"
                }
        except Exception as e:
            return {
                "has_update": False,
                "error": str(e)
            }

    async def apply_update(self, target_dir: Optional[Path] = None) -> bool:
        if target_dir is None:
            if getattr(sys, "frozen", False):
                target_dir = BASE_DIR / "app_runtime"
            else:
                target_dir = Path(__file__).resolve().parent.parent.parent

        headers = {"User-Agent": "Anamnesix-Desktop-Updater"}
        check = await self.check_for_updates()
        if not check.get("remote_sha"):
            return False

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.get(self.archive_url, headers=headers, follow_redirects=True)
                if res.status_code != 200:
                    return False

                user_frontend_dir = BASE_DIR / "frontend"
                user_frontend_dir.mkdir(parents=True, exist_ok=True)

                zip_buffer = io.BytesIO(res.content)
                with zipfile.ZipFile(zip_buffer) as zf:
                    root_folder = zf.namelist()[0].split("/")[0]
                    for member in zf.namelist():
                        if member.endswith("/"):
                            continue
                        rel_path = member[len(root_folder) + 1:]
                        if not rel_path or rel_path.startswith(".git"):
                            continue
                        dest_file = target_dir / rel_path
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        dest_file.write_bytes(zf.read(member))

                        if rel_path.startswith("frontend/"):
                            f_sub = rel_path[len("frontend/"):]
                            f_dest = user_frontend_dir / f_sub
                            f_dest.parent.mkdir(parents=True, exist_ok=True)
                            f_dest.write_bytes(zf.read(member))

                self.save_local_commit(
                    sha=check.get("remote_sha", ""),
                    date=check.get("date", ""),
                    message=check.get("message", "")
                )
                return True
        except Exception:
            return False

    def restart_application(self) -> None:
        if sys.platform == "win32":
            bat_path = BASE_DIR / "restart.bat"
            exe_path = sys.executable
            bat_content = f"""@echo off
timeout /t 2 /nobreak >nul
start "" "{exe_path}"
del "%~f0"
exit
"""
            bat_path.write_text(bat_content, encoding="utf-8")
            creation_flags = 0x08000000 | 0x00000200
            subprocess.Popen(["cmd.exe", "/c", str(bat_path)], creationflags=creation_flags, close_fds=True)
            os._exit(0)
        else:
            subprocess.Popen([sys.executable] + sys.argv, close_fds=True)
            os._exit(0)

github_updater = GitHubAutoUpdater()
