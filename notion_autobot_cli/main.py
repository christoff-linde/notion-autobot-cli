import json
from pprint import pprint
from typing import Dict

import typer
from dotenv import get_key
from jinja2 import Environment, FileSystemLoader
from notion_client import Client

app = typer.Typer()


@app.command()
def poke():
    """Poke notion."""
    typer.echo("Poking notion!")

    client_secret = get_key(".env", "NOTION_INTERNAL_INTEGRATION_SECRET")
    db_id = get_key(".env", "NOTION_DATABASE_ID")

    if client_secret is None:
        typer.echo("No client secret found!")
        raise typer.Exit(code=1)
    if db_id is None:
        typer.echo("No database id found!")
        raise typer.Exit(code=1)

    notion = Client(auth=client_secret)
    yeet = notion.databases.query(database_id=db_id)
    debug_dump(yeet)


def list_users(notion_client: Client):
    """List all users in the workspace."""
    return notion_client.users.list()


@app.command()
def parse():
    """Parse notion debug dump data."""
    typer.echo("Parsing notion debug dump data!")

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

    pprint(projects)

    write_to_template(projects, "projects.html", "projects.md")

    # for item in data["results"]:
    #     if item["object"] == "page":
    #         project = item["properties"]["Project"]["select"]["name"]
    #         projects[project] = {}

    # for item in data["results"]:
    #     if item["object"] == "page":
    #         project = item["properties"]["Project"]["select"]["name"]
    #         status = extract_task_status(item["properties"]["Status"]["status"]["name"])
    #         if status is None:
    #             continue

    #         projects[project][status] = []

    # for item in data["results"]:
    #     if item["object"] == "page":
    #         project = item["properties"]["Project"]["select"]["name"]
    #         status = extract_task_status(item["properties"]["Status"]["status"]["name"])
    #         if status is None:
    #             continue
    #         # assignee = item["properties"]["Assign"]["people"][0]["name"]
    #         # name = item["properties"]["Name"]["title"][0]["plain_text"]
    #         # due_date = item["properties"]["Due"]["date"]

    #         projects[project][status].append(
    #             {"name": item["properties"]["Name"]["title"][0]["plain_text"]}
    #         )


def extract_task_status(status) -> str | None:
    """Extract task status from notion."""
    match status:
        case "Todo" | "In Progress" | "In Review" | "QA (Staging)":
            extracted_status = "In Progress"
        case "Backlog" | "Blocked":
            extracted_status = None
        case "Done":
            extracted_status = "Done"
        case _:
            extracted_status = None
    return extracted_status
    # for item in data["results"]:
    #     if item["object"] == "page":
    #         assign = item["properties"]["Assign"]["people"][0]["name"]

    #         work_items[assign] = []

    # for item in data["results"]:
    #     if item["object"] == "page":
    #         assign = item["properties"]["Assign"]["people"][0]["name"]

    #         # name = item["properties"]["Name"]["title"][0]["plain_text"]
    #         status = item["properties"]["Status"]["status"]["name"]
    #         work_items[assign].append([status])
    #         # work_items[assign].append({"status": status, "name": name})

    # pprint(work_items)


def write_to_template(data: Dict, template_path: str, output_path: str):
    """Write to a template."""
    typer.echo("Writing to a template!")

    environment = Environment(
        loader=FileSystemLoader("templates/"),
        keep_trailing_newline=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    results_filename = output_path
    results_template = environment.get_template(template_path)

    context = {"data": data}

    with open(results_filename, mode="w", encoding="utf-8") as results:
        results.write(results_template.render(context))
        typer.echo(f"... wrote {results_filename}")


def debug_dump(data):
    with open("debug.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
