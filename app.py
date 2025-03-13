import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import folium
from streamlit_folium import folium_static

# Caricamento dati
eta_municipi = pd.read_excel("/mnt/data/Età media municipi.xlsx")
municipi_percentuali = pd.read_excel("/mnt/data/Municipi con percentuali.xlsx")
sezioni_percentuali = pd.read_excel("/mnt/data/Sezioni con percentuali.xlsx")
astensione_municipi = pd.read_excel("/mnt/data/Astensione per municipio.xlsx")
astensione_sezioni = pd.read_excel("/mnt/data/Astensione per sezione.xlsx")
municipi_geo = gpd.read_file("/mnt/data/Municipi Genova.geojson")
sezioni_geo = gpd.read_file("/mnt/data/precincts_genova_original.geojson")

# Layout UI
st.set_page_config(layout="wide", page_title="Dashboard Elettorale")
st.markdown("""
    <style>
    .stApp { background-color: black; color: white; }
    .card { background-color: #1E1E1E; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# Sezione Municipi
st.markdown("### **Dati per Municipio**")
st.markdown("**Età Media e Voti per Lista**")

# Merge dati municipi
municipi_data = municipi_percentuali.merge(eta_municipi[['Municipio', 'Età Media']], on='Municipio')

# Mappa Municipi
map_municipi = folium.Map(location=[44.4056, 8.9463], zoom_start=12, tiles="cartodb dark_matter")
for _, row in municipi_data.iterrows():
    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=f"Municipio: {row['Municipio']}<br>Età Media: {row['Età Media']}<br>Voti Totali: {row['Totale votanti']}",
        icon=folium.Icon(color="blue")
    ).add_to(map_municipi)
folium_static(map_municipi)

# Grafico voti per lista
fig_voti_municipi = px.bar(municipi_data, x='Municipio', y=['PD %', 'Lega %', 'FdI %', 'M5S %'],
                           title='Distribuzione Voti per Lista', barmode='group')
st.plotly_chart(fig_voti_municipi)

# Sezione Astensionismo Municipi
st.markdown("**Astensionismo per Municipio**")
fig_astensione_municipi = px.pie(astensione_municipi, names='Municipio', values='Astenuti %',
                                 title='Percentuale Astensionismo per Municipio')
st.plotly_chart(fig_astensione_municipi)

# Sezione Sezioni Elettorali
st.markdown("### **Dati per Sezione**")
st.markdown("**Voti per Lista e Astensionismo**")

# Mappa Sezioni
map_sezioni = folium.Map(location=[44.4056, 8.9463], zoom_start=12, tiles="cartodb dark_matter")
for _, row in sezioni_percentuali.iterrows():
    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=f"Sezione: {row['SEZIONE']}<br>Voti Totali: {row['Totale votanti']}",
        icon=folium.Icon(color="red")
    ).add_to(map_sezioni)
folium_static(map_sezioni)

# Grafico voti per lista sezioni
fig_voti_sezioni = px.bar(sezioni_percentuali, x='SEZIONE', y=['PD %', 'Lega %', 'FdI %', 'M5S %'],
                          title='Distribuzione Voti per Lista nelle Sezioni', barmode='group')
st.plotly_chart(fig_voti_sezioni)

# Sezione Astensionismo Sezioni
fig_astensione_sezioni = px.pie(astensione_sezioni, names='SEZIONE', values='Astenuti %',
                                title='Percentuale Astensionismo per Sezione')
st.plotly_chart(fig_astensione_sezioni)
