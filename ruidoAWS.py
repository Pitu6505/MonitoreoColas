import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')

# Configuración visual
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("paper", font_scale=1.2)

# ========================================================
# 1. CÁLCULO DE LA MÉTRICA DE IBM (w_V)
# ========================================================
# Formula: w_V = 0.3 * E_readout + 0.35 * (1/T1) + 0.35 * (1/T2)
df_ibm = pd.read_csv('registro_ruido_ibm.csv', sep=';')
df_ibm['Timestamp'] = pd.to_datetime(df_ibm['Timestamp'])

# Convertimos el error de porcentaje a fracción (0 a 1) para la fórmula
err_readout_ibm = df_ibm['Error_Lectura_Medio_%'] / 100.0

# Aplicamos la fórmula matemática (asumiendo T1 y T2 en microsegundos como pasaste)
df_ibm['Metric_Score'] = (0.3 * err_readout_ibm) + \
                         (0.35 * (1.0 / df_ibm['T1_Medio_us'])) + \
                         (0.35 * (1.0 / df_ibm['T2_Medio_us']))

df_ibm['Proveedor'] = 'IBM (Physics-based)'
df_ibm.rename(columns={'Backend': 'QPU'}, inplace=True)

# ========================================================
# 2. CÁLCULO DE LA MÉTRICA DE AWS (w_AWS)
# ========================================================
# Formula: w_AWS = 0.4 * E_readout + 0.15 * E_1Q + 0.45 * E_2Q
df_aws = pd.read_csv('registro_ruido_aws.csv', sep=';')
df_aws['Timestamp'] = pd.to_datetime(df_aws['Timestamp'])

# Forte 1 does not publish 1Q gate data, so we treat its 1Q fidelity as 99.99%.
df_aws.loc[df_aws['QPU'] == 'Forte 1', 'Fid_Media_1Q_%'] = 99.99
df_aws['Fid_Media_1Q_%'] = df_aws['Fid_Media_1Q_%'].fillna(99.99)

# Convertimos fidelidades a Tasas de Error en fracción (0 a 1)
err_readout_aws = (100.0 - df_aws['Fid_Lectura_%']) / 100.0
err_1q_aws = (100.0 - df_aws['Fid_Media_1Q_%']) / 100.0
err_2q_aws = (100.0 - df_aws['Fid_Media_2Q_%']) / 100.0

# Aplicamos la nueva fórmula matemática
df_aws['Metric_Score'] = (0.40 * err_readout_aws) + \
                         (0.15 * err_1q_aws) + \
                         (0.45 * err_2q_aws)

df_aws['Proveedor'] = 'AWS (Gate-based)'

# ========================================================
# 3. UNIFICACIÓN Y VISUALIZACIÓN
# ========================================================
# Unimos los dos DataFrames solo con las columnas que nos importan
df_combined = pd.concat([
    df_ibm[['Timestamp', 'QPU', 'Metric_Score', 'Proveedor']],
    df_aws[['Timestamp', 'QPU', 'Metric_Score', 'Proveedor']]
], ignore_index=True)

# Generar la Gráfica
plt.figure(figsize=(11, 6))

# Usamos distintos marcadores para diferenciar ecosistemas
sns.lineplot(data=df_combined, x='Timestamp', y='Metric_Score', 
             hue='QPU', style='Proveedor', 
             markers=['o', 's', '^', 'D', 'v', 'p'], dashes=False, markersize=8)

plt.title('Evolución de la Penalización de Ruido (Hardware Cost Metric)', fontweight='bold')
plt.ylabel('Puntuación de Ruido ($w_V$ / $w_{AWS}$)') # A menor puntuación, mejor máquina
plt.xlabel('Fecha de Calibración')
plt.xticks(rotation=45)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
plt.tight_layout()

# Guardar figura
plt.savefig('grafica_metrica_ruido_combinada.png', dpi=300)
print("¡Gráfica 'grafica_metrica_ruido_combinada.png' generada con éxito!")

# Gráfica separada solo para AWS
plt.figure(figsize=(11, 6))

sns.lineplot(data=df_aws, x='Timestamp', y='Metric_Score', 
             hue='QPU', marker='o', markersize=8, palette='tab10')

plt.title('AWS Noise Penalty Evolution (Hardware Cost Metric)', fontweight='bold')
plt.ylabel('Noise Score ($w_{AWS}$)')
plt.xlabel('Calibration Date')
plt.xticks(rotation=45)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
plt.tight_layout()

plt.savefig('grafica_metrica_ruido_aws.png', dpi=300)
print("¡Gráfica 'grafica_metrica_ruido_aws.png' generada con éxito!")

# Imprimir un resumen numérico para el texto del artículo
print("\n--- Media de Penalización por Máquina (Menor es mejor) ---")
print(df_combined.groupby('QPU')['Metric_Score'].mean().sort_values())