
from pathlib import Path
from ..config import Config
import tempfile

class ModelRunner:

    def __init__(self, config_list):
        self.config_list = config_list
    

    def run(self):

        for config in self.config_list:
           wd = self.make_wd() 
           self.copy_in_model_files(wd, config)
           self.gen_input_files(config)
           #self.run_model
           #self.archvie_model
    


    def make_wd(self) -> Path:
        return tempfile.mkdtemp()

    def copy_in_model_files(self, wd:Path, config:Config):
        # Copy in configured files (W2_con, Mbth, Mvpr1, temp, met, flow)

        wd = Path(wd)
        src = Path(__file__).parent / 'model_template'

        if not src.exists():
            raise FileNotFoundError
        
        for file in src.iterdir():
            destination = wd / file.name
            file.copy(destination)

    def gen_input_files(self, wd:Path, year:int):
        
        #src = Path(__file__).parent / 'model_template'
        #Working project src diectory
        Met = MetDataInput.fromfile(met_data_path)