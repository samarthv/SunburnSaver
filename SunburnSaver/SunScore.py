
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import utm
import math
from scipy.spatial.distance import cdist
from pysolar.solar import *
import pysolar
import datetime
from pytz import timezone
import pytz


import matplotlib
# from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt

import matplotlib.cm
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize


# In[2]:
class SunScore:

    def __init__(self):
        self.df = pd.read_csv("points.csv", header=None)


        # In[3]:


        self.df = self.df.drop(6, axis=1)
        self.df = self.df.drop(5, axis=1)
        self.df = self.df.drop(4, axis=1)
        self.df = self.df.drop(3, axis=1)


    # In[4]:


    def nearestPoint(self, df, easting, northing):
        # temp = df.copy()
        # temp["dists"] = np.sqrt(np.power((temp[0] - easting), 2) + np.power((temp[1] - northing), 2))
        # temp = temp.sort_values(by="dists")
        # row = temp.iloc[0]
        # return [row[0], row[1], row[2]]
        result = [0, 0, 0]
        result_distance = 999999999
        temp = df[(df[0]<easting+1) & (df[0]>easting-1) & (df[1]<northing+1) & (df[1]>northing-1)]
        for index, row in temp.iterrows():
            if (result_distance > ((easting-row[0])**2+(northing-row[1])**2)**0.5):
                result = [row[0], row[1], row[2]]
                result_distance = ((easting-result[0])**2+(northing-result[1])**2)**0.5
        return result





    def shaded(self, df, easting, northing, altitude, azimuth, sun_angle):
        parametric = np.array([np.cos(sun_angle*np.pi/180)*np.cos(azimuth*np.pi/180), np.cos(sun_angle*np.pi/180)*np.sin(azimuth*np.pi/180), np.sin(sun_angle*np.pi/180)])
        temp = df[(df[0]<easting+20) & (df[0]>easting-20) & (df[1]<northing+20) & (df[1]>northing-20)]


        # temp = temp[(temp[2] - altitude) > 3]
        # print(temp)
        # temp["cross"] = temp.apply(lambda x: np.cross(parametric, (np.array(x[0] - easting, x[1] - northing, x[2] - altitude))), axis=1)
        # temp["b"] = temp.apply(lambda x: np.sqrt(x["cross"].dot(x["cross"]))>1, axis=1)
        # return temp["b"].any()
        for index, row in temp.iterrows():
            if (row[2]-altitude > 3):
                difference = np.array([row[0] - easting, row[1] - northing, row[2] - altitude])
                cross_product = np.cross(parametric, difference)
                magnitude = np.sqrt(cross_product.dot(cross_product))
                if magnitude < 1:
                    return True
        return False




    def shadeweight(self, lat1, lon1, lat2, lon2):
        df = self.df
        point1 = utm.from_latlon(lat1, lon1)
        point2 = utm.from_latlon(lat2, lon2)

        maxEast = max(point1[0], point2[0])
        maxNorth = max(point1[1], point2[1])
        minEast = min(point1[0], point2[0])
        minNorth = min(point1[1], point2[1])

        temp = df[(df[0]<maxEast+20) & (df[0]>minEast-20) & (df[1]<maxNorth+20) & (df[1]>minNorth-20)]

        m_x = (point2[0]-point1[0])*2
        m_y = (point2[1]-point1[1])*2

        distance = np.sqrt((point1[0]-point2[0])**2+(point1[1]-point2[1])**2)
        m_x = m_x / distance
        m_y = m_y / distance
        distance = np.round(distance)

        pointsOnPath = []
        for _ in range((distance/2).astype(np.int64)):
            point = ((point1[0]+(_*m_x), point1[1]+(_*m_y)))
            pointsOnPath.append(point)

        for _ in range(len(pointsOnPath)):
            pointsOnPath[_] = self.nearestPoint(temp, pointsOnPath[_][0], pointsOnPath[_][1])

        date = datetime.datetime.now(tz=pytz.utc)
        date = date.astimezone(timezone('US/Pacific'))

        altitude = 0 #pysolar.solar.get_altitude(37.871085, -122.250752, date)
        azimuth = pysolar.solar.get_azimuth(37.871085,-122.250752, date)
        #TODO: why is altitude 0
        # print(altitude)

        for _ in range(len(pointsOnPath)):
            pointsOnPath[_].append(self.shaded(temp, pointsOnPath[_][0], pointsOnPath[_][1], pointsOnPath[_][2], azimuth, altitude))

        shadeWeight = 0
        for _ in range(len(pointsOnPath)):
            if (pointsOnPath[_][3]):
                shadeWeight += 1


        result = len(pointsOnPath) - shadeWeight
        return result