# OSM Plug-in for Gazebo/Stage #
	
	Author:         Tashwin Khurana
	Maintainer:     Krystian Gebis
	Version:        1.9
	Description:    Open Street Maps plugin for Gazebo and Stage Simulators
	                This folder contains files for building osm_plugin for both simulators.
	

## Dependencies: ##

	Python 2.7
	OpenCV
	Mapnik:
		https://github.com/mapnik/mapnik/wiki/UbuntuInstallation
	Osmapi:
		sudo pip install osmapi


## Files: ##

***osm2dict.py***

Collects data about certain types of roads based on input coordinates from osm database and converts the information received to format that can be used to build sdf files.

***dict2sdf.py***

Used to build sdf file from data received about the elements in the sdf format. 
 - functionality: 
  - add models to world, 
  - add road element, 
  - set road width, 
  - add points to the road element

***getMapImage.py***

Gets the image of the area required to be simulated.
       
***getOsmFile.py***

Downloads the osm database of the specified area.