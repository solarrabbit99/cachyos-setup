#!/usr/bin/env python3
import configparser
import subprocess
import os
from pathlib import Path

def get_active_engine():
    try:
        return subprocess.check_output(["fcitx5-remote", "-n"], encoding="utf-8").strip()
    except subprocess.CalledProcessError:
        return None

def get_data_dirs():
    dirs = []
    # user data dir
    xdg_data_home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    dirs.append(xdg_data_home / "fcitx5" / "inputmethod")
    # system dirs
    xdg_data_dirs = os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share")
    for d in xdg_data_dirs.split(":"):
        dirs.append(Path(d) / "fcitx5" / "inputmethod")
    return dirs

def find_conf_file(engine_id):
    for d in get_data_dirs():
        conf_file = d / f"{engine_id}.conf"
        if conf_file.exists():
            return conf_file
    return None

def get_label(conf_file):
    parser = configparser.ConfigParser(strict=False)
    parser.read(conf_file, encoding="utf-8")
    if parser.has_section("InputMethod") and parser.has_option("InputMethod", "Label"):
        return parser.get("InputMethod", "Label")
    return None

def main():
    engine = get_active_engine()
    if not engine:
        print("×", flush=True)
        return
    conf = find_conf_file(engine)
    if not conf:
        print("EN", flush=True) # default IM
        return
    label = get_label(conf)
    if label:
        print(label, flush=True)

if __name__ == "__main__":
    main()

