import datetime
import gym
from pathlib import Path
import wandb
import hydra
from omegaconf import DictConfig, OmegaConf
import logging
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.utils import set_random_seed
from stable_baselines3.common.callbacks import CallbackList

from agents.rl_birdview.utils.wandb_callback import WandbCallback
from carla_gym.utils import config_utils
from utils import server_utils

log = logging.getLogger(__name__)


@hydra.main(config_path="config", config_name="train_rl")
def main(cfg: DictConfig):
    if cfg.kill_running:
        server_utils.kill_carla()
    set_random_seed(cfg.seed, using_cuda=True)

    # start carla servers
    # according to config/train_rl.yaml,
    # cfg.train_envs is from config/train_envs/endless_all.yaml
    server_manager = server_utils.CarlaServerManager(
        cfg.carla_sh_path, configs=cfg.train_envs, t_sleep=10
    )
    server_manager.start()

    # prepare agent
    # According to config/train_rl.yaml,
    # cfg.ev_id = hero
    # cfg.actors[hero].agent = ppo
    agent_name = cfg.actors[cfg.ev_id].agent

    last_checkpoint_path = (
        Path(hydra.utils.get_original_cwd()) / "outputs" / "checkpoint.txt"
    )
    if last_checkpoint_path.exists():
        with open(last_checkpoint_path, "r") as f:
            cfg.agent[agent_name].wb_run_path = f.read()  # gives a new value to wb_run_path which was null found in
            # config/agent/ppo.yaml

    OmegaConf.save(config=cfg.agent[agent_name], f="config_agent.yaml")  # the saved configuration contains agent settings for
    # rl training which includes agent observation settings,
    # policy and training methodology. This file is composed
    # of config/agent/ppo.yaml, config/agent/ppo/obs_configs/birdview.yaml,
    # config/agent/ppo/policy/xtma_beta.yaml, config/agent/ppo/training/ppo.yaml

    # single agent
    # According to config/train_rl.yaml,
    # cfg.agent[ppo].entry_point = agents.rl_birdview.rl_birdview_agent:RlBirdviewAgent
    AgentClass = config_utils.load_entry_point(
        cfg.agent[agent_name].entry_point
    )  # loads the class instance, does not create actual object
    agent = AgentClass(
        "config_agent.yaml"
    )  # creates an agent object from the above class and previously saved agent configuration
    cfg_agent = OmegaConf.load(
        "config_agent.yaml"
    )  # assigns the agent settings to a variable

    obs_configs = {
        cfg.ev_id: OmegaConf.to_container(cfg_agent.obs_configs)
    }  # key value pair between hero and config/agent/ppo/obs_configs/birdview.yaml
    reward_configs = {
        cfg.ev_id: OmegaConf.to_container(cfg.actors[cfg.ev_id].reward)
    }  # key value pair between hero and some parts of config/train_rl.yaml. Contains how rewards are calculated.
    terminal_configs = {
        cfg.ev_id: OmegaConf.to_container(cfg.actors[cfg.ev_id].terminal)
    }  # key value pair between hero and some parts of config/train_rl.yaml. Contains how an episode terminates.

    # env wrapper
    # According to config/agent/ppo.yaml
    # cfg_agent.env_wrapper.entry_point = agents.rl_birdview.utils.rl_birdview_wrapper:RlBirdviewWrapper
    # cfg_agent.env_wrapper.kwargs =    input_states: [control, vel_xy]
    #                                   acc_as_action: True
    EnvWrapper = config_utils.load_entry_point(cfg_agent.env_wrapper.entry_point)
    wrapper_kargs = cfg_agent.env_wrapper.kwargs

    # cfg.train_envs contains the configuration in config/train_envs/endless_all.yaml file
    config_utils.check_h5_maps(cfg.train_envs, obs_configs, cfg.carla_sh_path)

    # creates a gym environment according to a given configuration and wraps it with a wrapper
    def env_maker(config):
        log.info(f'making port {config["port"]}')
        log.info(f'config: {config}')
        env = gym.make(
            config["env_id"],
            obs_configs=obs_configs,
            reward_configs=reward_configs,
            terminal_configs=terminal_configs,
            host="localhost",
            port=config["port"],
            seed=cfg.seed,
            no_rendering=False,
            **config["env_configs"],
        )
        env = EnvWrapper(env, **wrapper_kargs)
        return env
    print('server_manager.env_configs: ', server_manager.env_configs)
    if cfg.dummy or len(server_manager.env_configs) == 1:
        env = DummyVecEnv(
            [
                lambda config=config: env_maker(config)
                for config in server_manager.env_configs
            ]
        )
    else:
        env = SubprocVecEnv(
            [
                lambda config=config: env_maker(config)
                for config in server_manager.env_configs
            ]
        )

    # wandb init
    # update the cfg.wb_name to the date and time of the run
    cfg.wb_name = datetime.datetime.now().strftime("%H:%M")
    log.info(f'wandb run name: {cfg.wb_name}')
    wb_callback = WandbCallback(cfg, env)
    callback = CallbackList([wb_callback])

    # save wandb run path to file such that bash file can find it
    with open(last_checkpoint_path, "w") as f:
        f.write(wandb.run.path)

    agent.learn(
        env, total_timesteps=int(cfg.total_timesteps), callback=callback, seed=cfg.seed
    )

    server_manager.stop()


if __name__ == "__main__":
    main()
    log.info("train_rl.py DONE!")
