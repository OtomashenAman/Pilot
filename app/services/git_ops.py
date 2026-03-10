import os
import subprocess


def run_git(cmd: list[str], repo_path: str) -> str:
    result = subprocess.run(
        cmd,
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _has_origin(repo_path: str) -> bool:
    try:
        out = run_git(["git", "remote"], repo_path)
        return "origin" in out.split()
    except Exception:
        return False


def ensure_git_identity(repo_path: str):
    try:
        run_git(["git", "config", "--global", "--add", "safe.directory", repo_path], repo_path)
    except Exception:
        pass

    try:
        run_git(["git", "config", "user.name"], repo_path)
    except subprocess.CalledProcessError:
        run_git(["git", "config", "user.name", "AI Builder"], repo_path)

    try:
        run_git(["git", "config", "user.email"], repo_path)
    except subprocess.CalledProcessError:
        run_git(["git", "config", "user.email", "ai-builder@example.com"], repo_path)


def set_authenticated_remote(repo_path: str):
    token = os.environ["GITHUB_TOKEN"]
    owner = os.environ["GITHUB_OWNER"]
    repo = os.environ["GITHUB_REPO"]

    remote_url = f"https://{token}@github.com/{owner}/{repo}.git"

    if _has_origin(repo_path):
        run_git(["git", "remote", "remove", "origin"], repo_path)

    run_git(["git", "remote", "add", "origin", remote_url], repo_path)


def checkout_base_branch(repo_path: str, base_branch: str):
    run_git(["git", "checkout", base_branch], repo_path)
    run_git(["git", "pull", "origin", base_branch], repo_path)


def create_branch(repo_path: str, branch_name: str):
    run_git(["git", "checkout", "-b", branch_name], repo_path)


def add_commit_push(repo_path: str, commit_message: str, branch_name: str):
    run_git(["git", "add", "."], repo_path)

    status = run_git(["git", "status", "--porcelain"], repo_path)
    if not status.strip():
        return "no_changes"

    run_git(["git", "commit", "-m", commit_message], repo_path)
    run_git(["git", "push", "-u", "origin", branch_name], repo_path)
    return "pushed"