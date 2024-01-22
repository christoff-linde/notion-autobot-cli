import json
from datetime import datetime
from pprint import pprint
from typing import Dict

import typer
from dotenv import get_key
from jinja2 import Environment, FileSystemLoader
from notion_client import Client
from typing_extensions import Annotated

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
    data = notion.databases.query(database_id=db_id)
    debug_dump(data)


def list_users(notion_client: Client):
    """List all users in the workspace."""
    return notion_client.users.list()


@app.command()
def parse():
    """Parse notion debug dump data."""
    typer.echo("Parsing notion debug dump data!")

    today_data = parse_notion_data()
    write_to_template(today_data, "projects.html", "TODAY.md")

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


@app.command(
    help="Requests latest data from Notion database and outputs to debug.json file. "
    "The data is then parsed and written to a template.",
    short_help="Generate today's task list markdown report file.",
)
def today(
    debug: Annotated[bool, typer.Option()] = False,
    all_tasks: Annotated[bool, typer.Option()] = False,
) -> None:
    """Generate today's task list markdown report file."""
    if not debug:
        client_secret = get_key(".env", "NOTION_INTERNAL_INTEGRATION_SECRET")
        db_id = get_key(".env", "NOTION_DATABASE_ID")

        if client_secret is None:
            typer.echo("No client secret found!")
            raise typer.Exit(code=1)
        if db_id is None:
            typer.echo("No database id found!")
            raise typer.Exit(code=1)

        notion = Client(auth=client_secret)

        data = notion.databases.query(
            database_id=db_id,
            filter={
                "property": "Type",
                "select": {"equals": "Maintenance" if not all_tasks else ""},
            },
            sorts=[
                {"property": "Project", "direction": "ascending"},
                {"property": "Name", "direction": "ascending"},
                {"property": "Assign", "direction": "ascending"},
            ],
        )
        debug_dump(data)

    today_data = parse_notion_data()
    write_to_template(today_data, "projects.html", "TODAY.md")


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
