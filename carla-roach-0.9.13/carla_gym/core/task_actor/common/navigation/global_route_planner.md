- **__init __()** :
  - **self._map** : It contains carla map instance.
  - **self._resolution** : This is the maximum distance in meter between two waypoints in the **self._topology** variable.
  - **self._topology** : This contains modified topology from **self._map.get_topology()** where waypoints are maximum  resolution meter apart. The segment information is stored in a dictionary format. See [this](map_utils.md)
  - **self._intersection_end_node** : 
  - **self._previous_decision** : It contains the previous turn decision based on [RoadOption](map_utils.py).
  - **_build_graph()**, **_find_loose_ends()** and **_lane_change_link()** methods are called which are described below.
- **_build_graph** :
  - **graph** : It is an instance of networkx directed graph. 
  - **id_map** : It is a dictionary which maps (x,y,z) to node id.
  - **road_id_to_edge** : It is a dictionary that maps road id, section id, lane id to the edge in the graph.
  - In the **for loop** each road information stored in **segment** is iterated.
    - **entry_xyz** : It contains x, y, z values of the entry waypoint of the road as tuple.
    - **exit_xyz** : It contains x, y, z values of the exit waypoint of the road as tuple.
    - **path** : It is a list of waypoints separated by predefined meters apart from each other excluding the the entry and exit waypoint from entry to exit waypoint.
    - **entry_wp** : Entry waypoint of a road.
    - **exit_wp** : Exit waypoint of a road.
    - **intersection** : Boolean variable to determine if the waypoint is in a road intersection.
    - **road_id, section_id, lane_id** : These contains the road id, section id and lane id where the waypoint belongs.
    - In the **for loop**, **entry_xyz** and **exit_xyz** is iterated consecutively. They are given unique ids based on length of **id_map**. If they are already with an unique id, this process is not done. Lastly, the id is added as node to graph and (x, y, z) coordinate of entry and exit is added as keyword argument **vertex**.
    - **n1** : It contains the identifier for the entry vertex of the **segment**.
    - **n2** : It contains the identifier for the exit vertex of the **segment**.
    - **road_id_to_edge** is the map of road id, section id, lane id of entry waypoint to the directed edge of the graph which is from **n1** to **n2**.
    - **entry_carla_vector** : This is the forward vector associated with entry waypoint of the road segment.
    - **exit_carla_vector** : This is the forward vector associated with exit waypoint of the road segment.
    - An edge is added to the graph using **n1** and **n2** as well as necessary keyword arguments.
  - After the whole **self._topology** is iterated, **graph**, **id_map** and **road_id_to_edge** is returned.
- **_find_loose_ends()** : In **_build_graph** method the key of **road_id_to_edge** is built from entry waypoint of a road segment. If the topology graph is not connected, there may be exit way point of road segment which will be dead end. This method finds those waypoints and tries to connect them with new exit way points. Though this new points may be dead points also. 
- **_lane_change_link()** : A road can have several lanes. According to traffics rules, a vehicle can sometimes change its lane and sometimes cannot switch lanes. As we can see from **_build_graph** method every edge is associated with a road, segment and lane. When calculating the edge lane change does not occur. So, if traffic rules allows lane changes, there is no zero cost edge in the graph to make it happen despite the graph being connected. Some kind of cost must be incurred to change adjacent lanes. But this does not make any sense. This method adds zero cost edges to graph for adjacent lane change. 
  - In the **for loop** every **segment** in the **self._topology** is iterated
    - **left_found** : True if edge associated with left lane change is found.
    - **right_found** : True if edge associated with right lane change is found. 
    - In the **inner for loop** every waypoint in the **segment["path"]** variable is traversed.
      - If the **waypoint** is not in a junction,
        - Then, it is checked if lane change is permitted for the **waypoint**
          - If so, **next_waypoint** contains the waypoint in the right/left lane. 
          - If **next_waypoint** exists, is a driving lane and is in the same road as **waypoint**, then
            - **next_road_option** contains **RoadOption.CHANGELANERIGHT/RoadOption.CHANGELANELEFT**.
            - **next_segment** contains graph edge associated with **next_waypoint**.
              - If **next_segment** exists, then a graph edge is created using above variables and information and **right_found/left_found** is true.
      - If both zero cost edge associated with **segment** is found, then the loop breaks as a lane cannot have other lanes than left and right.
