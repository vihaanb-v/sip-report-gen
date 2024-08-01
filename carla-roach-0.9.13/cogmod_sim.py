import gym
import json
from pathlib import Path
import wandb
import hydra
from omegaconf import DictConfig, OmegaConf
import logging
import os.path
import sys

from gym.wrappers.monitoring.video_recorder import ImageEncoder
from stable_baselines3.common.vec_env.base_vec_env import tile_images

from carla_gym.utils import config_utils
from utils import server_utils
from agents.rl_birdview.utils.wandb_callback import WandbCallback
import pandas as pd

log = logging.getLogger(__name__)

from pygame_display import PygameDisplay
import os

def run_single(run_name, env, agents_dict, agents_log_dir, log_video, max_step=2800, show_pygame=False):
    display = PygameDisplay("Agent Visualization") if show_pygame else None
    list_render = []
    ep_stat_dict = {}
    ep_event_dict = {}
    
    supervision_dict_list = []
    
    for actor_id, agent in agents_dict.items():
        log_dir = agents_log_dir / actor_id
        log_dir.mkdir(parents=True, exist_ok=True)
        agent.reset(log_dir / f'{run_name}.log')

    log.info(f'Start running {run_name}.')
    obs = env.reset()
    timestamp = env.timestamp
    start_timestamp = timestamp
    done = {'__all__': False}
    
    while not done['__all__']:
        control_dict = {}
        
        agent = agents_dict['hero']
        control_dict['hero'] = agent.run_step(obs['hero'], timestamp)
            
        obs, reward, done, info = env.step(control_dict)
        
        supervision_dict = agent.supervision_dict
        supervision_dict['gaze_direction'] = obs['hero']['birdview']['gaze_direction']
        supervision_dict['detection_error'] = obs['hero']['birdview']['detection_error']
        supervision_dict['approximation_error'] = obs['hero']['birdview']['approximation_error']
        supervision_dict['image_difference'] = obs['hero']['birdview']['image_difference']
        supervision_dict['timestamp'] = timestamp
        supervision_dict['frame'] = timestamp['frame']
        supervision_dict_list.append(agent.supervision_dict)

        if log_video:
            img = obs['hero']['birdview']['rendered']
            img_org = obs['hero']['birdview']['image_original']
            masks = obs['hero']['birdview']['masks']
            # print("obs ", img.shape)
            render_imgs = [agent.render(info[actor_id]['reward_debug'], info[actor_id]['terminal_debug']) for actor_id, agent in agents_dict.items()]
            rendered_image = tile_images(render_imgs)
            list_render.append(rendered_image)
            if show_pygame:
                display.display_image(img, img_org)

        if done[actor_id] and (actor_id not in ep_stat_dict):
            episode_stat = info[actor_id]['episode_stat']
            ep_stat_dict[actor_id] = episode_stat
            ep_event_dict[actor_id] = info[actor_id]['episode_event']

        timestamp = env.timestamp
        if max_step and (timestamp['step'] - start_timestamp['step']) > max_step:
            display.close()
            return run_single(run_name, env, agents_dict, agents_log_dir, log_video)

        if show_pygame and display.check_for_quit():
            break
    
    if show_pygame and display:
        # check if pygame window is open and close it
        display.close()
    return list_render, ep_stat_dict, ep_event_dict, timestamp, supervision_dict_list


