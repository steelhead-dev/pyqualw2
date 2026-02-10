from pathlib import Path
from typing import Annotated

import tomli
import typer

app = typer.Typer()

model_directory = ""

model_file_dictionary = {}


@app.command()
def process_directory(
    directory: Annotated[
        Path,
        typer.Argument(
            help="The directory to process.",
            exists=True,  # Ensure diectory exisit
            dir_okay=True,  # Ensure it's a directory
            file_okay=False,  # Ensure it's not a file
        ),
    ],
):
    """Enter in directory containg Ce-QUAL-W2 model files."""
    model_directory = directory.resolve()

    for item in model_directory.iterdir():
        if item.name == "inputs":
            model_file_dictionary["model_inputs_path"] = item.resolve()
        if item.name == "outputs":
            model_file_dictionary["model_outputs_path"] = item.resolve()
        if item.name == "w2_con.csv":
            model_file_dictionary["model_config_path"] = item.resolve()
        if item.name == "run_settings.toml":
            model_file_dictionary["run_settings_path"] = item.resolve()

    with open(model_file_dictionary["run_settings_path"], mode="rb") as f:
        settings = tomli.load(f)

        run_settings = settings["run_settings"]
        time_start = run_settings["time_start"]
        time_end = run_settings["time_end"]
        print(f"The starting date and tiem is {time_start}")  # noqa: T201
        print(f"The ending date and tiem is {time_end}")  # noqa: T201


if __name__ == "__main__":
    app()
