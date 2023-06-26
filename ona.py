import typer
import time
from rich import print
from typing_extensions import Annotated
from rich.progress import track
from my_logger import MyLogger

app = typer.Typer()

logging = MyLogger()


@app.command()
def main():
    username = typer.prompt("Enter ONA username or press enter to use default", default="touma", show_default=False)
    password = typer.prompt("Enter ONA password or press enter to use default", default="touma", show_default=False)
    logging.info(f"Welcome {username.upper()}. with password {password}")


if __name__ == "__main__":
    app()
