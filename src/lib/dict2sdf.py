##############################################################################
# Author: Tashwin Khurana
# Version: 1.0
# Package: gazebo_osm
#
# Description: GetSDF() class
#             Builds a sdf file by adding models and seting their properties,
#             roads and sets spherical coordinates for the world
##############################################################################

import lxml.etree as Et
# import xml.dom.minidom as minidom
import numpy


class GetSDF:
    def __init__(self):
        self.sdf = Et.Element('sdf')
        self.sdf.set('version', "1.4")
        world = Et.SubElement(self.sdf, 'world')
        world.set('name', 'default')
        self.modelList = dict()

    def addSphericalCoords(self, latVal, lonVal,
                           elevationVal=0.0, headingVal=0):
        ''' Add the spherical coordinates for the map'''
        spherical_coordinates = Et.SubElement(self.sdf.find('world'),
                                              'spherical_coordinates')

        model = Et.SubElement(spherical_coordinates, 'surface_model')
        model.text = "EARTH_WGS84"

        lat = Et.SubElement(spherical_coordinates, 'latitude_deg')
        lat.text = str(latVal)

        lon = Et.SubElement(spherical_coordinates, 'longitude_deg')
        lon.text = str(lonVal)

        elevation = Et.SubElement(spherical_coordinates, 'elevation')
        elevation.text = str(elevationVal)

        heading = Et.SubElement(spherical_coordinates, 'heading_deg')
        heading.text = str(headingVal)

    def addGround(self, width, height):
        ground = Et.SubElement(self.sdf.find('world'), 'model')
        ground.set('name', 'ground')

        static = Et.SubElement(ground, 'static')
        static.text = "true"

        link = Et.SubElement(ground, 'link')
        link.set('name', "link")

        collision = Et.SubElement(link, 'collision')
        collision.set('name', 'collision')
        Et.SubElement(collision, 'pose').text = '0 0 0 0 0 0'

        geometry = Et.SubElement(collision, 'geometry')
        plane = Et.SubElement(geometry, 'plane')
        Et.SubElement(plane, 'size').text = str(width) + ' ' + str(height)
        Et.SubElement(plane, 'normal').text = '0 0 1'

        surface = Et.SubElement(collision, 'surface')
        friction = Et.SubElement(surface, 'friction')
        ode = Et.SubElement(friction, 'ode')
        Et.SubElement(ode, 'mu').text = '100'
        Et.SubElement(ode, 'mu2').text = '50'

        visual = Et.SubElement(link, 'visual')
        visual.set('name', 'visual')
        Et.SubElement(visual, 'pose').text = '0 0 -1 0 0 0'

        geometry = Et.SubElement(visual, 'geometry')

        plane = Et.SubElement(geometry, 'plane')
        Et.SubElement(plane, 'normal').text = '0 0 1'
        Et.SubElement(plane, 'size').text = str(width) + ' ' + str(height)

        material = Et.SubElement(visual, 'material')
        script = Et.SubElement(material, 'script')
        Et.SubElement(script, 'uri').text = 'file://media/materials/scripts/gazebo.material'
        Et.SubElement(script, 'name').text = 'Gazebo/Grass'


    def addScene(self, grid, origin_visual):
        scene = Et.SubElement(self.sdf.find('world'), 'scene')

        Et.SubElement(scene, 'grid').text = str(grid).lower()
        Et.SubElement(scene, 'origin_visual').text = str(origin_visual).lower()


    def includeModel(self, modelName):
        ''' Include models in gazebo database'''
        includeModel = Et.SubElement(self.sdf.find('world'), 'include')
        includeUri = Et.SubElement(includeModel, 'uri')
        includeUri.text = "model://" + modelName
        return includeModel

    def addModel(self, mainModel, modelName, pose):
        '''Add model with pose and the name taken as inputs'''

        includeModel = self.includeModel(mainModel)

        model = Et.SubElement(includeModel, 'name')
        model.text = modelName

        static = Et.SubElement(includeModel, 'static')
        static.text = 'true'

        modelPose = Et.SubElement(includeModel, 'pose')

        modelPose.text = (str(pose[0]) +
                          " " + str(pose[1]) +
                          " " + str(pose[2]) + " 0 0 0")

    def addRoad(self, roadName, roadType):
        '''Add road to sdf file'''
        road = Et.SubElement(self.sdf.find('world'), 'road')
        road.set('name', roadName)
        # roadMaterial = Et.SubElement(road, 'material')
        # script = Et.SubElement(roadMaterial, 'script')
        # Et.SubElement(script, 'uri').text = ('file://media/materials/' +
        #                                      'scripts/gazebo.material')
        # Et.SubElement(script, 'name').text = 'Gazebo/Black'

    # Adds little box to display location of osm gps point in world
    def addRoadDebug(self, pose, roadName):
        boxModel = self.addModel('wood_cube_10cm', roadName + '_leftLane_debug', pose)

    def addLeftLaneDebug(self, pose, roadName):
        boxModelL = self.addModel('wood_cube_10cm', roadName + '_rightLane_debug', pose)

    def addRightLaneDebug(self, pose, roadName):
        boxModelR = self.addModel('wood_cube_10cm', roadName + '_debug', pose)

    def setRoadWidth(self, width, roadName):
        ''' Set the width of the road specified by the road name'''
        allRoads = self.sdf.find('world').findall('road')

        roadWanted = [road for road in allRoads
                      if road.get('name') == roadName]

        roadWidth = Et.SubElement(roadWanted[0], 'width')
        roadWidth.text = str(width)

    def addRoadPoint(self, point, roadName):
        '''Add points required to build a road, specified by the roadname'''
        allRoads = self.sdf.find('world').findall('road')

        roadWanted = [road for road in allRoads
                      if road.get('name') == roadName]
        roadPoint = Et.SubElement(roadWanted[0], 'point')
        roadPoint.text = (str(point[0]) +
                          " " + str(point[1]) +
                          " " + str(point[2]))

    def addBuilding(self, mean, pointList, building_name, color):
        height = 20.0

        building = Et.SubElement(self.sdf.find('world'), 'model')
        building.set('name', building_name)
        static = Et.SubElement(building, 'static')
        static.text = 'true'
        mainPose = Et.SubElement(building, 'pose')
        mainPose.text = (str(mean[0, 0]) +
                         " " + str(mean[1, 0]) +
                         " " + str(mean[2, 0]) +
                         " 0 0 0")

        yaw = [numpy.arctan2((pointList[1, point] - pointList[1, point + 1]),
                             (pointList[0, point] - pointList[0, point + 1]))
               for point in range(numpy.size(pointList, 1) - 1)]

        distance = [numpy.sqrt(((pointList[1, point] -
                                 pointList[1, point + 1]) ** 2 +
                                (pointList[0, point] -
                                 pointList[0, point + 1]) ** 2))
                    for point in range(numpy.size(pointList, 1) - 1)]

        meanPoint = [[(pointList[0, point] +
                       pointList[0, point + 1]) / 2 - mean[0, 0],
                      (pointList[1, point] +
                       pointList[1, point + 1]) / 2 - mean[1, 0], 0]
                     for point in range(numpy.size(pointList, 1) - 1)]

        for point in range(len(yaw)):
            link = Et.SubElement(building, 'link')
            link.set('name', (building_name + '_' + str(point)))
            collision = Et.SubElement(link, 'collision')
            collision.set('name', (building_name + '_' + str(point)))

            geometry = Et.SubElement(collision, 'geometry')
            box = Et.SubElement(geometry, 'box')
            Et.SubElement(box, 'size').text = str(distance[point]) + ' 0.2 ' + str(height)

            visual = Et.SubElement(link, 'visual')
            visual.set('name', (building_name + '_' + str(point)))

            geometry = Et.SubElement(visual, 'geometry')
            box = Et.SubElement(geometry, 'box')
            Et.SubElement(box, 'size').text = str(distance[point]) + ' 0.2 ' + str(height)

            material = Et.SubElement(visual, 'material')
            script = Et.SubElement(material, 'script')
            Et.SubElement(script, 'uri').text = ('file://media/materials/' +
                                                 'scripts/gazebo.material')
            Et.SubElement(script, 'name').text = 'Gazebo/' + color
            Et.SubElement(link, 'pose').text = (str(meanPoint[point][0]) +
                                                ' ' +
                                                str(meanPoint[point][1]) +
                                                ' ' +
                                                str(height / 2.0 - 1.0) +
                                                ' 0 0 ' +
                                                str(yaw[point]))

    def writeToFile(self, filename):
        '''Write sdf file'''
        outfile = open(filename, "w")
        outfile.write(Et.tostring(self.sdf, pretty_print=True,
                                  xml_declaration=True))
        outfile.close()
