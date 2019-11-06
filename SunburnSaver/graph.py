########################################################
# This generates and stores our graph of the world     #
########################################################
import pandas as pd
import xml.etree.ElementTree as ET
import googlemaps
import math
import numpy
from SunScore import *

gmaps_api = googlemaps.Client(key=[redacted])


# import osmium as mium
# import pickle
# import osmapi as osm
# import googlemaps
# import json

#
# osm_api = osm.OsmApi()
# gmaps_api = googlemaps.Client(key=[redacted])


class Graph:
    def __init__(self):
        xml_data = "map.osm"
        etree = ET.parse(xml_data)  # create an ElementTree object
        root = etree.getroot()

        # nodes
        try:
            self.node_df = pd.read_pickle("node_df.pkl")
        except:
            print("ERROR: node_df not found")
            df_cols = ["id", "uid", "lat", "lon"]
            rows = []
            for node in root:
                if node is None or node.tag!="node":
                    continue
                # print (node.attrib)
                try:
                    s_id = node.attrib["id"]
                    s_uid = node.attrib["uid"]
                    s_lat = node.attrib["lat"][:7]
                    s_lon = node.attrib["lon"][:9]
                except:
                    continue


                rows.append({"id": s_id, "uid": s_uid,
                             "lat": s_lat, "lon": s_lon})
            self.node_df = pd.DataFrame(rows, columns=df_cols)
            self.node_df.drop_duplicates(inplace=True, subset=["id"])

            # drop rows where (lat, lon) is duplicated (keeps first)
            # self.node_df.drop_duplicates(inplace=True, subset=["lat", "lon"])

            # populate a nodes column
            node_col = []
            for index, row in self.node_df.iterrows():
                new_node = Node(row["lat"], row["lon"], row["id"])
                node_col.append(new_node)
            self.node_df["nodes"] = pd.Series(node_col)
            # save to pickle
            self.node_df.to_pickle("node_df.pkl")

        # paths
        try:
            self.way_df = pd.read_pickle("way_df.pkl")
        except:
            print("Error: way_df not found")
            ways_cols = ["way_id", "id"]
            ways_rows = []
            for node in root:
                if node is None or node.tag!="way":
                    continue
                try:

                    s_way_id = node.attrib["id"]

                    cur_row = []
                    for i in range(len(node)):
                        try:
                            cur_row.append(node[i].attrib["ref"])
                        except:
                            continue
                    ways_rows.append({"way_id": s_way_id, "id": cur_row})


                except:
                    continue
            self.way_df = pd.DataFrame(ways_rows, columns=ways_cols)
            # to pickle
            self.way_df.to_pickle("way_df.pkl")


        # edges
        try:
            self.edges = pd.read_pickle("edges.pkl")
        except:
            print("ERROR: Edges table not found")
            new_rows = []
            found = []
            c = 0
            for index, row in self.way_df.iterrows():
                print ("current row:", c)
                c+=1
                ids = list(row["id"])
                # note this excludes first and last item

                for i in range(1, len(ids)):
                    if (ids[i], ids[i-1]) in found:
                        continue
                    found.append((ids[i], ids[i-1]))
                    found.append((ids[i-1], ids[i]))
                    if ((self.node_df.loc[self.node_df["id"]==ids[i]].empty) or (self.node_df.loc[self.node_df["id"] == ids[i-1]].empty)):
                        continue
                    lat1 = float(self.node_df.loc[self.node_df["id"]==ids[i]].iloc[0]["lat"])

                    lon1 = float(self.node_df.loc[self.node_df["id"]==ids[i]].iloc[0]["lon"])
                    origins = (lat1, lon1)
                    lat2 = float(self.node_df.loc[self.node_df["id"] == ids[i-1]].iloc[0]["lat"])
                    lon2 = float(self.node_df.loc[self.node_df["id"] == ids[i-1]].iloc[0]["lon"])
                    destinations = (lat2, lon2)

                    # dist_matrix = gmaps_api.distance_matrix(origins, destinations, mode="walking")
                    # dist = dist_matrix["rows"][0]["elements"][0]["distance"]["value"]
                    dist = ((lat1-lat2)**2 + (lon1-lon2)**2)**0.5


                    new_rows.append({"id1": ids[i], "id2":ids[i-1], "distance":dist})
                    new_rows.append({"id1":ids[i-1], "id2":ids[i], "distance":dist})

            self.edges = pd.DataFrame(new_rows, columns=["id1", "id2", "distance"])
            print(self.edges.head())
            # to pickle
            self.edges.to_pickle("edges.pkl")


    def getIds(self):
        """returns a list of ids of nodes"""
        return self.node_df["id"]

    def getLat(self, id):
        """returns the latitude of node w/ id"""

        return float (self.node_df.loc[self.node_df["id"] == id]["lat"])


    def getLon(self, id):
        """returns the longitude of node w/ id"""
        return float(self.node_df.loc[self.node_df["id"]==id]["lon"])


    def getNeighbors(self, id):
        """returns a list of neighbor ids of node w/ id"""
        return self.edges.loc[self.edges["id1"]==id, "id2"]

    def getDistance(self, id1, id2):
        """returns distance between node w/ id1 and node w/ id2"""
        return self.edges.loc[(self.edges["id1"]==id1) & (self.edges["id2"]==id2), "distance"].iloc[0]

    def getEuclideanDistance(self, id, lat, lon):
        """returns the euclidean distance between node w/ id and specified lat and lon"""
        id_lat = self.getLat(id)
        id_lon = self.getLon(id)
        return ((id_lat - float(lat))**2 + (id_lon - float(lon))**2)**0.5

    def findClosestID(self, lat, lon):
        """returns the id of node with closest lat and lon """
        distances = self.node_df[["id"]].copy()
        distances["distances"] = distances["id"].apply(lambda x: self.getEuclideanDistance(x, lat, lon))
        distances = distances.sort_values(by="distances")
        return distances.iloc[0]["id"]

    def getSunScore(self, id1, id2):
        """returns the sun score between id1 and id2"""
        # We knpw that id1 and id2 are neighbors
        lat1 = self.getLat(id1)
        lon1 = self.getLon(id1)

        lat2 = self.getLat(id2)
        lon2 = self.getLon(id2)
        sun = SunScore()
        return sun.shadeweight(lat1, lon1, lat2, lon2)

    def convertIDsToLatLon(self, ids):
        """given a list of ids, returns a list of (lat, lon)"""
        result = []
        for id in ids:
            result.append((self.getLat(id), self.getLon(id)))
        return result





class Node:
    def __init__(self, lat, lon, _id):
        self.id = _id
        self.lat = lat
        self.lon = lon
        self.neighbors = []

    def addNeighbor(self, new_node_id):
        self.neighbors += [new_node_id]

    def getLat(self):
        return self.lat

    def getLon(self):
        return self.lon

    def getID(self):
        return self.id


