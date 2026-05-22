import streamlit as st

import requests
import pandas as pd
from io import StringIO
import json
import geopandas as gpd
import matplotlib.pyplot as plt

STATISTIKAAMETI_API_URL = "https://andmed.stat.ee/api/v1/et/stat/RV032"

JSON_PAYLOAD_STR =""" {
  "query": [
    {
      "code": "Aasta",
      "selection": {
        "filter": "item",
        "values": [
          "2014",
          "2015",
          "2016",
          "2017",
          "2018",
          "2019",
          "2020",
          "2021",
          "2022",
          "2023"
        ]
      }
    },
    {
      "code": "Maakond",
      "selection": {
        "filter": "item",
        "values": [
          "39",
          "44",
          "49",
          "51",
          "57",
          "59",
          "65",
          "67",
          "70",
          "74",
          "78",
          "82",
          "84",
          "86",
          "37"
        ]
      }
    },
    {
      "code": "Sugu",
      "selection": {
        "filter": "item",
        "values": [
          "2",
          "3"
        ]
      }
    }
  ],
  "response": {
    "format": "csv"
  }
}
"""
geojson = "maakonnad.geojson"
    
@st.cache_data
def import_data():
    headers = {
        'Content-Type': 'application/json'  # or application/x-www-form-urlencoded if needed
    }
    
    parsed_payload = json.loads(JSON_PAYLOAD_STR)
    
    
    response = requests.post(STATISTIKAAMETI_API_URL, json=parsed_payload, headers=headers)
    
    if response.status_code == 200:
        print("Request successful.")       
        text = response.content.decode('utf-8-sig')
        df = pd.read_csv(StringIO(text))

    else:
        print(f"Failed with status code: {response.status_code}")
        print(response.text)
    return df

@st.cache_data
def import_geojson():
    gdf = gpd.read_file(geojson)
    return gdf

def get_data_for_year(df, year):
    year_data = df[df.Aasta==year]
    return year_data

def merging(df, gdf):
    merged = gdf.merge(df, left_on='MNIMI', right_on='Maakond', how='left')
    merged["Loomulik iive"] = merged["Mehed Loomulik iive"] + merged["Naised Loomulik iive"]
    return merged

def plot(df):
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Replace 'value_column' with the column name you want to visualize
    df.plot(column='Loomulik iive', 
                     ax=ax,
                     legend=True,
                     cmap='viridis',  # Choose a colormap
                     legend_kwds={'label': "Loomulik iive"})
    
    plt.title('Loomulik iive maakonniti aastal 2023')
    plt.axis('off')  # Hide axis
    plt.tight_layout()
    plt.show()

st.title("Kodutöö 6")
st.write("Uurime loomulikku iivet erinevatel aastatel")

st.sidebar.header("Valikud")
data = import_data()
geo_data = import_geojson()

if not data.empty and not geo_data.empty:
    merged_data = merging(data, geo_data)
    year = st.sidebar.selectbox("Vali aasta:", sorted(merged_data['Aasta'].unique()))
    year_data = get_data_for_year(merged_data, year)
    plot_map(year_data, year)
else:
    st.warning("Andmete laadimine ebaõnnestus.")
