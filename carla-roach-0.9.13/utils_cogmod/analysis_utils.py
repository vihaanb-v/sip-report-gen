
import os
import json
from matplotlib import pyplot as plt
import pandas as pd
import yaml
import carla
from utils.server_utils import CarlaServerManager


def create_df_for_collisions_with_vehicles(file_path):
    return create_df_for_collisions_with_agent_type(file_path, 'vehicle')

def create_df_for_collisions_with_pedestrians(file_path):
    return create_df_for_collisions_with_agent_type(file_path, 'pedestrian')

def create_df_for_collisions_with_moving_objects(file_path):
    ret = pd.DataFrame()
    
    collision_vehicle = create_df_for_collisions_with_agent_type(file_path, 'vehicle')
    collision_pedestrian = create_df_for_collisions_with_agent_type(file_path, 'pedestrian')

    ret = pd.concat([collision_vehicle, collision_pedestrian], ignore_index=True)

    return ret

def create_df_for_collisions_with_agent_type(file_path, agent_type='vehicle'):
    # given the file path reads the ep_stat_buffers and creates a dataframe with all the collisions with vehicles
    df = create_episode_df(file_path)
    accidents = df[df['is_route_completed_nocrash'] == False]
    ret = pd.DataFrame()
    for i in range(len(accidents)):
        row = accidents.iloc[i]
        suite = row['suite']
        run = row['run']
        file_name = os.path.join(file_path, 'diagnostics', suite, f"{run}.json")
        with open(file_name) as json_file:
            json_file = json.load(json_file)
            json_data = json_file['hero']
            # create if vehciel of pedestrian
            col_name = f'collisions_{agent_type}'
            collision_vehicle_info = json_data[col_name]
            for collision_vehicle in collision_vehicle_info:
                collision_vehicle['suite'] = suite
                collision_vehicle['run'] = run
                collision_vehicle['location'] = suite.split('_')[1]
                collision_vehicle['traffic'] = suite.split('_')[2]
                collision_vehicle['driver_type'] = run.split('_')[0]
                collision_vehicle['run_number'] = run.split('_')[-1]
                for key in ['normal_impulse', 'event_loc', 'event_rot', 'ev_loc', 'ev_rot', 'ev_vel', 'oa_loc', 'oa_rot', 'oa_vel']:
                    collision_vehicle[f"{key}_x"], collision_vehicle[f"{key}_y"], collision_vehicle[f"{key}_z"] = collision_vehicle.pop(key)
                ret = pd.concat([ret, pd.DataFrame([collision_vehicle])], ignore_index=True)
    ret = ret.round(4)
    return ret

def create_episode_df(file_path):
    df = read_episode_stat_buffers(file_path)
    # add step and simulation time to the dataframe
    for i in range(len(df)):
        file_name = os.path.join(file_path, 'diagnostics', df.loc[i, 'suite'], f"{df.loc[i, 'run']}.json")
        with open(file_name) as json_file:
            json_file = json.load(json_file)
            json_data = json_file['hero']
        df.loc[i, 'step'] = json_data['route_completion']['step']
        df.loc[i, 'simulation_time'] = json_data['route_completion']['simulation_time']
        # add another column named driver type which is the first part of the run
        df.loc[i, 'driver_type'] = df.loc[i, 'run'].split('_')[0]
        # add another column named run_number which is the second part of the run
        df.loc[i, 'run_number'] = df.loc[i, 'run'].split('_')[-1]
        # add a column named location which is the suite ("CogMod-v0_Town04_empty_simple") Town04
        df.loc[i, 'location'] = df.loc[i, 'suite'].split('_')[1]
        df.loc[i, 'traffic'] = df.loc[i, 'suite'].split('_')[2]
        # add a column named n_collision_vehicle = int(collisions_vehicle * route_completed_in_km)
        df.loc[i, 'n_collision_vehicle'] = round(df.loc[i, 'collisions_vehicle'] * df.loc[i, 'route_completed_in_km'])
        df.loc[i, 'n_collision_pedestrian'] = round(df.loc[i, 'collisions_pedestrian'] * df.loc[i, 'route_completed_in_km'])
    return df



