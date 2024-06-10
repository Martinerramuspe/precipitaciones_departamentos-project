import streamlit as st
import pandas as pd
import plotly.express as px

# Ruta del archivo CSV
csv = r'C:\Users\erram\milimetros-agua-project\df_limpio.csv'

# Cargar el DataFrame desde el archivo CSV
df = pd.read_csv(csv)

# Convertir la columna de fechas a tipo datetime
df['fecha'] = pd.to_datetime(df['fecha'])


# Mapear el número de mes a su nombre correspondiente
nombre_meses = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 
                7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
# Extraer el mes de la columna "fecha"
df['Mes'] = df['fecha'].dt.month.map(nombre_meses)


# Obtener la lista de localidades únicas
localidades = df['Localidad'].unique()

# Sidebar inputs ( para ubicar los imputs en el lateral)
st.sidebar.header('Filtros')
ciudad = st.sidebar.selectbox('Selecciona una ciudad', localidades)
fecha_inicial = st.sidebar.date_input('Fecha inicial', value=pd.to_datetime('2010-11-15'))
fecha_final = st.sidebar.date_input('Fecha final', value=pd.to_datetime('2023-11-15'))

# Filtrar por la localidad seleccionada
df_ciudad = df[df['Localidad'] == ciudad]

# Filtrar por las fechas seleccionadas
df_ciudad = df_ciudad[(df_ciudad['fecha'] >= pd.to_datetime(fecha_inicial)) & 
                      (df_ciudad['fecha'] <= pd.to_datetime(fecha_final))]

# Obtener métricas KPI
cantidad = df_ciudad["Precipitación"].mean()
varianza = df_ciudad["Precipitación"].var()
conteo_precipitacion_cero = (df_ciudad["Precipitación"] == 0).sum()

# Mostrar las métricas como KPIs con números más grandes y en recuadros más pequeños
st.markdown(f"""
    <div style="display: flex; justify-content: space-around;">
        <div style="padding: 5px; border: 2px solid #4CAF50; border-radius: 5px; width: 25%;">
            <h3 style="text-align: center; margin: 5px;">Promedio de lluvia diaria</h3>
            <h4 style="text-align: center; margin: 5px;"><b>{cantidad:.2f}</b></h4>
        </div>
        <div style="padding: 5px; border: 2px solid #2196F3; border-radius: 5px; width: 25%;">
            <h3 style="text-align: center; margin: 5px;">Varianza</h3>
            <h4 style="text-align: center; margin: 5px;"><b>{varianza:.2f}</b></h4>
        </div>
        <div style="padding: 5px; border: 2px solid #ffcc00; border-radius: 5px; width: 25%;">
            <h3 style="text-align: center; margin: 5px;">Cantidad dias sin lluvias</h3>
            <h4 style="text-align: center; margin: 5px;"><b>{conteo_precipitacion_cero}</b></h4>
        </div>
    </div>
""", unsafe_allow_html=True)



# Agrupar por Localidad, Latitud y Longitud, y contar las precipitaciones
df_group = df_ciudad.groupby(['Localidad', 'Latitud_dd', 'Longitud_dd']).agg({'Precipitación': 'count'}).reset_index()

# Crear el mapa con color para la intensidad de precipitación
fig = px.scatter_mapbox(df_group, lat="Latitud_dd", lon="Longitud_dd",
                        hover_name="Localidad", hover_data=["Precipitación"],
                        size="Precipitación", size_max=20, zoom=9, height=400)

# Actualizar el estilo del mapa
fig.update_layout(mapbox_style="carto-positron")

# Mostrar el mapa
st.plotly_chart(fig)

# boxplots
fig_box = px.box(df_ciudad,x="Precipitación", y='Estación', orientation='h')
# Mostrar la gráfica box
st.plotly_chart(fig_box)

# Serie temporal
fig_temporal = px.area(df_ciudad, y='Precipitación')
# Mostrar la gráfica de serie
st.plotly_chart(fig_temporal) 

# Agrupar por mes y calcular el promedio de las precipitaciones
df_promedio_mes = df_ciudad.groupby('Mes')['Precipitación'].mean().reset_index()
# Ordenar los meses cronológicamente
meses_orden = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
               'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
df_promedio_mes['Mes'] = pd.Categorical(df_promedio_mes['Mes'], categories=meses_orden, ordered=True)
df_promedio_mes = df_promedio_mes.sort_values('Mes')
# Crear el gráfico de barras
fig_barras = px.bar(df_promedio_mes, x='Mes',color='Precipitación', y='Precipitación',color_continuous_scale='Blues',
                    labels={'Mes': 'Mes', 'Precipitación': 'Promedio [mm]'})

# Mostrar el gráfico de barras
st.plotly_chart(fig_barras)