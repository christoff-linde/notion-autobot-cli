import json
from datetime import datetime
from typing import Dict

import requests
import typer
from discord import SyncWebhook
from dotenv import get_key
from jinja2 import Environment, FileSystemLoader


def extract_task_status(status) -> str | None:
    """Extract task status from notion."""
    match status:
        case "Todo" | "In Progress" | "In Review" | "QA (Staging)":
            extracted_status = "In Progress"
        case "Blocked":
            extracted_status = "Blocked"
        case "Backlog":
            extracted_status = None
        case "Done":
            extracted_status = "Done"
        case _:
            extracted_status = None
    return extracted_status


def parse_notion_data() -> Dict:
    """Parse notion debug data.

    This goes through the debug.json file (or later, any notion-returned data)
    and extracts all the project data (in the format required for the initial
    use case).
    """
    with open("debug.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    projects = {}

    for item in data["results"]:
        if item["object"] == "page":
            project = item["properties"]["Project"]["select"]["name"]
            status = extract_task_status(item["properties"]["Status"]["status"]["name"])
            if status is None:
                continue

            # if project not in projects:
            #     projects[project] = {}
            if status not in projects:
                projects[status] = {}

            # Extract additional properties as needed
            name = item["properties"]["Name"]["title"][0]["plain_text"]
            assignee = item["properties"]["Assign"]["people"][0]["name"]
            # due_date = item["properties"]["Due"]["date"]

            if project not in projects[status]:
                projects[status][project] = []

            projects[status][project].append({"name": name, "assignee": assignee})

    return projects


def write_to_template(data: Dict, template_path: str, output_path: str):
    """Write to a template."""
    typer.echo("Writing to a template!")

    environment = Environment(
        loader=FileSystemLoader("templates/"),
        keep_trailing_newline=False,
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=True,
    )
    results_filename = output_path
    results_template = environment.get_template(template_path)

    context = {"data": data, "current_time": datetime.now().strftime("%A, %d-%m-%Y")}

    with open(results_filename, mode="w", encoding="utf-8") as results:
        results.write(results_template.render(context))
        typer.echo(f"... wrote {results_filename}")


def debug_dump(data):
    with open("debug.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def send_webhook() -> None:
    """Send a webhook to discord.

    This sends the generated markdown file to discord.
    """
    webhook_url = get_key(".env", "DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise typer.Exit(code=1)

    session = requests.Session()
    webhook = SyncWebhook.from_url(webhook_url, session=session)

    with open("TODAY.md") as file:
        data = file.read()
    webhook.send(data)