def run_env(cfg, 
            env_idx,
            env_setup,
            suite_name,
            agents_dict, 
            obs_configs, 
            reward_configs, 
            terminal_configs):

    # resume task_idx from ep_stat_buffer_{env_idx}.json
    ep_state_buffer_json = f'{hydra.utils.get_original_cwd()}/outputs/ep_stat_buffer_{env_idx}.json'
    if cfg.resume and os.path.isfile(ep_state_buffer_json):
        ep_stat_buffer = json.load(open(ep_state_buffer_json, 'r'))
        ckpt_task_idx = len(ep_stat_buffer['hero'])
        log.info(f'Resume from task_idx {ckpt_task_idx}')
    else:
        ckpt_task_idx = 0
        ep_stat_buffer = {}
        for actor_id in agents_dict.keys():
            ep_stat_buffer[actor_id] = []
        log.info(f'Start new env from task_idx {ckpt_task_idx}')

    log.info(f"Start running! env_idx: {env_idx}, suite_name: {suite_name}")

    # make directories
    diags_dir = Path('diagnostics') / suite_name
    agents_log_dir = Path('agents_log') / suite_name
    
    diags_dir.mkdir(parents=True, exist_ok=True)
    agents_log_dir.mkdir(parents=True, exist_ok=True)
    
    # make env
    env = gym.make(env_setup['env_id'], obs_configs=obs_configs, reward_configs=reward_configs,
                terminal_configs=terminal_configs, host=cfg.host, port=cfg.port,
                seed=cfg.seed, no_rendering=cfg.no_rendering, **env_setup['env_configs'])


    # loop through each route
    for task_idx in range(ckpt_task_idx, env.num_tasks):
        log.info(f"Start running env_idx {env_idx}, task_idx {task_idx}, suite_name: {suite_name}")
        env.set_task_idx(task_idx)

        run_name = f"{env.task['driver']}_{env.task['route_id']:01d}_repeat_{env.task['n_repeat']}"
        agents_dict['hero'].obs_configs['birdview']['driver'] = env.task['driver']

        recorder_path = os.path.join(os.path.abspath(diags_dir), f'{run_name}.log')
        video_path = (diags_dir / f'{run_name}.mp4').as_posix()
        csv_path = (diags_dir / f'{run_name}.csv').as_posix()
        json_path = (diags_dir / f'{run_name}.json').as_posix()

        env.client.start_recorder(recorder_path, True)
        log.info("Recording on file: %s", recorder_path)
        try: 
            list_render, ep_stat_dict, ep_event_dict, _, supervision_dict  = run_single(run_name=run_name, 
                                                                                        env=env, 
                                                                                        agents_dict=agents_dict, 
                                                                                        agents_log_dir=agents_log_dir, 
                                                                                        log_video=cfg.log_video,
                                                                                        show_pygame=True)
        except Exception as e:
            log.error(f'Error in run_single: {e}')
            env.client.stop_recorder()
            continue
        
        # log video
        if cfg.log_video:
            env.client.stop_recorder()
            encoder = ImageEncoder(video_path, list_render[0].shape, 30, 30)
            for im in list_render:
                encoder.capture_frame(im)
            encoder.close()
            encoder = None

        # save statistics
        save_stat(csv_path, supervision_dict)
        
        # dump events
        with open(json_path, 'w') as fd:
            json.dump(ep_event_dict, fd, indent=4, sort_keys=False)

        # # save statistics
        for actor_id, ep_stat in ep_stat_dict.items():
            ep_stat['run'] = run_name
            ep_stat['suite'] = suite_name
            ep_stat_buffer[actor_id].append(ep_stat)

        with open(ep_state_buffer_json, 'w') as fd:
            json.dump(ep_stat_buffer, fd, indent=4, sort_keys=True)
        # clean up
        list_render.clear()
        ep_event_dict = None

    # close env
    env.close()
    env = None
    
    pass


