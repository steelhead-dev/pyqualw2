import typer
from pathlib import Path
from typing_extensions import Annotated
import pandas as pd
import os

app = typer.Typer()

model_directory =""

model_file_dictionary = {}

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
    """
    Enter in directory containg Ce-QUAL-W2 model files
    """

    model_directory = directory.resolve()
    print(f"Absolute path of the directory: {model_directory}")

    for item in model_directory.iterdir():
        if item.name == "w2_con.csv":
            model_file_dictionary["model_config_path"] = item.resolve()
            print(f"Config file logged at {model_file_dictionary["model_config_path"]}")


if __name__ == "__main__":
    app()
