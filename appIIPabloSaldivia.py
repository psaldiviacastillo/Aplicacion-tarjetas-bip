import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests

# Configuración inicial
st.set_page_config(page_title="Análisis Puntos de Recarga Tarjeta BIP", page_icon="🚌  💳 ", layout="wide")
plt.style.use('default')
sns.set_palette("husl")

# Función para cargar datos
@st.cache_data
def cargar_datos():
    url = 'https://datos.gob.cl/api/3/action/datastore_search?resource_id=cbd329c6-9fe6-4dc1-91e3-a99689fd0254'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        resultado = data.get("result", {})
        records = resultado.get("records", [])
        df = pd.DataFrame(records)
        
        # Limpieza de datos
        df = df.loc[:, ~(df.isna() | (df == '')).all()]
        
        # Convertir a título
        columnas = ['NOMBRE DE FANTASIA', 'DIRECCION', 'COMUNA']
        for col in columnas:
            if col in df.columns:
                df[col] = df[col].str.title()
        
        # Mapeo de sectores
        mapeo_sectores = {
            "Conchali": "Norte", "Huechuraba": "Norte", "Independencia": "Norte",
            "Recoleta": "Norte", "Quilicura": "Norte", "Pedro Aguirre Cerda": "Sur",
            "San Miguel": "Sur", "San Joaquin": "Sur", "Lo Espejo": "Sur",
            "La Cisterna": "Sur", "La Granja": "Sur", "San Ramon": "Sur",
            "El Bosque": "Sur", "San Bernardo": "Sur", "La Pintana": "Sur",
            "La Florida": "Sur", "Puente Alto": "Sur", "Providencia": "Oriente",
            "Ñuñoa": "Oriente", "La Reina": "Oriente", "Las Condes": "Oriente",
            "Vitacura": "Oriente", "Lo Barnechea": "Oriente", "Peñalolen": "Oriente",
            "Cerro Navia": "Poniente", "Lo Prado": "Poniente", "Pudahuel": "Poniente",
            "Quinta Normal": "Poniente", "Renca": "Poniente", "Maipu": "Poniente",
            "Cerrillos": "Poniente", "Estacion Central": "Poniente", "Padre Hurtado": "Poniente",
            "Santiago": "Centro", "Macul": "Centro"
        }
        
        df['SECTOR'] = df['COMUNA'].map(mapeo_sectores)
        
        # Población por comuna
        poblacion_comunas = {
            "Conchali": 125000, "Huechuraba": 105000, "Independencia": 85000,
            "Recoleta": 155000, "Quilicura": 220000, "Pedro Aguirre Cerda": 115000,
            "San Miguel": 95000, "San Joaquin": 105000, "Lo Espejo": 125000,
            "La Cisterna": 90000, "La Granja": 135000, "San Ramon": 105000,
            "El Bosque": 185000, "San Bernardo": 285000, "La Pintana": 195000,
            "La Florida": 407927, "Puente Alto": 667904, "Providencia": 120000,
            "Ñuñoa": 185000, "La Reina": 95000, "Las Condes": 285000,
            "Vitacura": 85000, "Lo Barnechea": 105000, "Peñalolen": 272913,
            "Cerro Navia": 145000, "Lo Prado": 105000, "Pudahuel": 225000,
            "Quinta Normal": 115000, "Renca": 145000, "Maipu": 520000,
            "Cerrillos": 85000, "Estacion Central": 135000, "Padre Hurtado": 65000,
            "Santiago": 404495, "Macul": 116534
        }
        
        df['POBLACION'] = df['COMUNA'].map(poblacion_comunas)
        
        return df
    else:
        st.error("Error al cargar los datos desde la API")
        return pd.DataFrame()

# Cargar datos
df = cargar_datos()

# Título de la aplicación
st.title("🚌  💳  Análisis de Puntos de Recarga en Santiago")

# Sidebar con filtros
st.sidebar.header("Filtros")

# Filtro por sector
sectores = df['SECTOR'].unique()
sector_seleccionado = st.sidebar.multiselect(
    "Selecciona sectores:",
    options=sectores,
    default=sectores
)

