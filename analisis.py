import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from datetime import datetime

fecha_actualizacion = datetime.today().strftime('%d/%m/%Y')
jornada = 23  # cambia este número cada vez que actualices

print(f"Análisis Liga MX - Jornada {jornada} | Actualizado: {fecha_actualizacion}")
print("-" * 50)

# Cargar datos reales de FBref
df = pd.read_csv('data_ligamx.csv', skiprows=1)

# Limpiar columnas
df = df[['Player', 'Squad', 'Age', 'Pos', 'MP', 'Gls', 'Ast']].copy()
df.columns = ['Jugador', 'Equipo', 'Edad', 'Posicion', 'Partidos', 'Goles', 'Asistencias']

# Eliminar filas vacías o encabezados repetidos
df = df[df['Jugador'] != 'Player'].dropna(subset=['Jugador'])

# Convertir a números
df['Goles'] = pd.to_numeric(df['Goles'], errors='coerce').fillna(0)
df['Asistencias'] = pd.to_numeric(df['Asistencias'], errors='coerce').fillna(0)
df['Partidos'] = pd.to_numeric(df['Partidos'], errors='coerce').fillna(1)

# Consolidar jugadores que se transfirieron durante la temporada
df = df.groupby('Jugador').agg({
    'Equipo': 'last',  # quedarse con el último equipo
    'Edad': 'first',
    'Posicion': 'first',
    'Partidos': 'sum',
    'Goles': 'sum',
    'Asistencias': 'sum'
}).reset_index()

# Calcular métricas
df['Goles_por_partido'] = (df['Goles'] / df['Partidos']).round(2)
df['Contribuciones'] = df['Goles'] + df['Asistencias']

# Mostrar top 10 por contribuciones
top10 = df[df['Partidos'] >= 10].nlargest(10, 'Contribuciones')
print(top10[['Jugador', 'Equipo', 'Goles', 'Asistencias', 'Contribuciones', 'Goles_por_partido']])

plt.figure(figsize=(12, 7))
sns.barplot(data=top10, x='Contribuciones', y='Jugador', 
            hue='Equipo', palette='viridis', dodge=False)

plt.xlabel('Contribuciones (Goles + Asistencias)')
plt.ylabel('Jugador')
plt.title('Top 10 Jugadores por Contribuciones - Liga MX Clausura 2026')
plt.tight_layout()
plt.show()

# Índice de valor: qué tanto rinde un jugador por contribución
# Entre más alto, más eficiente (más contribuciones en menos partidos)
df['Indice_valor'] = ((df['Contribuciones'] / df['Partidos']) * 100).round(1)

top10_valor = df[df['Partidos'] >= 10].nlargest(10, 'Indice_valor')

plt.figure(figsize=(12, 7))
sns.barplot(data=top10_valor, x='Indice_valor', y='Jugador',
            hue='Equipo', palette='coolwarm', dodge=False)

plt.xlabel('Índice de Valor (Contribuciones por 100 partidos)')
plt.ylabel('Jugador')
plt.title('Top 10 Jugadores por Índice de Valor - Liga MX Clausura 2026')
plt.tight_layout()
plt.show()

print(top10_valor[['Jugador', 'Equipo', 'Partidos', 'Contribuciones', 'Indice_valor']])

print(df[df.duplicated(subset=['Jugador'], keep=False)][['Jugador', 'Equipo', 'Partidos', 'Goles']].sort_values('Jugador'))

print(df.groupby('Jugador').filter(lambda x: len(x) > 1)[['Jugador', 'Equipo', 'Partidos', 'Goles']].sort_values('Jugador').to_string())

# Análisis por posición
print("\nTop 3 por posición:")
posiciones = df.groupby('Posicion').apply(
    lambda x: x.nlargest(3, 'Indice_valor')[['Jugador', 'Equipo', 'Contribuciones', 'Indice_valor']]
).reset_index(drop=True)
print(posiciones.to_string())

# Análisis por posición con mínimo de partidos
print("\nTop 3 por posición (mínimo 8 partidos):")
posiciones = df[df['Partidos'] >= 8].groupby('Posicion').apply(
    lambda x: x.nlargest(3, 'Indice_valor')[['Jugador', 'Equipo', 'Contribuciones', 'Indice_valor']]
).reset_index(drop=True)
print(posiciones.to_string())

# Visualización top 3 por posición
fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.suptitle('Top 3 Jugadores por Posición - Liga MX Clausura 2026', fontsize=14, fontweight='bold')

posiciones_lista = df[df['Partidos'] >= 8]['Posicion'].unique()
traduccion_posiciones = {
    'FW': 'Delantero',
    'MF': 'Mediocampista', 
    'DF': 'Defensa',
    'GK': 'Portero',
    'MF,FW': 'Mediocampista/Delantero',
    'FW,MF': 'Delantero/Mediocampista',
    'DF,MF': 'Defensa/Mediocampista',
    'MF,DF': 'Mediocampista/Defensa',
    'DF,FW': 'Defensa/Delantero'
}

for i, pos in enumerate(posiciones_lista[:6]):
    ax = axes[i//3][i%3]
    data_pos = df[(df['Partidos'] >= 8) & (df['Posicion'] == pos)].nlargest(3, 'Indice_valor')
    
    if len(data_pos) > 0:
        sns.barplot(data=data_pos, x='Indice_valor', y='Jugador', 
                   palette='Blues_r', ax=ax)
        ax.set_title(traduccion_posiciones.get(pos, pos))
        ax.set_xlabel('Índice de Valor')
        ax.set_ylabel('')

plt.tight_layout(pad=3.0)
plt.subplots_adjust(left=0.15)
plt.show()