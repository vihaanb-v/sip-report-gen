- I am going to describe the content of this script later.
- **get_observation()**
  - This method returns an observation dictionary initialized as below,

        {
            'frame': self._world.get_snapshot().frame,
            'binary_mask': np.array(binary_mask, dtype=np.int8),
            'location': np.array(location, dtype=np.float32),
            'rotation': np.array(rotation, dtype=np.float32),
            'absolute_velocity': np.array(absolute_velocity, dtype=np.float32),
            'extent': np.array(extent, dtype=np.float32),
            'on_sidewalk': np.array(on_sidewalk, dtype=np.int8),
            'road_id': np.array(road_id, dtype=np.int8),
            'lane_id': np.array(lane_id, dtype=np.int8)
        }
    Here all the key except for 'frame' is an array that contain essential information about a maximum number of pedestrians in a certain range of the ego vehicle. All of them is sorted in ascending order based on the distance of the pedestrian with respect to the ego vehicle.        