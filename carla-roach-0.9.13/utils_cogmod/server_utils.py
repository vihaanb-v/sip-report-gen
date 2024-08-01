import subprocess
import os
import time
from omegaconf import OmegaConf
import psutil 

# os.environ.get('CUDA_VISIBLE_DEVICES')

import logging
import platform

log = logging.getLogger(__name__)

def is_process_running(process_name):
    """Check if there is any running process that contains the given name."""
    for proc in psutil.process_iter(['pid', 'name']):
        if process_name.lower() in proc.info['name'].lower():
            return True, proc.info['pid']
    return False, None

def kill_process_tree(pid, including_parent=True):    
    parent = psutil.Process(pid)
    if including_parent:
        parent.kill()

    children = parent.children(recursive=True)
    for child in children:
        child.kill()

def kill_carla():
    if platform.system() == "Windows":
        processes = ["CarlaUE4-Win64-Shipping.exe"]
        for proc_name in processes:
            is_running, pid = is_process_running(proc_name)
            if is_running:
                try:
                    kill_process_tree(pid)
                    log.info(f"Killed process {proc_name} and its child processes")
                    time.sleep(1)
                except psutil.NoSuchProcess:
                    log.info(f"Process {proc_name} no longer exists")
            else:
                log.info(f"Process {proc_name} not found.")
    if platform.system() == "Linux":
        kill_process = subprocess.Popen("killall -9 -r CarlaUE4-Linux", shell=True)
        kill_process.wait()
        time.sleep(1)
    log.info("Kill Carla Servers complete!")

class CarlaServerManager:
    def __init__(self, carla_sh_str, port=2000, configs=None, t_sleep=5):
        self._carla_sh_str = carla_sh_str
        # self._root_save_dir = root_save_dir
        self._t_sleep = t_sleep
        self.env_configs = []  # contains a single environment settings

        if configs is None:
            cfg = {
                "gpu": 0,
                "port": port,
            }
            self.env_configs.append(cfg)
        else:
            # there are multiple gpus in the same environment in the configuration file, we want to simulate every environment
            # for every gpu in different port. So, single environment configuration is created with single gpu and single port
            for cfg in configs:
                for gpu in cfg["gpu"]:
                    single_env_cfg = OmegaConf.to_container(cfg)
                    single_env_cfg["gpu"] = gpu
                    single_env_cfg["port"] = port
                    self.env_configs.append(single_env_cfg)
                    port += 5

    def start(self):
        # kill_carla()
        for cfg in self.env_configs:
            if platform.system() == "Windows":
                cmd = (
                    f'set CUDA_VISIBLE_DEVICES={cfg["gpu"]} && {self._carla_sh_str} '
                    f'-fps=25 -quality-level=high -carla-rpc-port={cfg["port"]} -prefernvidia -ResX=600 -ResY=400 -windowed'
                )
            if platform.system() == "Linux":
                cmd = (
                    f'CUDA_VISIBLE_DEVICES={cfg["gpu"]} bash {self._carla_sh_str} '
                    f'-fps=10 -quality-level=Low -carla-rpc-port={cfg["port"]} -prefernvidia -ResX=400 -ResY=300 -windowed'
                )
            log.info(cmd)
            server_process = subprocess.Popen(cmd, shell=True)
        time.sleep(self._t_sleep)

    def stop(self):
        kill_carla()
        time.sleep(self._t_sleep)
        log.info(f"Kill Carla Servers!")
        
    
