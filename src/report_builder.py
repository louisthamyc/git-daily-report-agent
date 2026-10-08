
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


PROJECT_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PROJECT_DIR / "templates"
OUTPUT_DIR = PROJECT_DIR / "data" / "reports"


def build_html_report(
    report,
    repository_name,
    report_date=None,
):
    if report_date is None:
        report_date = datetime.now().astimezone().strftime("%Y-%m-%d")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    environment = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(
            enabled_extensions=("html", "j2"),
            default_for_string=True,
        ),
    )

    template = environment.get_template("daily_report.html.j2")

    html = template.render(
        report=report,
        repository_name=repository_name,
        report_date=report_date,
    )

    output_file = OUTPUT_DIR / f"report-{report_date}.html"
    output_file.write_text(html, encoding="utf-8")

    return output_file
