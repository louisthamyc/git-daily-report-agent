# Git Daily Report Agent

Git Daily Report Agent is a small Python desktop automation project that inspects the current repository, summarizes the author's Git activity for the day, and sends a polished HTML report by email.

It is designed for a local daily workflow:

- read the configured Git repository
- collect today's commits for the current Git author
- inspect commit stats and diffs
- ask a local Ollama model to turn raw activity into a structured engineering summary
- generate an HTML report
- email the report using Gmail
- optionally run automatically on a daily schedule from a Windows tray app

## Features

- GUI configuration window for repository, recipient, and schedule
- Windows tray icon with quick actions
- optional daily scheduler using APScheduler
- commit analysis for the current Git author only
- AI-based summary generation with Ollama
- structured report sections:
  - summary
  - accomplishments
  - bugs fixed
  - technical changes
  - next steps
- HTML report rendering via Jinja2
- Gmail API email delivery

## Project structure

```text
.
├── app.py                     # Tkinter UI and tray application entry point
├── config.yaml                # Runtime configuration for repo, email, and schedule
├── credentials/               # Gmail OAuth client secrets
├── data/
│   └── reports/               # temporary report output during generation
├── src/
│   ├── gmail_client.py         # Gmail send logic and OAuth setup
│   ├── ollama_client.py        # Local Ollama prompt + response handling
│   ├── report_builder.py       # Jinja2 HTML report rendering
│   ├── report_sender.py        # orchestration for collecting Git data and sending mail
│   └── ...
├── templates/
│   └── daily_report.html.j2   # HTML template for the final report
├── .gitignore
├── GitDailyAgent.spec         # PyInstaller build specification
├── README.md
```

## Requirements

Install the required Python dependencies:

```bash
pip install pyyaml jinja2 google-auth google-auth-oauthlib google-api-python-client ollama pillow pystray apscheduler
```

You also need:

- Git installed and available in PATH
- a running local Ollama server
- an Ollama model available, for example `qwen2.5:7b`
- a Google Cloud project with Gmail API enabled
- OAuth credentials saved at `credentials/credentials.json`

## Configuration

The app creates `config.yaml` automatically if it does not exist. A typical configuration looks like this:

```yaml
repository: "C:/path/to/your/repository"
email:
  recipient: "you@example.com"
report:
  subject_prefix: "Git Daily Report"
schedule:
  time: "19:00"
```

### Settings explained

- `repository`: the Git repository to inspect
- `email.recipient`: the email address for the report
- `report.subject_prefix`: prefix used in the email subject
- `schedule.time`: daily run time in `HH:MM` format using the local configured timezone (`Asia/Kuala_Lumpur` in the app)

## Gmail setup

The Gmail client expects these files:

- `credentials/credentials.json`
- `credentials/token.json`

When the app runs for the first time, it can open a browser-based Google OAuth sign-in flow and create the token automatically.

## Running the app

From the project root, run:

```bash
python app.py
```

This opens the Git Daily Agent window. From there you can:

- choose the repository path with Browse...
- update the email recipient
- set the daily schedule time
- save the configuration
- trigger a report manually
- minimize the app to the system tray

## Daily report flow

The application workflow is:

1. load config values from `config.yaml`
2. collect commits authored by the current Git user for the current day
3. fetch stats and diff details for each commit
4. send the raw activity to Ollama for structured analysis
5. render the HTML summary using the Jinja2 template
6. send the email through Gmail

The main logic lives in:

- `app.py` — desktop app, scheduling, and tray integration
- `src/report_sender.py` — git activity collection and orchestration
- `src/ollama_client.py` — Ollama request and JSON parsing
- `src/report_builder.py` — HTML output generation
- `src/gmail_client.py` — Gmail authentication and email sending

## Output

The report is generated temporarily in:

```text
data/reports/
```

The file name follows this pattern:

```text
report-YYYY-MM-DD.html
```

The current implementation writes the HTML report to disk and removes it after the email is sent, so the app can generate and deliver the report without leaving an unnecessary local copy behind.

## Notes

- The project reads the current Git author using `git config user.name`.
- It only analyzes commits from the current day (`--since=midnight`).
- The app is intended for local automation and may require small configuration adjustments depending on your repository path, timezone, Gmail OAuth setup, and the Ollama model you use.
- The generated summary is intentionally constrained to the actual Git activity analyzed by the app.

## Typical workflow

```bash
# start Ollama
ollama serve

# ensure the model is available
ollama pull qwen2.5:7b

# run the app
python app.py
```

Once the app is running, you can save your configuration and let the scheduler send a daily report automatically.
