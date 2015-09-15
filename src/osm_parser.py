import osmapi
import numpy as np
from lxml import etree

from lib.catmull_rom_spline import catmull_rom
from lib.osm2dict import Osm2Dict
from lib.dict2sdf import GetSDF


def parse_osm(input_file_path, output_file_path):
    input_file = open(input_file_path, 'r')
    input_file_data = input_file.read()
    input_file.close()

    api = osmapi.OsmApi()
    osm_dictionary = api.ParseOsm(input_file_data)

    root = etree.fromstring(input_file_data)
    min_longitude = float(root[0].get('minlon'))
    min_latitude = float(root[0].get('minlat'))
    max_longitude = float(root[0].get('maxlon'))
    max_latitude = float(root[0].get('maxlat'))

    osm = Osm2Dict(min_longitude, min_latitude, max_longitude, max_latitude, osm_dictionary)

    road_point_width_map, model_pose_map, building_location_map = osm.getMapDetails()

    sdf_file = GetSDF()
    sdf_file.addSphericalCoords(osm.getLat(), osm.getLon())
    sdf_file.includeModel("sun")

    for building_name in building_location_map.keys():
        location = building_location_map[building_name]
        mean = location['mean']
        points = location['points']
        color = location['color']
        sdf_file.addBuilding(mean, points, building_name, color)

    print('|-----------------------------------')
    print('| Number of Roads: ' + str(len(road_point_width_map.keys())))
    print('|-----------------------------------')

    for idx, road in enumerate(road_point_width_map.keys()):
        sdf_file.addRoad(road, road_point_width_map[road]['texture'])
        sdf_file.setRoadWidth(road_point_width_map[road]['width'], road)
        points = road_point_width_map[road]['points']

        print('| Road' + str(idx + 1) + ': ' + road.encode('utf-8').strip())
        print "|  -- Width: ", str(road_point_width_map[road]['width'])

        x_data = points[0, :]
        y_data = points[1, :]

        if len(x_data) < 3:
            for j in np.arange(len(x_data)):
                sdf_file.addRoadPoint([x_data[j], y_data[j], 0], road)
        else:
            x, y = catmull_rom(x_data, y_data, 10)
            for point in range(len(x)):
                sdf_file.addRoadPoint([x[point], y[point], 0], road)

    print('|')
    print('|-----------------------------------')
    print('| Generating the SDF world file...')
    sdf_file.writeToFile(output_file_path)


if __name__ == '__main__':
    parse_osm("../resources/ny.osm", "../resources/result.sdf")
