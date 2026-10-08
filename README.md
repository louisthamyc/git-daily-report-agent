# Git Daily Report Agent

A small Python automation project that inspects the Git activity for the current author, summarizes recent commits with a local Ollama model, generates a polished HTML report, and emails it to a configured recipient.

## Overview

This project is designed to help you send a daily engineering summary without manually writing a report. It:

- reads the repository configured in `config.yaml`
- finds the current Git author and recent commit history
- extracts commit stats and diffs for recent work
- asks a local Ollama model to turn the raw Git activity into a structured report
- renders the result as an HTML file in the `data/reports` folder
- sends the report via Gmail

## Features

- Git activity extraction from recent commits
- AI-generated summaries using Ollama
- Structured report output with sections for:
  - summary
  - accomplishments
  - bugs fixed
  - technical changes
  - next steps
- HTML report generation using Jinja2 templates
- Email delivery through Gmail API

## Requirements

Install the Python dependencies used by the project:

```bash
pip install pyyaml jinja2 google-auth google-auth-oauthlib google-api-python-client ollama
```

You also need:

- Git installed and available in PATH
- A running local Ollama instance with a model available, such as `qwen2.5:7b`
- Create a Google Cloud Project and get Google Gmail API credentials configured in the `credentials/` folder

## Configuration

Update `config.yaml` before running the project:

```yaml
repository: "C:\\YOUR REPO"

email:
  recipient: "you@example.com"

report:
  subject_prefix: "Git Daily Report"
```

Notes:

- `repository` should point to the Git repository you want to inspect
- `email.recipient` is the address that receives the generated report
- `report.subject_prefix` controls the email subject prefix

## Gmail setup

The Gmail client expects OAuth credentials in:

- `credentials/credentials.json`
- `credentials/token.json`

The first time the app runs, it may open a browser-based Google sign-in flow and generate a token file.

## Running the project

From the project root:

```bash
python app.py
```

When executed, the script will:

1. find recent commits for the current Git author
2. fetch commit stats and diffs
3. send the full activity to the Ollama model
4. generate an HTML report
5. email the report to the configured recipient

## How it works

The main workflow is defined in `app.py`:

- `get_today_commits()` reads recent Git commits for the active author
- `get_commit_details()` fetches each commit's diff and stats
- `build_git_activity()` assembles the commit payload
- `analyze_git_activity()` asks Ollama to return valid JSON structured as a daily report
- `build_html_report()` renders the final HTML document
- `send_email()` sends the output using Gmail

## Output

Generated reports are saved in:

```text
data/reports/
```

The output file name follows the pattern:

```text
report-YYYY-MM-DD.html
```

## Notes

- The project still WIP
- The project currently checks commit history using the current Git author and a rolling 10-day window (You may change according to need).
- The project is designed around local automation and may need minor adjustments depending on your repository path, Gmail setup, and available Ollama model.
- The generated report is intentionally factual and constrained to the actual Git activity that was analyzed.
