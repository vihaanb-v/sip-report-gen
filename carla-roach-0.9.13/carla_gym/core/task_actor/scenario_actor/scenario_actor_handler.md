# carla_gym/core/task_actor/scenario_actor/scenario_actor_handler.py

- This class is used to handle **ScenarioActor** agents. They are different from ego vehicle and traffic manager generated zombie vehicles as their routes and actions are predetermined. They can be seen to be used in carla scenario runner.
- **__init__()** :
 
  - **self.scenario_actors** : It is a dictionary between scenario actor id and **TaskVehicle** objects.
  - **self.scenario_agents** : It is a dictionary between scenario agent id and agents implemented in **carla_gym/core/task_actor/scenario_actor/agents**.
  - **self._client** : It is a carla client instance.
  - **self._world** : It is carla world instance.
- **reset()**:
 
  -  **self.hero_vehicles** contains instance of **TaskVehicle** class.
  -  **actor_config** contains scenario actor configuration.
  -  **route_config** contains the route configuration associated with the scenario actor.
  -  Every scenario actor in **actor_config** is iterated
    
     -  **bp_filter** contains the blueprint regex expression based on the scenario actor id **sa_id** and vehicle **model**.
     -  **blueprint** contains the blueprint name that is chosen randomly by using **bp_filter**.
     -  **role_name** attribute of **blueprint** is set to **sa_id** which is scenario actor id.
     -  **spawn_transform** contains the carla transform where the above scenario actor with **sa_id** will be spawned. It is the first element of **route_config[sa_id]** list.
     -  **carla_vehicle** contains the carla vehicle instance that is spawned using **blueprint** and **spawn_transform**.
     -  **self._world.tick()** as the environment is asynchronous and vehicle will not spawn until next tick.
     -  **target_transforms** contains the target carla transformation the spawned vehicle must follow that is excluding the transformation where the vehicle was spawned.
     -  **self.scenario_actors[sa_id]** contains the instance of [**TaskVehicle**](../common/task_vehicle.py)
     -  **AgentClass** contains [**BasicAgent**](./agents/basic_agent.py) or [**ConstantSpeedAgent**](./agents/constant_speed_agent.py) based on **module_str** and **class_str**.
     -  **self.scenario_agents[sa_id]** contains the object instance of **AgentClass**.
- **tick()**:
  - Predetermined control action are applied to the scenario actors.
  - **tick()** method of [**TaskVehicle**](../common/task_vehicle.md) is then called.