def read_episode_stat_buffers(file_path):
    # given the file path of the project reads the ep_stat_buffers present in the folder
    ep_stat_buf_names = [f for f in os.listdir(file_path) if 'ep_stat_buffer' in f]
    data_df = pd.DataFrame()
    for f in ep_stat_buf_names:
        json_file_name = os.path.join(file_path, f)
        with open(json_file_name) as json_file:
            json_file = json.load(json_file)
            episode_dicts = json_file['hero']
            for json_file in episode_dicts:
                data_df = data_df.append(json_file, ignore_index=True)
    # remove unncecessary columns
    data_df = data_df.drop(columns=['encounter_light', 'encounter_stop', 'light_passed', 'percentage_outside_lane',
                                    'percentage_wrong_lane', 'red_light', 'route_dev', 'score_composed', 'score_penalty', 
                                    'score_route', 'stop_infraction', 'stop_passed', 'collisions_layout', 'collisions_others']) 
    data_df['is_route_completed'] = data_df['is_route_completed'].astype(bool)
    data_df['is_route_completed_nocrash'] = data_df['is_route_completed_nocrash'].astype(bool)
    data_df = data_df.round(2)
    return data_df

def get_episodes_with_driver_type(file_path, driver_type):
    df = create_episode_df(file_path)
    # if the type and driver type are the same then we return the row
    return df[df['run'].str.contains(driver_type)] 








# Scenario related functions

def get_collision_with_vehicle_scenario_with_idx(file_path, df, index, threshold=50):
    row = df.iloc[index]
    suite, run, step, other_agent_id = row['suite'], row['run'], row['step'], row['other_actor_id']
    collision_type = row['collision_type']
    file_name = os.path.join(file_path, 'diagnostics', suite, f"{run}.csv")
    ego_df = pd.read_csv(file_name)
    ego_df = ego_df[(ego_df['timestamp'] >= step - threshold) & (ego_df['timestamp'] <= step + threshold)]
    ego_df['suite'] = suite
    ego_df['run'] = run
    ego_df['driver_type'] = ego_df['run'].apply(lambda x: x.split('_')[0])
    ego_df['location'] = suite.split('_')[1]
    ego_df['collision_type'] = collision_type
    ego_df['other_actor_id'] = other_agent_id
    return ego_df

def get_collision_with_vehicle_scenario_df(file_path, df, threshold=50):
    n_row = len(df)
    dfs = []
    for i in range(n_row):
        ego_df = get_collision_with_vehicle_scenario_with_idx(file_path, df, i, threshold)
        dfs.append(ego_df)
    ret = pd.concat(dfs, ignore_index=True)
    return ret











# visualizer related functions

def plot_error_and_speed_vs_timestamp(accident_scenario_df):
    # accident scenario is a single dataframe containing all the accidents
    # we need to group the dataframe by the other actor id to detenct unique accidents 
    # and then plot the error and speed of the actor vs timestamp (starts at zero)
    grouped = accident_scenario_df.groupby('other_actor_id')
    for name, group in grouped:
        print(f"Plotting for agent {name}")
        group['timestamp'] = group['timestamp'] - group['timestamp'].min()
        group['speed'] = group['speed'].apply(lambda x: float(x[1:-1]))

        # Normalize the values manually
        for column in ['speed', 'detection_error', 'approximation_error', 'image_difference']:
            group[column] = (group[column] - group[column].min()) / (group[column].max() - group[column].min())

        plt.figure(figsize=(10, 6))
        plt.plot(group['timestamp'], group['speed'], label='Speed', color='black')
        plt.plot(group['timestamp'], group['detection_error'], label='Detection Error', color='red')
        plt.plot(group['timestamp'], group['approximation_error'], label='Approximation Error', color='green')
        plt.plot(group['timestamp'], group['image_difference'], label='Image Difference', color='blue')

        plt.axvline(x=(group['timestamp'].max() - group['timestamp'].min()) / 2, color='gray', linestyle='--')

        plt.xlabel('Timestamp')
        plt.ylabel('Normalized Value')
        plt.title(f'Normalized Analysis of Agent {name} {group["run"].iloc[0]}')
        plt.legend()
        plt.show()




