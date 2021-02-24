from datetime import date
import os
import requests 
import json 
import pandas as pd

def get_data_from_api(url):
    request = requests.get(url)
    if request.status_code == 200:
        # transform to pandas DataFrame
        df = pd.json_normalize(request.json()["features"])
        return df
    else:
        print("The data could not be updated.")



# extract data from API
# data: https://npgeo-corona-npgeo-de.hub.arcgis.com/datasets/c2f3c3b935a242169c6bec82e1fa573e_0
# labels: https://www.arcgis.com/home/item.html?id=c093fe0ef8fd4707beeb3dc0c02c3381
data_url = "https://opendata.arcgis.com/datasets/c2f3c3b935a242169c6bec82e1fa573e_0.geojson"
labels_url = "https://opendata.arcgis.com/datasets/58dba7034918475cb8aaf8ad38f7e77a_0.geojson"

# get data from api
data = get_data_from_api(data_url)
labels = get_data_from_api(labels_url)

# merge labels to data
data_labeled = pd.merge(data, labels, left_on="properties.AdmUnitId", right_on="properties.AdmUnitId")

# keep relevant columns only
df = data_labeled[["geometry_x", "properties.AdmUnitId", "properties.AnzFall", "properties.AnzTodesfall",
                   "properties.AnzFallNeu", "properties.AnzTodesfallNeu", "properties.AnzFall7T",
                   "properties.Inz7T", "properties.Name"]].copy()

# rename columns
df.rename(columns={"geometry_x":"geometry", "properties.AdmUnitId": "AdmUnitId", "properties.AnzFall":"infektionenGesamt",
           "properties.AnzTodesfall": "todeGesamt", "properties.AnzFallNeu": "infektionenNeu",
           "properties.AnzTodesfallNeu": "todeNeu", "properties.AnzFall7T": "infektionen7Tage",
           "properties.Inz7T":"inzidenz7Tage", "properties.Name":"verwaltungseinheit"}, inplace=True)

# save data as .csv file
df.to_csv("covid_data.csv")

# append to history csv file
df["date"] = date.today().strftime("%m-%d-%Y")
if os.path.isfile("./history.csv"):
    df.to_csv("history.csv", mode="a", header=False) # append to existing file
else:
    df.to_csv("history.csv") # create new file
