import pandas as pd
import requests
import streamlit as st
import plotly.graph_objs
import plotly.express as px
import os
import locale
locale.setlocale(locale.LC_ALL, "german")

def get_timestamp(file):
    ts = os.path.getmtime(file)
    return ts

@st.cache(suppress_st_warning=True)
def load_data(file, timestamp, **kwargs):
    st.write("Load data...")
    df = pd.read_csv(file, **kwargs)
    return df

@st.cache(suppress_st_warning=True, hash_funcs={plotly.graph_objs.Figure: lambda _: None}, allow_output_mutation=True)
def create_map(df, api_url):

    # get geometry information for plotting
    response = requests.get(api_url)
    kreis_geo = []
    for kreis in response.json()["features"]:
        AdmUnitId = kreis["properties"]["AdmUnitId"]
        geometry = kreis["geometry"]
        kreis_geo.append({
            "type": "Feature",
            "geometry": geometry,
            "id": AdmUnitId
        })
    geo = {'type': 'FeatureCollection', 'features': kreis_geo}

    # keep only districts
    df = df[df.AdmUnitId > 16]

    # create map
    fig = px.choropleth(df,
                        geojson=geo,
                        scope="europe",
                        color_continuous_scale="Burgyl",
                        locations="AdmUnitId",
                        color="inzidenz7Tage",
                        template="simple_white",
                        hover_name="verwaltungseinheit",
                        hover_data=("inzidenz7Tage", "infektionenNeu", "todeNeu"),
                        labels={"AdmUnitId": "Landkreis",
                                "verwarltungseinheit": "Landkreis",
                                "inzidenz7Tage": "7-Tage Inzidenz",
                                "todeNeu": "Todesfälle",
                                "infektionenNeu": "Neuinfektionen"}
                        )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig

# load data and create map object
ts = get_timestamp("covid_data.csv")
df = load_data("covid_data.csv", timestamp=ts, index_col=0)
fig = create_map(df, "https://opendata.arcgis.com/datasets/917fc37a709542548cc3be077a786c17_0.geojson")

##### ACTUAL APP:

st.title("Covid-19 Dashboard: Inzidenz in Deutschland")

# filter data using input
choices = list(df.verwaltungseinheit.unique())
input = st.selectbox("Wählen Sie eine Aggregationsebene. Sie können entweder einzelne Stadt- und Landkreise auswählen oder die gesamte BRD oder Bundesländer auswählen.", choices, index=choices.index('Bundesrepublik Deutschland'))

inzidenz = round(float(df.loc[df["verwaltungseinheit"]==input].inzidenz7Tage), 1)
fall7tage = int(df.loc[df["verwaltungseinheit"]==input].infektionen7Tage)
neuinfektionen = int(df.loc[df["verwaltungseinheit"]==input].infektionenNeu)
gesamtinfektionen = int(df.loc[df["verwaltungseinheit"]==input].infektionenGesamt)
todeNeu = int(df.loc[df["verwaltungseinheit"]==input].todeNeu)
todeGesamt = int(df.loc[df["verwaltungseinheit"]==input].todeGesamt)

### KEY FACTS FOR SELECTED AGGREGATION

col1, col2, col3 = st.beta_columns(3)
with col1:
    st.markdown("### *7-Tage-Inzidenz:*")
    st.markdown("### <font color=‘#8b0000’><strong>{}</strong></font>".format(inzidenz), unsafe_allow_html=True)
    st.markdown("### *7-Tage-Fallzahl:*")
    st.markdown("### <font color=‘#8b0000’><strong>{:n}</strong></font>".format(fall7tage), unsafe_allow_html=True)
    st.write("\n")

with col2:
    st.markdown("### *Neuinfektionen:*")
    st.markdown("### <font color=‘#8b0000’><strong>{:n}</strong></font>".format(neuinfektionen), unsafe_allow_html=True)
    st.markdown("### *Gesamtzahl Fälle:*")
    st.markdown("### <font color=‘#8b0000’><strong>{:n}</strong></font>".format(gesamtinfektionen), unsafe_allow_html=True)
    st.write("\n")

with col3:
    st.markdown("### *Neue Todesfälle:*")
    st.markdown("### <font color=‘#8b0000’><strong>{:n}</strong></font>".format(todeNeu), unsafe_allow_html=True)
    st.markdown("### *Gesamtzahl Todesfälle:*")
    st.markdown("### <font color=‘#8b0000’><strong>{:n}</strong></font>".format(todeGesamt), unsafe_allow_html=True)
    st.write("\n")

st.markdown("<hr style=\"height:3px;border:none;background-color:darkgrey\">", unsafe_allow_html=True)

### CHOROPLETH MAP FOR GERMANY

st.subheader("Infektionsgeschehen in Deutschland:")
st.write("\n")
st.plotly_chart(fig)
st.write("\n")

st.markdown("<hr style=\"height:3px;border:none;background-color:darkgrey\">", unsafe_allow_html=True)

### TOP 5 / BOTTOM 5

st.subheader("Landkreise mit den höchsten und niedrigsten Kennzahlen:")

df2 = df.set_index("verwaltungseinheit").copy()
df2.rename(columns={"infektionenGesamt":"Gesamtzahl Infektionen", "todeGesamt": "Gesamtzahl Todesfälle",
                    "infektionenNeu": "Neuinfektionen", "todeNeu": "Neue Todesfälle",
                    "infektionen7Tage":"Gesamtzahl Infektionen vergangene 7 Tage", "inzidenz7Tage": "7-Tage-Inzidenz"},
           inplace=True)

metrics = ["7-Tage-Inzidenz", "Gesamtzahl Infektionen vergangene 7 Tage", "Neuinfektionen", "Gesamtzahl Infektionen",
           "Neue Todesfälle", "Gesamtzahl Todesfälle"]
input_number = st.selectbox("Wählen Sie eine Kennzahl.", metrics, index=0)

df2 = df2.loc[df2.AdmUnitId > 16] # exclude BRD and federal states aggregation
df2["7-Tage-Inzidenz"] = round(df2["7-Tage-Inzidenz"], 1)
df2 = df2[[input_number]].copy() # make copy of data with relevant data only
df2.index.name = None # remove index name
pd.options.display.float_format = "{:,.1f}".format
col4, col5 = st.beta_columns(2)
with col4:
    df2.sort_values(input_number, ascending=True, inplace=True)
    st.table(df2.head().style.format("{:7,.1f}"))

with col5:
    df2.sort_values(input_number, ascending=False, inplace=True)
    st.table(df2.head().style.format("{:7,.1f}"))