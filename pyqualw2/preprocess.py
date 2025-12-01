import typer
from pathlib import Path
from typing_extensions import Annotated
import pandas as pd
import os
import tomli

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
        if item.name == "inputs":
            model_file_dictionary["model_inputs_path"] = item.resolve()
            print(f"Config file logged at {model_file_dictionary["model_inputs_path"]}")
        if item.name == "outputs":
            model_file_dictionary["model_outputs_path"] = item.resolve()
            print(f"Config file logged at {model_file_dictionary["model_outputs_path"]}")
        if item.name == "w2_con.csv":
            model_file_dictionary["model_config_path"] = item.resolve()
            print(f"Config file logged at {model_file_dictionary["model_config_path"]}")
        if item.name == "run_settings.toml":
            model_file_dictionary["run_settings_path"] = item.resolve()
            print(f"Config file logged at {model_file_dictionary["run_settings_path"]}")

#def parse_run_settings ():
    with open(model_file_dictionary["run_settings_path"], mode = 'rb') as run_settings:
        settings = tomli.load(run_settings)
        print(settings)

if __name__ == "__main__":
    app()
