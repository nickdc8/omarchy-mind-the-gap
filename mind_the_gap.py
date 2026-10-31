"""Mind the Gap: manually compact occupied numeric Hyprland workspaces."""
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys


def ctl(*args):
    return subprocess.check_output(["hyprctl", *args], text=True, timeout=5)


def plan(workspaces):
    # Named, special and persistent desktops are deliberately reserved.
    reserved = {w["id"] for w in workspaces if w["id"] > 0 and
                (w.get("ispersistent") or w["name"] != str(w["id"]))}
    occupied = sorted(w["id"] for w in workspaces if w["id"] > 0 and
                      w.get("windows", 0) and w["id"] not in reserved)
    result = {}
    target = 1
    for source in occupied:
        while target in reserved:
            target += 1
        if source != target:
            result[source] = target
        target += 1
    return result


def cascade():
    # Avoid moving windows between outputs. Resume automatically on one monitor.
    if len(json.loads(ctl("-j", "monitors"))) != 1:
        return
    mapping = plan(json.loads(ctl("-j", "workspaces")))
    if not mapping:
        return
    clients = json.loads(ctl("-j", "clients"))
    focused = json.loads(ctl("-j", "activewindow"))
    active = json.loads(ctl("-j", "activeworkspace"))["id"]
    commands = []
    for source, target in mapping.items():
        for client in clients:
            if client["workspace"]["id"] == source and not client.get("pinned", False):
                commands.append(f'dispatch hl.dsp.window.move({{workspace="{target}",window="address:{client["address"]}",follow=false}})')
    if active in mapping:
        commands.append(f'dispatch hl.dsp.focus({{workspace="{mapping[active]}"}})')
        if focused.get("address"):
            commands.append(f'dispatch hl.dsp.focus({{window="address:{focused["address"]}"}})')
    if commands:
        response = ctl("--batch", "; ".join(commands))
        if any(line.strip() != "ok" for line in response.splitlines() if line.strip()):
            raise RuntimeError(response)


def main():
    if "--status" in sys.argv:
        print(json.dumps(len(json.loads(ctl("-j", "monitors"))) == 1 and
                         bool(plan(json.loads(ctl("-j", "workspaces"))))))
        return
    runtime = Path(os.environ["XDG_RUNTIME_DIR"])
    with open(runtime / "mind-the-gap.lock", "w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        cascade()


if __name__ == "__main__":
    main()
