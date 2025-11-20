import typer
from pathlib import Path
from typing_extensions import Annotated
import pandas as pd
import os

app = typer.Typer()


@app.command()
def process_directory(
    directory: Annotated[
        Path,
        typer.Argument(
            help='The directory to process.',
            exists=True, #Ensure diectory exisit
            dir_okay=True, # Ensure it's a directory
            file_okay=False, # Ensure it's not a file
        )
    ]
):
    absolute_path = directory.resolve()
    print(f"Absolute path of the directory: {absolute_path}")

    print("Contents of the directory")
    for item in absolute_path.iterdir():
        print(f"- {item.name}")


if __name__ == "__main__":
    app()
