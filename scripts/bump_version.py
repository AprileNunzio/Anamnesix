import re
import sys
import argparse
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT_DIR / "VERSION"
SETTINGS_FILE = ROOT_DIR / "app" / "config" / "settings.py"
MAIN_FILE = ROOT_DIR / "app" / "main.py"
ISS_FILE = ROOT_DIR / "scripts" / "installer.iss"

def parse_semver_tuple(ver_str: str):
    clean = ver_str.strip().lstrip("v")
    parts = clean.split(".")
    major = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else 1
    minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    patch = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
    return (major, minor, patch)

def format_semver_tuple(tpl) -> str:
    return f"{tpl[0]}.{tpl[1]}.{tpl[2]}"

def get_current_file_version() -> tuple:
    if VERSION_FILE.exists():
        content = VERSION_FILE.read_text(encoding="utf-8").strip()
        if content:
            return parse_semver_tuple(content)
    return (1, 1, 1)

def get_highest_git_tag_version() -> tuple:
    tags = []
    try:
        out = subprocess.check_output(["git", "tag", "--sort=-v:refname"], stderr=subprocess.DEVNULL).decode("utf-8")
        for line in out.splitlines():
            s = line.strip().lstrip("v")
            parts = s.split(".")
            if len(parts) == 3 and all(p.isdigit() for p in parts):
                tags.append(tuple(int(p) for p in parts))
    except Exception:
        return (1, 0, 0)
    return max(tags) if tags else (1, 0, 0)

def get_highest_known_version() -> tuple:
    f_ver = get_current_file_version()
    g_ver = get_highest_git_tag_version()
    return max(f_ver, g_ver)

def increment_tuple(base_tuple: tuple, part: str = "patch") -> tuple:
    major, minor, patch = base_tuple
    if part == "major":
        return (major + 1, 0, 0)
    if part == "minor":
        return (major, minor + 1, 0)
    return (major, minor, patch + 1)

def sync_version_in_files(new_ver: str) -> None:
    clean_ver = new_ver.strip().lstrip("v")
    VERSION_FILE.write_text(f"{clean_ver}\n", encoding="utf-8")

    if SETTINGS_FILE.exists():
        txt = SETTINGS_FILE.read_text(encoding="utf-8")
        txt = re.sub(r'APP_VERSION\s*=\s*"[^"]*"', f'APP_VERSION = "{clean_ver}"', txt)
        SETTINGS_FILE.write_text(txt, encoding="utf-8")

    if MAIN_FILE.exists():
        txt = MAIN_FILE.read_text(encoding="utf-8")
        txt = re.sub(r'version="[^"]*"', f'version="{clean_ver}"', txt)
        MAIN_FILE.write_text(txt, encoding="utf-8")

    if ISS_FILE.exists():
        txt = ISS_FILE.read_text(encoding="utf-8")
        txt = re.sub(r'AppVersion=[^\r\n]*', f'AppVersion={clean_ver}', txt)
        txt = re.sub(r'#define\s+MyAppVersion\s+"[^"]*"', f'#define MyAppVersion "{clean_ver}"', txt)
        ISS_FILE.write_text(txt, encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--get", action="store_true")
    parser.add_argument("--next", action="store_true")
    parser.add_argument("--tag", action="store_true")
    parser.add_argument("--bump", choices=["patch", "minor", "major"], default=None)
    parser.add_argument("--set", dest="set_ver", type=str, default=None)
    args = parser.parse_args()

    if args.get:
        curr = format_semver_tuple(get_current_file_version())
        sys.stdout.write(f"v{curr}\n" if args.tag else f"{curr}\n")
        return

    if args.set_ver:
        target = args.set_ver.strip().lstrip("v")
        sync_version_in_files(target)
        sys.stdout.write(f"v{target}\n" if args.tag else f"{target}\n")
        return

    if args.next:
        highest = get_highest_known_version()
        next_ver_tuple = increment_tuple(highest, "patch")
        next_ver_str = format_semver_tuple(next_ver_tuple)
        sync_version_in_files(next_ver_str)
        sys.stdout.write(f"v{next_ver_str}\n" if args.tag else f"{next_ver_str}\n")
        return

    bump_part = args.bump if args.bump else "patch"
    curr_file = get_current_file_version()
    new_ver_tuple = increment_tuple(curr_file, bump_part)
    new_ver_str = format_semver_tuple(new_ver_tuple)
    sync_version_in_files(new_ver_str)
    sys.stdout.write(f"v{new_ver_str}\n" if args.tag else f"{new_ver_str}\n")

if __name__ == "__main__":
    main()