# Filtro por comuna
comunas = df['COMUNA'].unique()
comuna_seleccionada = st.sidebar.multiselect(
    "Selecciona comunas:",
    options=comunas,
    default=comunas
)

# Aplicar filtros
df_filtrado = df[df['SECTOR'].isin(sector_seleccionado) & df['COMUNA'].isin(comuna_seleccionada)]

# Mostrar estadísticas básicas
st.header("Resumen de Datos")
col1, col2, col3 = st.columns(3)
col1.metric("Total de Puntos", len(df_filtrado))
col2.metric("Comunas Cubiertas", df_filtrado['COMUNA'].nunique())
col3.metric("Sectores", df_filtrado['SECTOR'].nunique())

# Pestañas para diferentes visualizaciones
tab1, tab2, tab3, tab4 = st.tabs(["Distribución", "Mapa", "Densidad", "Datos Crudos"])

with tab1:
    st.header("Distribución de Puntos de Recarga")
    
    # Gráfico por sector
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    sectores_count = df_filtrado['SECTOR'].value_counts()
    ax1.bar(sectores_count.index, sectores_count.values)
    ax1.set_title('Puntos de Recarga por Sector')
    ax1.set_ylabel('Cantidad')
    ax1.tick_params(axis='x', rotation=45)
    
    # Gráfico por comuna (top 10)
    comunas_count = df_filtrado['COMUNA'].value_counts().head(10)
    ax2.barh(comunas_count.index, comunas_count.values)
    ax2.set_title('Top 10 Comunas con más Puntos')
    ax2.set_xlabel('Cantidad')
    
    plt.tight_layout()
    st.pyplot(fig)

with tab2:
    st.header("Mapa de Puntos de Recarga")
    
    # Verificar si tenemos coordenadas
    if 'LATITUD' in df_filtrado.columns and 'LONGITUD' in df_filtrado.columns:
        # Filtrar coordenadas válidas
        df_mapa = df_filtrado.dropna(subset=['LATITUD', 'LONGITUD'])
        df_mapa = df_mapa[(df_mapa['LATITUD'] != 0) & (df_mapa['LONGITUD'] != 0)]
        
        if not df_mapa.empty:
            # RENOMBRAR LAS COLUMNAS para que Streamlit las reconozca
            df_mapa_renombrado = df_mapa.rename(columns={
                'LATITUD': 'lat', 
                'LONGITUD': 'lon'
            })
            st.map(df_mapa_renombrado[['lat', 'lon']])
        else:
            st.warning("No hay coordenadas válidas para mostrar en el mapa.")
    else:
        st.warning("Los datos no contienen coordenadas para mostrar en el mapa.")

with tab3:
    st.header("Densidad de Puntos por Población")
    
    # Calcular densidad
    densidad = df_filtrado.groupby('COMUNA').agg(
        Puntos=('COMUNA', 'count'),
        Poblacion=('POBLACION', 'first')
    ).reset_index()
    
    densidad['Puntos_por_1000hab'] = (densidad['Puntos'] / densidad['Poblacion'] * 1000).round(4)
    densidad = densidad.sort_values('Puntos_por_1000hab', ascending=False).head(10)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(densidad['COMUNA'], densidad['Puntos_por_1000hab'])
    ax.set_title('Densidad de Puntos por cada 1000 habitantes (Top 10)')
    ax.set_xlabel('Puntos por 1000 habitantes')
    plt.tight_layout()
    st.pyplot(fig)

with tab4:
    st.header("Datos Crudos")
    st.dataframe(df_filtrado)
    
    # Opción para descargar datos
    csv = df_filtrado.to_csv(index=False)
    st.download_button(
        label="Descargar datos como CSV",
        data=csv,
        file_name="puntos_recarga.csv",
        mime="text/csv"
    )

# Información adicional
st.sidebar.header("Acerca de")
st.sidebar.info("""
Esta aplicación muestra datos de puntos de recarga en Santiago, 
obtenidos desde datos.gob.cl. Los datos se actualizan automáticamente
al cargar la aplicación.
""")