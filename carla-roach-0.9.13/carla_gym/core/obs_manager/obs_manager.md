## carla_gym/core/obs_manager/obs_manager.py

As you can see, **ObsManagerBase** is a abstract class for observation manager. Below are the python scripts that contain concrete classes that implements observation manager.

- [chauffeurnet](birdview/chauffeurnet.py)
- [control](actor_state/control.py)
- [route](actor_state/route.py)
- [speed](actor_state/speed.py)
- [velocity](actor_state/velocity.py)
- [rgb](camera/rgb.py)
- [gnss](navigation/gnss.py)
- [waypoint_plan](navigation/waypoint_plan.py)
- [ego](object_finder/ego.py)
- [pedestrian](object_finder/pedestrian.py)
- [stop_sign](object_finder/stop_sign.py)
- [traffic_light_new](object_finder/traffic_light_new.py)
- [vehicle](object_finder/vehicle.py)

Here are some parts of **ObsManagerBase**:

- **__ init __** : This methods call the **_define_obs_space()** for all the observation manager that implements **ObsManagerBase**.
- **_define_obs_space()** : This returns **spaces.Dict** type or gym dictionary from concrete classes. What the dictionary contains is implementation dependent. As you can see this method is called from **__ init __**, so when the concrete class instances of observation managers are created, this method is called and gym observation space is created inside observation managers.