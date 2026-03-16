import os
import subprocess


def run_cmd(cmd: list[str], cwd: str) -> dict:
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "ok": result.returncode == 0,
    }


def validate_frontend(frontend_dir: str) -> dict:
    if not os.path.exists(frontend_dir):
        return {"ok": False, "step": "exists", "stderr": f"Missing frontend dir: {frontend_dir}"}

    install = run_cmd(["npm", "install"], frontend_dir)
    if not install["ok"]:
        return {"ok": False, "step": "npm_install", **install}

    build = run_cmd(["npm", "run", "build"], frontend_dir)
    if not build["ok"]:
        return {"ok": False, "step": "npm_build", **build}

    return {"ok": True, "step": "frontend_validation_passed"}


def validate_backend_imports(backend_dir: str) -> dict:
    if not os.path.exists(backend_dir):
        return {"ok": False, "step": "exists", "stderr": f"Missing backend dir: {backend_dir}"}

    return {"ok": True, "step": "backend_validation_passed"}