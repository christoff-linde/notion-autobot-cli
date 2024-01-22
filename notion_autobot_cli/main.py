import typer
from dotenv import get_key
from notion_client import Client
from typing_extensions import Annotated
from utils import debug_dump, parse_notion_data, write_to_template

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
