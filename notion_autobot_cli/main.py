import json
from pprint import pprint

import typer
from dotenv import get_key
from notion_client import Client

app = typer.Typer()


@app.callback()
def callback():
    """Notion Autobot CLI."""


@app.command()
def shoot():
    """Shoot the portal gun."""
    typer.echo("Shooting portal gun!")


@app.command()
def load():
    """Load the portal gun."""
    typer.echo("Loading portal gun!")


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

    work_items = {}

    for item in data["results"]:
        if item["object"] == "page":
            assign = item["properties"]["Assign"]["people"][0]["name"]

            work_items[assign] = []

    for item in data["results"]:
        if item["object"] == "page":
            assign = item["properties"]["Assign"]["people"][0]["name"]

            name = item["properties"]["Name"]["title"][0]["plain_text"]
            status = item["properties"]["Status"]["status"]["name"]

            work_items[assign].append({"status": status, "name": name})

    pprint(work_items)


@app.command()
def template():
    """Create a template."""
    typer.echo("Creating a template!")

    from jinja2 import Environment, FileSystemLoader

    max_score = 100
    test_name = "Python Challenge"
    students = [
        {"name": "Sandrine", "score": 100},
        {"name": "Gergeley", "score": 87},
        {"name": "Frieda", "score": 92},
        {"name": "Fritz", "score": 40},
        {"name": "Sirius", "score": 75},
    ]

    environment = Environment(loader=FileSystemLoader("templates/"), autoescape=True)
    results_filename = "students_results.html"
    results_template = environment.get_template("results.html")
    context = {"students": students, "test_name": test_name, "max_score": max_score}
    with open(results_filename, mode="w", encoding="utf-8") as results:
        results.write(results_template.render(context))
        typer.echo(f"... wrote {results_filename}")


def debug_dump(data):
    with open("debug.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
