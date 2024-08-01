# class WeatherHandler
- **__ init __()**:
  - **self._world** : Carla world instance.
  - **self._dynamic** : Whether the weather dynamically changes after **reset()** method is called.
- **reset()**: It first checks if **carla.WeatherParameters** has attribute described in **cfg_weather** (for example, "ClearNoon"). If so, then the carla world weather is set to it. For example, for "ClearNoon", it will be **carla.WeatherParameters.ClearNoon**. If "dynamic" is found in the string that is stored in **cfg_weather**, a dynamic weather is set with **Sun** and **Storm** class. After each tick if **self._dynamic** is **true**, weather conditions are changed. If both conditions are false, then by default the weather is set to "ClearNoon".
- **tick()**: If **self._dynamic** is **true**, the weather conditions are changed which is self explanatory. 
- **clean()**: If **self._dynamic** is **true**, severals variables are set to **None** as they are only created when **self._dynamic** is true. See **reset()** method's **elif** block. Then **self._dynamic** is set to false.