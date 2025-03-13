# Ecco un esempio di codice completo che non richiede le colonne 'lat'/'lon' nei tuoi DataFrame
# ma calcola le coordinate dalle geometrie del file GeoJSON. Assicurati di adattare i nomi delle colonne
# del tuo GeoDataFrame (es. 'NOME' o 'NAME') a quelli presenti nei tuoi file.

import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import folium
from streamlit_folium import folium_static

# Caricamento dati da cartella 'data'
eta_municipi = pd.read_excel("data/Età media municipi.xlsx")
municipi_percentuali = pd.read_excel("data/Municipi con percentuali.xlsx")
sezioni_percentuali = pd.read_excel("data/Sezioni con percentuali.xlsx")
astensione_municipi = pd.read_excel("data/Astensione per municipio.xlsx")
astensione_sezioni = pd.read_excel("data/Astensione per sezione.xlsx")

# Carica GeoDataFrame e convertilo in EPSG 4326 (lat/lon)
municipi_geo = gpd.read_file("data/Municipi Genova.geojson").to_crs(epsg=4326)
sezioni_geo = gpd.read_file("data/precincts_genova_original.geojson").to_crs(epsg=4326)

# ====== ESEMPI DI COLONNE ======
# Adatta questi nomi a quelli reali del tuo GeoDataFrame.
# Ad esempio, se il file dei Municipi contiene la colonna "NOME" con
# il nome del municipio, e in 'municipi_percentuali' la colonna si chiama 'Municipio',
# puoi uniformarle.

# Esempio:
# 1) Rinomino la colonna 'NOME' in 'Municipio' nel GeoDataFrame
#    per poter fare il merge con 'municipi_percentuali'.

# (Supponiamo che la colonna nel GeoJSON si chiami 'NOME')
municipi_geo = comuni_geo = municipi_geo.rename(columns={"NOME": "Municipio"})

# 2) Ora faccio il merge con i dati di percentuali
municipi_merged = municipi_geo.merge(municipi_percentuali, on="Municipio", how="left")

# 3) Se voglio aggiungere l'Età Media:
municipi_merged = municipi_merged.merge(eta_municipi[["Municipio", "Età Media"]], on="Municipio", how="left")

# 4) Calcolo il centroide per piazzare i marker
municipi_merged["centroid"] = municipi_merged.geometry.centroid

# Stessa logica per le sezioni.
# Supponiamo che la colonna nel GeoJSON delle sezioni sia 'SEZIONE', e che
# in sezioni_percentuali ci sia anche la colonna 'SEZIONE'.
sezioni_geo = sezioni_geo.rename(columns={"SEZIONE": "SEZIONE"})  # se serve
sezioni_merged = sezioni_geo.merge(sezioni_percentuali, on="SEZIONE", how="left")
sezioni_merged["centroid"] = sezioni_merged.geometry.centroid

# Layout UI
st.set_page_config(layout="wide", page_title="Dashboard Elettorale")
st.markdown(
    """
    <style>
    .stApp { background-color: black; color: white; }
    .card { background-color: #1E1E1E; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
    </style>
    """,
    unsafe_allow_html=True
)

# ===================== Sezione Municipi =====================
st.markdown("### **Dati per Municipio**")

# Mappa Municipi con centri calcolati
map_municipi = folium.Map(location=[44.4056, 8.9463], zoom_start=12, tiles="cartodb dark_matter")

for _, row in municipi_merged.iterrows():
    if pd.notna(row["centroid"]):
        lat = row["centroid"].y
        lon = row["centroid"].x
        popup_txt = f"""
        <b>Municipio:</b> {row['Municipio']}<br>
        <b>Età Media:</b> {row.get('Età Media', 'N/A')}<br>
        <b>Voti Totali:</b> {row.get('Totale votanti', 'N/A')}
        """
        folium.Marker(
            location=[lat, lon],
            popup=popup_txt,
            icon=folium.Icon(color="blue")
        ).add_to(map_municipi)

folium_static(map_municipi)

# Grafico voti per lista (esempio con alcune colonne)
fig_voti_municipi = px.bar(
    municipi_merged.dropna(subset=["Municipio"]),
    x="Municipio",
    y=["PD %", "Lega %", "FdI %", "M5S %"],
    title="Distribuzione Voti per Lista",
    barmode="group"
)
st.plotly_chart(fig_voti_municipi)

# Astensionismo Municipi
st.markdown("**Astensionismo per Municipio**")
fig_astensione_municipi = px.pie(
    astensione_municipi,
    names="Municipio",
    values="Astenuti %",
    title="Percentuale Astensionismo per Municipio"
)
st.plotly_chart(fig_astensione_municipi)

# ===================== Sezione Sezioni =====================
st.markdown("### **Dati per Sezione**")

map_sezioni = folium.Map(location=[44.4056, 8.9463], zoom_start=12, tiles="cartodb dark_matter")

for _, row in sezioni_merged.iterrows():
    if pd.notna(row["centroid"]):
        lat = row["centroid"].y
        lon = row["centroid"].x
        popup_txt = f"""
        <b>Sezione:</b> {row['SEZIONE']}<br>
        <b>Voti Totali:</b> {row.get('Totale votanti', 'N/A')}
        """
        folium.Marker(
            location=[lat, lon],
            popup=popup_txt,
            icon=folium.Icon(color="red")
        ).add_to(map_sezioni)
folium_static(map_sezioni)

fig_voti_sezioni = px.bar(
    sezioni_merged.dropna(subset=["SEZIONE"]),
    x="SEZIONE",
    y=["PD %", "Lega %", "FdI %", "M5S %"],
    title="Distribuzione Voti per Lista nelle Sezioni",
    barmode="group"
)
st.plotly_chart(fig_voti_sezioni)

# Astensionismo Sezioni
fig_astensione_sezioni = px.pie(
    astensione_sezioni,
    names="SEZIONE",
    values="Astenuti %",
    title="Percentuale Astensionismo per Sezione"
)
st.plotly_chart(fig_astensione_sezioni)