@hydra.main(config_path='config', config_name='itsc_route')
def main(cfg: DictConfig):
    log.setLevel(cfg.log_level.upper())
    if cfg.kill_running:
        server_utils.kill_carla()

    # start carla servers
    server_manager = server_utils.CarlaServerManager(cfg.carla_sh_path, port=cfg.port)
    server_manager.start()

    # single actor, place holder for multi actors
    agents_dict = {}
    obs_configs = {}
    reward_configs = {}
    terminal_configs = {}
    agent_names = []
    
    for ev_id, ev_cfg in cfg.actors.items():
        agent_names.append(ev_cfg.agent)
        cfg_agent = cfg.agent[ev_cfg.agent]
        OmegaConf.save(config=cfg_agent, f='config_agent.yaml')
        AgentClass = config_utils.load_entry_point(cfg_agent.entry_point)
        agents_dict[ev_id] = AgentClass('config_agent.yaml')
        
        # changing the birdview module to extended_chauffeurnet 
        agents_dict[ev_id].obs_configs['birdview']['module'] = 'birdview.extended_chauffeurnet'
        # agents_dict[ev_id].obs_configs['birdview']['module'] = 'birdview.chauffeurnet'
        
        obs_configs[ev_id] = agents_dict[ev_id].obs_configs

        # get obs_configs from agent
        reward_configs[ev_id] = OmegaConf.to_container(ev_cfg.reward)
        terminal_configs[ev_id] = OmegaConf.to_container(ev_cfg.terminal)

    # check h5 birdview maps have been generated
    config_utils.check_h5_maps(cfg.test_suites, obs_configs, cfg.carla_sh_path)

    # resume env_idx from checkpoint.txt
    last_checkpoint_path = f'{hydra.utils.get_original_cwd()}/outputs/checkpoint.txt'
    
    try:
        if os.path.exists(last_checkpoint_path):
            with open(last_checkpoint_path, 'r') as f:
                env_idx = int(f.read())
        else:
            # create checkpoint.txt
            env_idx = 0
            with open(last_checkpoint_path, 'w') as f:
                f.write(f'{env_idx}')
                
        
        if env_idx >= len(cfg.test_suites):
            log.info(f'Finished! env_idx: {env_idx}')
            return
        
        while env_idx <= len(cfg.test_suites)-1:
            # compose suite_name
            env_setup = OmegaConf.to_container(cfg.test_suites[env_idx])
            suite_name = env_setup['env_id']
            for k in sorted(env_setup['env_configs']):
                suite_name = suite_name + '_' + str(env_setup['env_configs'][k])
            
            run_env(cfg,
                    env_idx,
                    env_setup,
                    suite_name,
                    agents_dict, 
                    obs_configs, 
                    reward_configs, 
                    terminal_configs)
            
            log.info(f"Finished running env_idx {env_idx}, suite_name: {suite_name}")
            env_idx += 1
            with open(last_checkpoint_path, 'w') as f:
                f.write(f'{env_idx}')
    except Exception as e:
        log.error(f"An error occurred: {str(e)}")

    server_manager.stop()
    pass

def save_stat(file_path, supervision_dict_list):
    # Initialize an empty list to hold the modified dictionaries
    modified_dicts = []

    for supervision_dict in supervision_dict_list:
        modified_dict = {
            'timestamp': supervision_dict['timestamp']['step'],
            'simulation_time': supervision_dict['timestamp']['simulation_time'],
            'wall_time': supervision_dict['timestamp']['wall_time'],
            'frame': supervision_dict['frame'],
            'throttle': supervision_dict['action'][0],
            'steer': supervision_dict['action'][1],
            'brake': supervision_dict['action'][2],
            'value': supervision_dict['value'],
            'action_mu_1': supervision_dict['action_mu'][0],
            'action_mu_2': supervision_dict['action_mu'][1],
            'action_sigma_1': supervision_dict['action_sigma'][0],
            'action_sigma_2': supervision_dict['action_sigma'][1],
            'speed': supervision_dict['speed'],
            'gaze_direction': supervision_dict['gaze_direction'],
            'detection_error': supervision_dict['detection_error'],
            'approximation_error': supervision_dict['approximation_error'],
            'image_difference': supervision_dict['image_difference']
        }
        modified_dicts.append(modified_dict)
    
    # Creating a DataFrame from the list of modified dictionaries
    df = pd.DataFrame(modified_dicts)
    
    # Saving the DataFrame to a CSV file
    df.to_csv(file_path, index=False)
    pass


if __name__ == '__main__':
    main()
    log.info("cogmod_sim.py DONE!")
