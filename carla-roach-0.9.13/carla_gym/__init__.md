## carla_gym/init.py

There are several environments that are implemented in **carla_gym**. The environments are registered in **carla_gym/__init__.py** file. The environment ids are : 
- NoCrash-v0
- NoCrash-v1
- NoCrash-v2
- NoCrash-v3
- CoRL2017-v0
- CoRL2017-v1
- CoRL2017-v2
- CoRL2017-v3
- Endless-v0
- LeaderBoard-v0

After the environments are declared in **_AVAILABLE_ENVS** dictionary, they are iterated and registered by **register()** method from **gym.envs.registration**.