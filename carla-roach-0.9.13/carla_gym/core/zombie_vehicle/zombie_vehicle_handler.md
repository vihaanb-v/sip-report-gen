# carla_gym/core/zombie_vehicle/zombie_vehicle_handler.py

- **__init__()**
  
  - **self._logger** : It is used to log important messages.
  - **self.zombie_vehicles** : This is a dictionary where the key is zombie vehicle id and value is **ZombieVehicle** object.
  - **self._client** : It contains carla client instance.
  - **self._world** : It contains carla world instance.
  - **self._spawn_distance_to_ev** : This is the minimum distance from ego vehicle from which the zombie vehicles will be spawned.
  - **self._tm_port** : This is the port where traffic manager is connected.

- **reset()**
  
  - **num_zombie_vehicles** can be list of two integers or one single integers. If this is a list of two integers then, a random integer is selected and placed in **n_spawn** variable. Otherwise, **num_zombie_vehicles** is assigned to **n_spawn** variable.
  - **filtered_spawn_points** contains spawn points that are minimum **self._spawn_distance_to_ev** meter distance from the spawned ego vehicles using the  **_filter_spawn_points()** method.
  - **filtered_spawn_points** are randomly shuffled.
  - **_spawn_vehicles()** method is called to generate **n_spawn** number of **ZombieVehicle** instances.


- **_filter_spawn_points()**

  - It filters out spawn points that are in **self._spawn_distance_to_ev** meter distance of any spawned ego vehicle. 

- **_spawn_vehicles()**
  
  - **blueprints** contains all the vehicle blueprints.
  - **SpawnActor**, **SetAutopilot** and **FutureActor** are different carla commands.
  - **spawn_transforms** is iterated.
  
    - A random **blueprint** is selected from **blueprints**.
    - Different attributes of **blueprint** are set.
    - **batch** list appended with carla command that first spawns a actor based on the **blueprint** and **transform** and then sets the spawned actor to autopilot mode.
  - **self._client.apply_batch_sync()** method is applied to the **batch** and responses are generated which are then iterated.
  
    - If the **response** does not contain error, then **zombie_vehicle_ids** list is appended with response actor id.
  - **zombie_vehicle_ids** list is then iterated in which **zombie_vehicles** dictionary is set to have key **zv_id** and associated value **ZombieVehicle** object instance.
