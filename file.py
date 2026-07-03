import os
import subprocess
import sys

TOKEN = os.environ.get("GITHUB_TOKEN")
if not TOKEN:
    print("ERROR: Set GITHUB_TOKEN environment variable with your GitHub personal access token")
    sys.exit(1)

REPO_URL = f"https://{TOKEN}@github.com/GHAIThMsON/testing-my-for-github.git"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def run(cmd, cwd=None):
    result = subprocess.run(cmd, cwd=cwd or SCRIPT_DIR, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running {' '.join(cmd)}:\n{result.stderr.strip()}")
        sys.exit(1)
    return result.stdout.strip()


def main():
    os.chdir(SCRIPT_DIR)
    files = [d for d in os.listdir(SCRIPT_DIR)
             if os.path.isfile(os.path.join(SCRIPT_DIR, d)) and not d.startswith(".") and d != os.path.basename(__file__)]

    if not files:
        print("No files found to upload.")
        return

    print(f"Found files: {', '.join(files)}")

    if not os.path.exists(os.path.join(SCRIPT_DIR, ".git")):
        run(["git", "init", "-b", "main"])

    try:
        run(["git", "remote", "get-url", "origin"])
    except SystemExit:
        run(["git", "remote", "add", "origin", REPO_URL])

    try:
        run(["git", "config", "user.email"])
    except SystemExit:
        run(["git", "config", "user.email", "bot@uploader.local"])
        run(["git", "config", "user.name", "UploadBot"])

    run(["git", "fetch", "origin"])
    try:
        run(["git", "rev-parse", "origin/main"])
        run(["git", "reset", "origin/main"])
    except SystemExit:
        pass

    run(["git", "add", "-A"])
    run(["git", "commit", "--allow-empty", "-m", "Upload files to repo"])

    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if branch != "main":
        run(["git", "branch", "-m", "main"])

    print("Pushing to remote...")
    run(["git", "push", "-u", "origin", "main"])
    print("Done! Files uploaded successfully.")


if __name__ == "__main__":
    main()