- **_localize()** : Self-explanatory from the code comments. It mainly returns a graph edge associated with a given location.
- **trace_route()**:

  - **origin** and **destination** both are Carla location.
  - **route_trace** is a list of 
  - **route** contains the list of nodes from **origin** to **destination** 
  -  **current_waypoint** is the waypoint associated with **origin**.
  -  **destination_waypoint** is the waypoint associated with **destination**.
  -  In the **for loop**
     
     - **road_option** is an enum described in [RoadOption](map_utils.py). It is calculated by **_turn_decision()**. It says if the ego vehicle should go straight, follow the lane, go left or go right. The edge between nodes have **type** attribute which also contains [RoadOption](map_utils.py). So why this is needed? It is because of intersections. To smoothly navigate the intersection, the car has to turn left or right before encountering an edge of type left or right.
     - **edge** defines the edge between current node and next node of the route list.
     - If the type of the edge tells to go straight, left, right or change lane to left or right, then :
      
        -   **route_trace** list is appended with tuple of **current_waypoint** and **road_option**.
        -   **exit_wp** is the exit waypoint of the **edge**
        -   We get **n1** and **n2** from **self._road_id_to_edge** dictionary which was constructed and modified in **_build_graph()** and **_find_loose_ends()** methods.
        -   **next_edge** is built from **n1** and **n2**.
        -   **path** attribute of edges is described in **_build_graph()** method of [GlobalRoutePlanner](global_route_planner.py) and **get_sampled_topology()** method of found [here](map_utils.py).
        -   If **path** attribute of **next_edge** exists,
            -   **closest_index** is the index of a waypoint in the **path** of **next_edge** that is closest to **current_waypoint**.
            -  **closest_index** is modified to be the last index or 5 index away from the current one.
            -  **current_waypoint** is set to waypoint having the **closest_index**.
        - else:
          -  **current_waypoint** is set to **exit_waypoint** of the **next_edge**.
        - **route_trace** list appended with **current_waypoint** and **road_option**.
      - else,
  
        - **path** list is appended with the waypoints in the current **edge**.
        - **closest_index** is the index of a waypoint in **path** list that is closest to the **current_waypoint**.
        - In the **for** loop, 

          - **waypoint** is assigned to **current_waypoint**.
          - **trace_route** is appended with **current_waypoint** and **road_option**
          - If **i** is second last and distances between **waypoint** and **destination** is less than some threshold, then the for is concluded.
          - else if **i** is second last and **current_waypoint** and **destination_waypoint** are in the same road, 
            - **destination_index** is found by **_find_closest_in_list()** method.
            - if **closest_index** is greater than **destination_index**, then the for loop is concluded.   
-  **_path_search()**:

   - **start** denotes the start edge that is associated with **origin** and **end** denotes the end edge that is associated with **destination**. Both are calculated by **_localize()**.
   - As a result, the **source** argument and **target** argument of  **nx.astar_path** contains the first node of both **origin** and **end** respectively. See what other arguments do [here](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.astar.astar_path.html)
   - **nx.astar_path** returns a list of nodes from origin to end which stored in the **route**. **route** is appended with second node of **end** as it is not contained in the **route**. 
- **_successive_last_intersection_edge()**:

  - Self explanatory from the comments.
  - Basically, it starts from the **index** node and consecutively calculates **candidate_edge** from current node and next node in the for loop.
  - If **candidate_edge** is in intersection and the ego vehicle have to follow the lane while in this edge, the loop will go on. Otherwise, it will break returning last such edge and associated last node.
- **_turn_decision()**:
  
  - It returns [RoadOption](map_utils.py) based on current **index** of the **route** list.
  - **decision** variable is initiated to **None**. **previous_node, current_node, next_node, next_edge** is calculated from the **route** list.
  - If the value of **index** is 0, then **decision** is based on the type of **next_edge**.
  - If the value of **index** is greater than 0

    - Decision will be same as previous decision if all of the below holds,
    
      - Previous decision was going left, right, straight, following lane, changing to left lane, changing to right lane as **self._previous_decision != RoadOption.VOID**.
      - We are currently in an intersection as **self._intersection_end_node > 0 and self_intersection_end_node != previous_node**
      - The next edge is to follow the lane
      - The next edge is in an intersection
    - If any of the above is not true then,
      - **self._intersection_end_node** is initialized to -1.
      - **current_edge** is calculated from **previous_node** and **current_node**.
      - **calculate_turn** is a decision variable. If in the current edge and in the next edge, we have to follow the lane and the next edge is in an intersection but the current edge is not, then we have to calculate if we have to take a turn.
      - if **calculate_turn** is true, then 
        - **tail_edge** is the last edge that is in an intersection having the criteria to follow the lane while in this edge. **last_node** is the second node of **tail_edge** meaning the last node of on going road intersection. Both are calculated by **self._successive_last_intersection_edge** method.
        - **self._intersection_end_node** is assigned the **last_node**.
        - If we successfully calculated the **tail_edge**, then the **next_edge** becomes the **tail_edge**.
        - **cv** is the exit vector of the current edge.
        - **nv** is the exit vector of the next edge.
        - If **cv** or **nv** does not exist the type of the **next_edge** is returned.
        - As we can see above that **next_edge** can become the **tail_edge**. As a result, **next_edge** is not immediate to **current_edge**.
        - For every successor node of the current node that is not in the route list, we get the net vector **sv** between current node and immediate successor node from the edge between these two nodes. **cross_list** is then appended with value of z component of cross product of **cv** and **sv**.
        - **next_cross** contains the value of z component of cross product of **cv** and **nv**.
        - **deviation** contains the angle between **cv** and **nv** in radian.
        - If **cross_list** is empty, it is appended with 0.
        - If **deviation** is less than **threshold**, then the decision is to go straight.
        - If **next_cross** is smaller than the smallest element of **cross_list** or smaller than 0, then the decision is to turn left.
        - If **next_cross** is greater than the greatest element of **cross_list** or greater than 0, then the decision is to turn right.
      - If we do not have to calculate turn, then the decision is based on the type of the **next_edge**.
  - If index value is less than or equal to 0, hen the decision is based on the type of the **next_edge**.
  - **self._previous_decision = decision** is assigned the calculated **decision**
  - **decision** is then returned.
- **_find_closest_in_list()**:

  - This method returns index of the closet waypoint in a waypoint list with respect to a provided waypoint.