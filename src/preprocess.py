import typer
import pandas as pd
import os

def main(model_directory: str):
    '''
    '''
    working_directory = os.getcwd()

    model_path = os.path.join(working_directory, model_directory)

    print(f"{model_path}")

if __name__ == "__main__":
    typer.run(main)
