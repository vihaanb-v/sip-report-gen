# carla_gym/core/zombie_walker/zombie_walker_handler.py

Here I describe several parts of **ZombieWalkerHandler** class.

- **self._logger**: It is used to log information in python.
- **self.zombie_walkers** : This a dictionary where the key is walker id and value is **ZombieWalker** object found in **carla_gym/core/zombie_walker/zombie_walker.py** file.
- **self._client** : This contains carla client instance.
- **self._world** : This contains carla world instance.
- **self._spawn_distance_to_ev** : This is the distance from ego vehicle from where the walker will be spawned.
- **clean()** : This method gets the list of alive walkers from the carla server. Then from the **self.zombie_walkers** list, if a walker is in the live walker list, it calls **clean** method upon the live walker instance. 