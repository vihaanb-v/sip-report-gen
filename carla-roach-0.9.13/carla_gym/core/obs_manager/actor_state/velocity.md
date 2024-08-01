- **get_observation()**
  - It gets the transformation, acceleration, velocity, and angular velocity of the ego vehicle in the global/world coordinate system.
  - It uses the **trans_utils.vec_global_to_ref()** function to convert the global acceleration and velocity to the ego vehicle's reference frame. This effectively transforms these values from global/world coordinates to the ego vehicle's local coordinates.
  - The resulting observations, **acc_xy, vel_xy, and vel_ang_z**, are then returned as a dictionary, representing the ego vehicle's state in its local reference frame.
  - These values are initialized ase below,

        {
            'acc_xy': np.array([acc_ev.x, acc_ev.y], dtype=np.float32),
            'vel_xy': np.array([vel_ev.x, vel_ev.y], dtype=np.float32),
            'vel_ang_z': np.array([ang_w.z], dtype=np.float32)
        }