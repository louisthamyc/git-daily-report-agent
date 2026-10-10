from datetime import datetime
from src.ollama_client import analyze_git_activity
from src.report_builder import build_html_report
from pathlib import Path
from src.gmail_client import send_email

import subprocess
import yaml

PROJECT_DIR = Path(__file__).resolve().parent

def load_config():
    config_file = PROJECT_DIR / "config.yaml"

    with open(config_file, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)
    

config = load_config()

REPOSITORY = config["repository"]
EMAIL_RECIPIENT = config["email"]["recipient"]
SUBJECT_PREFIX = config["report"]["subject_prefix"]


def run_git_command(repository, *args):
    result = subprocess.run(
        ["git", "-C", repository, *args],
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
        errors="replace",
    )

    return result.stdout

# get current author
def get_git_cur_author():
    result = subprocess.run(
        ["git", "config", "user.name"],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.strip()


def get_today_commits(repository):
    curr_author = get_git_cur_author()
    output = run_git_command(
        repository,
        "log",
        f"--author={curr_author}",
        "--since=midnight",
        "--pretty=format:%H|%h|%an|%ad|%s",
        "--date=iso",
    )

    commits = []

    for line in output.splitlines():
        commit_hash, short_hash, author, date, message = line.split("|", 4)

        commits.append(
            {
                "hash": commit_hash,
                "short_hash": short_hash,
                "author": author,
                "date": date,
                "message": message,
            }
        )

    return commits


def get_commit_details(repository, commit_hash):
    stats = run_git_command(
        repository,
        "show",
        "--stat",
        "--format=",
        commit_hash,
    )

    diff = run_git_command(
        repository,
        "show",
        "--format=",
        "--no-ext-diff",
        commit_hash,
    )

    return {
        "stats": stats,
        "diff": diff,
    }


def build_git_activity(repository, commits):

    if not commits:
        return "No Git commits were made today."

    activity = []

    for commit in commits:
        details = get_commit_details(
            repository,
            commit["hash"],
        )

        activity.append(
            f"""
                Commit: {commit["short_hash"]}
                Author: {commit["author"]}
                Date: {commit["date"]}
                Message: {commit["message"]}

                Statistics:
                {details["stats"]}

                Diff:
                {details["diff"]}
            """
        )

    return "\n".join(activity)


if __name__ == "__main__":
    print("Collecting today's Git activity...")

    commits = get_today_commits(REPOSITORY)

    if commits:
        git_activity = build_git_activity(REPOSITORY, commits)
        print("Analyzing activity with local AI...")
        report = analyze_git_activity(git_activity)
    else:
        report = {
            "summary": "No Git commits were recorded today.",
            "accomplishments": [],
            "bugs_fixed": [],
            "technical_changes": [],
            "next_steps": [],
        }
    
    repository_name = Path(REPOSITORY).name

    output_file = build_html_report(
        report=report,
        repository_name=repository_name,
    )

    print()
    print("Report generated successfully.")
    print()
    print("Sending report by email...")

    cur_date = datetime.now().astimezone().strftime("%Y-%m-%d")

    html_content = output_file.read_text(encoding="utf-8")

    send_email(
        recipient=EMAIL_RECIPIENT,
        subject=f"{SUBJECT_PREFIX} - {cur_date}",
        html_content=html_content,
    )

    print("Daily Git report sent successfully")
    output_file.unlink()  # Delete the temporary HTML file