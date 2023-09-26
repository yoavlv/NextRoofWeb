import math


def calc_distance_from_the_see_TLV(X_coordinate, Y_coordinate):
    north_x = 180471
    north_y = 672391
    south_x = 177333
    south_y = 663016

    m = (south_y - north_y) / (south_x - north_x)
    b = north_y - (m * north_x)

    numerator = abs(m * X_coordinate - Y_coordinate + b)
    denominator = math.sqrt(m**2 + 1)
    return numerator / denominator


def calc_distance_from_train_station(x, y):
    stations = [(179820.47, 662424.54), (180619, 664469.56),
                (181101.44, 665688.78), (181710.96, 667877.05)]
    distances = [
        abs(station[0] - x) + abs(station[1] - y) for station in stations
    ]
    min_distance = min(distances)
    return min_distance
