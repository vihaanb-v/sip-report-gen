## carla_gym/core/obs_manager/obs_manager_handler.py

Below are several parts of **ObsManagerHandler** class.

- **__ init__()**
  - **self._obs_managers** : It a dictionary that contains observation manager for a given ego vehicle id and observation id. There can be several such observation managers.
  - **self._obs_configs** : It contains the observation configuration dictionary that is passed as argument to the constructor of **ObsManagerHandler** class. Here is an example of such dictionary presented in yaml format for readability.
    
        hero:
            obs_configs:
                birdview:
                    module: birdview.chauffeurnet
                    width_in_pixels: 192
                    pixels_ev_to_bottom: 40
                    pixels_per_meter: 5.0
                    history_idx:
                    - -16
                    - -11
                    - -6
                    - -1
                    scale_bbox: true
                    scale_mask_col: 1.0
                speed:
                    module: actor_state.speed
                control:
                    module: actor_state.control
                velocity:
                    module: actor_state.velocity

    Here **hero** is the ego vehicle id and **birdview, speed, control and velocity** are observation ids.
  - **_init_obs_managers()** method is called to create several observation managers based on yaml document and stored in **self._obs_managers** dictionary.
- **observation_space()** : The reason to use property method, is to make composite dictionary gym space. **self._obs_managers** contains key value pair between ego vehicle id and another dictionary. The inner dictionary contains key value pair between observation ids and observation manager instance. Same structure is followed in **obs_spaces_dict** local variable. Only difference is the dictionaries are gym dictionaries instead of python dictionaries. Also, the inner dictionary contains key value pair between observation ids and observation spaces of observation managers. More about observation managers [here](obs_manager.md)
- **self._init_obs_managers()** : 
  
  - It is used to populate **self._obs_managers** dictionary. 
  - If we use the above observation configuration example shown in **__ init__()** method paragraph, then on the first iteration of the outer loop **ev_id** is **hero** and **ev_obs_configs** contains the part after **hero** in dictionary format. Then in the inner loop, there will be four iterations. The observation id **obs_id** are **birdview, speed, control and velocity**. The **module** part is used to bring the class instance of observation manager. For example, for **birdview** observation id, the class **ObsManager** is from **carla_gym/core/obs_manager/birdview/chauffeurnet.py**. More about observation manager [here](obs_manager.md).
- **reset()**:
  
  - **ego_vehicles** is dictionary where key is the ego vehicle id and value is associated [**TaskVehicle**](../task_actor/common/task_vehicle.py)
  - **_init_obs_managers()** is called to populate **self._obs_managers** dictionary.
  - In the **for loop** the observation manager is attached to its associated [**TaskVehicle**](../task_actor/common/task_vehicle.py).