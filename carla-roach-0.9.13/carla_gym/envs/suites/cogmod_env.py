from carla_gym import CARLA_GYM_ROOT_DIR
from carla_gym.carla_multi_agent_env import CarlaMultiAgentEnv
from carla_gym.utils import config_utils
import json


class CogModEnv(CarlaMultiAgentEnv):
    def __init__(self, carla_map, host, port, seed, no_rendering, obs_configs, reward_configs, terminal_configs,
                 weather_group, routes_group):
        nRepeat = 3
        all_tasks = self.build_all_tasks(carla_map, weather_group, routes_group, nRepeat)
        super().__init__(carla_map, host, port, seed, no_rendering,
                         obs_configs, reward_configs, terminal_configs, all_tasks)

    @staticmethod
    def build_all_tasks(carla_map, weather_group, routes_group, nRepeat=1):
        assert carla_map in ['Town04', 'Town05']
        
        if routes_group == 'empty':
            num_zombie_vehicles = {'Town04': 0, 'Town05': 0}
            num_zombie_walkers = {'Town04': 0, 'Town05': 0}
        elif routes_group == 'low':
            num_zombie_vehicles = {'Town04': 40, 'Town05': 40}
            num_zombie_walkers = {'Town04': 20, 'Town05': 20}
        elif routes_group == 'medium':
            num_zombie_vehicles = {'Town04': 80, 'Town05': 80}
            num_zombie_walkers = {'Town04': 40, 'Town05': 40}
        elif routes_group == 'high':
            num_zombie_vehicles = {'Town04': 120, 'Town05': 120}
            num_zombie_walkers = {'Town04': 60, 'Town05': 60}

        # weather
        if weather_group == 'new':
            weathers = ['SoftRainSunset', 'WetSunset']
        elif weather_group == 'simple':
            weathers = ['ClearNoon']
        else:
            weathers = [weather_group]

        drivers = ['normal', 'distracted']

        
        description_folder = CARLA_GYM_ROOT_DIR / 'envs/scenario_descriptions/CogMod' / carla_map

        actor_configs_dict = json.load(open(description_folder / 'actors.json'))
        route_descriptions_dict = config_utils.parse_routes_file(description_folder / 'routes.xml')

        all_tasks = []
        for driver in drivers:
            for route_id, route_description in route_descriptions_dict.items():
                for i in range(nRepeat):
                    task = {
                        'weather': weathers[0],
                        'description_folder': description_folder,
                        'route_id': route_id,
                        'n_repeat': i,
                        'driver': driver,
                        'num_zombie_vehicles': num_zombie_vehicles[carla_map],
                        'num_zombie_walkers': num_zombie_walkers[carla_map],
                        'ego_vehicles': {
                            'routes': route_description['ego_vehicles'],
                            'actors': actor_configs_dict['ego_vehicles'],
                        },
                        'scenario_actors': {
                            'routes': route_description['scenario_actors'],
                            'actors': actor_configs_dict['scenario_actors']
                        } if 'scenario_actors' in actor_configs_dict else {}
                    }
                    all_tasks.append(task)

        return all_tasks
