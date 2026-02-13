from pathlib import Path
from ..config import Config
import tempfile
import os
import subprocess

class ModelRunner:

    def __init__(self, config_list):
        self.config_list = config_list
    
    def run(self):

        for config in self.config_list:
           wd = self.make_temp_wd() 
           self.copy_in_model_files(wd, config)
           self.gen_input_files(config)
           self.run_model(wd)
           #self.archvie_model

    def make_temp_wd(self) -> Path:
        return tempfile.mkdtemp()

    def copy_in_model_files(self, wd:Path, config:Config):
        # Copy in configured files (W2_con, Mbth, Mvpr1, temp, met, flow)
        wd = Path(wd)
        config.to_directory(wd)
    
    def run_model(self, wd:Path):
        model_path = wd / 'w2_v45_64.exe'
        if os.name == 'nt':  # Windows
            process = subprocess.Popen([str(model_path)], 
                                    creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Linux/Unix with Wine
            process = subprocess.Popen(['wine', str(model_path)],
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE,
                                    cwd=str(wd))
    
    def archive_model_run(self, wd:Path, config:Config):
        
        archive_dir = Path(__file__).parent/model_run_desc/year

        for file in wd.iterdir():
            file.copy(archive_dir)