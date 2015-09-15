import osmapi
import numpy as np

from lib.laneBoundaries import LaneBoundaries
from lib.catmull_rom_spline import catmull_rom
from lib.osm2dict import Osm2Dict
from lib.dict2sdf import GetSDF
from lxml import etree


class OSMBoundingBox(object):
    def __init__(self, min_latitude, max_latitude, min_longitude,
                 max_longitude):
        self.min_latitude = min_latitude
        self.max_latitude = max_latitude
        self.min_longitude = min_longitude
        self.max_longitude = max_longitude


class OSMFile(object):
    def __init__(self, input_file_path):
        input_file = open(input_file_path, 'r')
        self.input_file_data = input_file.read()
        input_file.close()

    def get_bounding_box(self):
        root = etree.fromstring(self.input_file_data)
        minlat = float(root[0].get('minlat'))
        maxlat = float(root[0].get('maxlat'))
        minlon = float(root[0].get('minlon'))
        maxlon = float(root[0].get('maxlon'))
        return OSMBoundingBox(minlat, maxlat, minlon, maxlon)

    def get_osm_dictionary(self):
        api = osmapi.OsmApi()
        result = api.ParseOsm(self.input_file_data)
        return result

    def write_to_SDF(self, output_file_path):
        osm_dictionary = self.get_osm_dictionary()
        bounding_box = self.get_bounding_box()
        osm = Osm2Dict(
            bounding_box.min_longitude,
            bounding_box.min_latitude,
            bounding_box.max_longitude,
            bounding_box.max_latitude,
            osm_dictionary)

        roadPointWidthMap, modelPoseMap, buildingLocationMap = osm.getMapDetails()

        sdfFile = GetSDF()
        sdfFile.addSphericalCoords(osm.getLat(), osm.getLon())
        sdfFile.includeModel("sun")
        # for model in modelPoseMap.keys():
        #     points = modelPoseMap[model]['points']
        #     if len(points) > 2:
        #         sdfFile.addModel(modelPoseMap[model]['mainModel'],
        #                          model,
        #                          [points[0, 0], points[1, 0], points[2, 0]])

        for building in buildingLocationMap.keys():
            sdfFile.addBuilding(buildingLocationMap[building]['mean'],
                                buildingLocationMap[building]['points'],
                                building,
                                buildingLocationMap[building]['color'])

        print('|-----------------------------------')
        print('| Number of Roads: ' + str(len(roadPointWidthMap.keys())))
        print('|-----------------------------------')

        lanes = 0

        roadLaneSegments = []
        centerLaneSegments = []
        laneSegmentWidths = []

        # Include the roads in the map in sdf file
        for idx, road in enumerate(roadPointWidthMap.keys()):
            sdfFile.addRoad(road, roadPointWidthMap[road]['texture'])
            sdfFile.setRoadWidth(roadPointWidthMap[road]['width'], road)
            points = roadPointWidthMap[road]['points']

            print('| Road' + str(idx + 1) + ': ' + road.encode('utf-8').strip())

            laneSegmentWidths.append(roadPointWidthMap[road]['width'])
            print "|  -- Width: ", str(roadPointWidthMap[road]['width'])

            xData = points[0, :]
            yData = points[1, :]

            if len(xData) < 3:

                x = []
                y = []
                lanePoint = []

                for j in np.arange(len(xData)):
                    sdfFile.addRoadPoint([xData[j], yData[j], 0], road)
                    lanePoint.append([xData[j], yData[j]])
                    x.append(xData[j])
                    y.append(yData[j])

                roadLaneSegments.append([lanePoint, lanePoint])
                centerLaneSegments.append([x, y])

            else:

                x, y = catmull_rom(xData, yData, 10)

                centerLaneSegments.append([x, y])

                lanes = LaneBoundaries(x, y)
                for point in range(len(x)):
                    sdfFile.addRoadPoint([x[point], y[point], 0], road)
                    # sdfFile.addRoadDebug([x[point], y[point], 0], road)

        print('|')
        print('|-----------------------------------')
        print('| Generating the SDF world file...')
        sdfFile.writeToFile(output_file_path)

if __name__ == '__main__':
    input_file_path = "../resources/ny.osm"
    output_file_path = "../resources/result.sdf"
    osm_file = OSMFile(input_file_path)
    osm_file.write_to_SDF(output_file_path)
