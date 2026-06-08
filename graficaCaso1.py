import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. CONFIGURACIÓN VISUAL PARA EL PAPER
# ==========================================
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("paper", font_scale=1.2)

# ==========================================
# 2. DATOS DEL CASO DE USO 1 (50 Circuitos)
# ==========================================
providers = [
    "AWS Rigetti Cepheus", 
    "AWS Rigetti Ankaa-3", 
    "AWS IQM Garnet", 
    "IBM Fez (Time-based)", 
    "AWS IonQ Forte"
]

costs = [36.25, 60.00, 87.50, 353.33, 4015.00]

# Crear DataFrame
df_costs = pd.DataFrame({
    'Provider': providers,
    'Cost': costs
})

# Ordenar de menor a mayor coste para que la gráfica quede más profesional
df_costs = df_costs.sort_values('Cost', ascending=True)

# ==========================================
# 3. GENERACIÓN DE LA GRÁFICA
# ==========================================
plt.figure(figsize=(10, 6))

# Crear gráfico de barras horizontales usando una paleta de colores académica
barplot = sns.barplot(
    x='Cost', 
    y='Provider', 
    data=df_costs, 
    palette="viridis",
    edgecolor="black"
)

# Añadir etiquetas de texto (con el símbolo del dólar) al final de cada barra
for i, p in enumerate(barplot.patches):
    width = p.get_width()
    plt.text(
        width + (max(costs) * 0.02), # Separación del texto de la barra
        p.get_y() + p.get_height() / 2,
        f'${width:,.2f}', 
        va='center', 
        ha='left', 
        fontsize=11, 
        fontweight='bold'
    )

# Configuración de etiquetas y título
plt.title('Projected Execution Costs: QML Inference (50 Circuits)', fontweight='bold', pad=15)
plt.xlabel('Total Cost (USD)', fontweight='bold')
plt.ylabel('QCaaS Provider & QPU', fontweight='bold')

# Ampliar el límite X para que el texto de IonQ ($4,015.00) no se corte por la derecha
plt.xlim(0, max(costs) * 1.15)

plt.tight_layout()

# Guardar la gráfica en alta resolución
plt.savefig('inference_costs_bar.png', dpi=300)
print("¡Gráfica 'inference_costs_bar.png' generada con éxito!")