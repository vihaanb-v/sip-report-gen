import numpy as np



def measure_detection_error(gt_vehicles, gt_walkers, mod_vehicles, mod_walkers):
    d_vehicle = len(gt_vehicles) - len(mod_vehicles)
    d_walker = len(gt_walkers) - len(mod_walkers)
    
    n_gt_agent = len(gt_vehicles) + len(gt_walkers)
    n_mod_agent = len(mod_vehicles) + len(mod_walkers)
    
    detection_ratio = n_mod_agent / (n_gt_agent + 1e-5)
    detection_error = 1 - detection_ratio
    if n_gt_agent == 0 and n_mod_agent == 0:
        detection_error = 0
    # print("total gt agents: ", n_gt_agent, " total mod agents: ", n_mod_agent)
    # print(' ratio ', np.round(detection_error, 2))
    return detection_error

def measure_perception_error(gt_vehicles, gt_walkers, mod_vehicles, mod_walkers):
    
    distance_sum = 0
    # each actor is in the form ((loc, rot), id, extent)
    # find the distance between each gt with mod vehicle
    distance_threshold = 1.0
    extent_threshold = 0.001

    for i in range(len(gt_vehicles)):
        gt_vehicle = gt_vehicles[i]
        min_distance = 100000
        for j in range(len(mod_vehicles)):
            mod_vehicle = mod_vehicles[j]
            distance = gt_vehicle[0].location.distance(mod_vehicle[0].location)
            extent_diff = (gt_vehicle[2].x-mod_vehicle[2].x) + (gt_vehicle[2].y-mod_vehicle[2].y)
            if distance < min_distance:
                min_distance = distance
        if min_distance < distance_threshold and extent_diff < extent_threshold:
            distance_sum += min_distance

    for i in range(len(gt_walkers)):
        gt_walker = gt_walkers[i]
        min_distance = 100000
        for j in range(len(mod_walkers)):
            mod_walker = mod_walkers[j]
            distance = gt_walker[0].location.distance(mod_walker[0].location)
            extent_diff = (gt_walker[2].x-mod_walker[2].x) + (gt_walker[2].y-mod_walker[2].y)
            if distance < min_distance:
                min_distance = distance
        if min_distance < distance_threshold and extent_diff < extent_threshold:
            distance_sum += min_distance
    
    # print('distanace sum', distance_sum)
    return distance_sum

def measure_image_difference(gt_image, mod_image):
    # gt_image and mod_image are PIL images
    # convert to numpy array
    # gt_image = np.array(gt_image)
    # mod_image = np.array(mod_image)
    # calculate the difference
    diff = np.abs(gt_image - mod_image)
    # calculate the sum of the difference
    diff_sum = np.sum(diff)
    # normalize the difference
    # diff_sum = diff_sum / (gt_image.shape[0] * gt_image.shape[1] * gt_image.shape[2])
    return diff_sum

