from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from graph import *
from PathFind import *

class Start:
    def __init__(self):
        self.graph = Graph()


    def findPath(self, point1, point2, sunWeight):
        print("Finding Path:")
        path = getPath(point1, point2, self.graph, sunWeight)
        print(path)
        # convert ids in path to (lat, lon) tuples
        result = []
        for id in path:
            lat = self.graph.getLat(id)
            lon = self.graph.getLon(id)
            result.append((lat, lon))
        # display
        print("Display:")
        self.display(result)


    def display(self, pointsOnPath):

        m=Basemap(resolution='h', lat_0=37.871085, lon_0=-122.250752, llcrnrlon= -122.2591049877, llcrnrlat=37.8690194851, urcrnrlon= -122.2485293995, urcrnrlat=37.8773824906, epsg=2227)

        m.arcgisimage(service='ESRI_Imagery_World_2D', xpixels=2000, verbose=True)

        for point in pointsOnPath:
            coord = utm.to_latlon(point[0], point[1], 10, 'S')
            lat = coord[0]
            lon = coord[1]
            print(lat, lon)
            x, y = m(lon, lat)
            m.plot(x, y, 'bo', markersize = 5)

            plt.show()