def plot_accidents_vs_traffic_density(episode_df):
    # Define the order of traffic density levels for proper plotting
    traffic_order = ['empty', 'low', 'medium', 'high']
    # Group the data by driver type and traffic density
    grouped = episode_df.groupby(['driver_type', 'traffic'])
    # Create a new figure
    plt.figure(figsize=(10, 6))
    # For each driver type
    for driver_type in episode_df['driver_type'].unique():
        # Initialize lists to store traffic densities and number of accidents
        traffic_densities = []
        num_accidents = []
        # For each traffic density level
        for traffic in traffic_order:
            # If the group (driver_type, traffic) exists in the grouped DataFrame
            if (driver_type, traffic) in grouped.groups:
                # Get the group
                group = grouped.get_group((driver_type, traffic))
                # Calculate the number of accidents and append to the list
                total_accidents = group['n_collision_vehicle'].sum() + group['n_collision_pedestrian'].sum()
                num_accidents.append(total_accidents)
                # Append the traffic density to the list
                traffic_densities.append(traffic)
        # Plot the number of accidents against traffic density for the current driver type
        plt.plot(traffic_densities, num_accidents, marker='o', label=driver_type)
    plt.xlabel('Traffic Density')
    plt.ylabel('Number of Accidents')
    plt.title('Number of Accidents vs Traffic Density')
    plt.legend()
    plt.show()

def plot_accidents_vs_traffic_density_from_accident_df(accidents_df):
    # Define the order of traffic density levels for proper plotting
    traffic_order = ['empty', 'low', 'medium', 'high']
    # Group the data by driver type and traffic density
    grouped = accidents_df.groupby(['driver_type', 'traffic'])
    # Create a new figure
    plt.figure(figsize=(10, 6))
    # For each driver type
    for driver_type in accidents_df['driver_type'].unique():
        # Initialize lists to store traffic densities and number of accidents
        traffic_densities = []
        num_accidents = []
        # For each traffic density level
        for traffic in traffic_order:
            # If the group (driver_type, traffic) exists in the grouped DataFrame
            if (driver_type, traffic) in grouped.groups:
                # Get the group
                group = grouped.get_group((driver_type, traffic))
                # Calculate the number of accidents and append to the list
                num_accidents.append(len(group))
            else:
                # If no accidents for this traffic type, append 0
                num_accidents.append(0)
            # Append the traffic density to the list
            traffic_densities.append(traffic)
        # Plot the number of accidents against traffic density for the current driver type
        plt.plot(traffic_densities, num_accidents, marker='o', label=driver_type)
    plt.xlabel('Traffic Density')
    plt.ylabel('Number of Accidents')
    plt.title('Number of Accidents vs Traffic Density')
    plt.legend()
    plt.show()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
# replay related functions
def read_config(config_path):
    with open(config_path, 'r') as file:
        cfg = yaml.safe_load(file)
    return cfg

def init_client(host, port):
    try:
        client = carla.Client(host, port)
        print(f"client connected to {host}:{port}")
        print(f"client.get_server_version(): {client.get_server_version()}, client.get_client_version(): {client.get_client_version()}")
        client.set_timeout(60.0)
    except RuntimeError as re:
        if "timeout" not in str(re) and "time-out" not in str(re):
            print("Could not connect to Carla server because:", re)
        client = None 
    return client

# Assuming 'client' is already initialized and is an instance of carla.Client
# The path to your recorder log file

def run_replay(config_path, recorder_file_path, actor_id, start_time, duration):
    cfg = read_config(config_path)
    server_manager = CarlaServerManager(cfg['carla_sh_path'], cfg['port'], t_sleep=5)
    server_manager.stop()
    server_manager.start()

    client = init_client(cfg['host'], cfg['port'])
    # Check if file exists
    try:
        with open(recorder_file_path, 'r') as file:
            print(f"File found: {recorder_file_path}")
    except FileNotFoundError:
        print(f"File not found: {recorder_file_path}")
        exit()
    try:
        # Corrected call to replay_file
        replay_result = client.replay_file(
            recorder_file_path,
            time_start=start_time,  # Explicitly specifying as double
            duration=duration,    # Explicitly specifying as double
            follow_id=actor_id,     # This is already an int, but making sure it's clearly specified
            replay_sensors=True  # Assuming you want to replay sensors, adjust as necessary
        )
        print("Replaying recorded log file...")
    except Exception as e:
        print(f"An error occurred while trying to replay the file: {e}")