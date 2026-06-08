import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

# ==========================================
# 1. CONFIGURACIÓN VISUAL PARA EL PAPER
# ==========================================
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("paper", font_scale=1.2)

# ==========================================
# 2. DATOS DEL CASO DE USO 2 (245,760 Circuitos)
# ==========================================
providers = [
    "AWS Rigetti Cepheus", 
    "AWS Rigetti Ankaa-3", 
    "AWS IQM Garnet", 
    "IBM Fez (Time-based)", 
    "AWS IonQ Forte"
]

# Costes astronómicos del entrenamiento
costs = [178176.00, 294912.00, 430080.00, 1736704.00, 19734528.00]

# Crear DataFrame y ordenar
df_costs = pd.DataFrame({
    'Provider': providers,
    'Cost': costs
})
df_costs = df_costs.sort_values('Cost', ascending=True)

# ==========================================
# 3. GENERACIÓN DE LA GRÁFICA (ESCALA LOGARÍTMICA)
# ==========================================
plt.figure(figsize=(10, 6))

# Usamos la paleta "magma" para dar sensación de intensidad/coste elevado
barplot = sns.barplot(
    x='Cost', 
    y='Provider', 
    data=df_costs, 
    palette="magma",
    edgecolor="black"
)

# Aplicar escala logarítmica al eje X
plt.xscale('log')

# Formatear el eje X para que muestre números legibles en lugar de 10^x
formatter = ticker.FuncFormatter(lambda y, _: f'${y:,.0f}')
plt.gca().xaxis.set_major_formatter(formatter)

# Añadir etiquetas de texto a cada barra
for i, p in enumerate(barplot.patches):
    width = p.get_width()
    # En escala logarítmica, la posición del texto necesita un multiplicador
    plt.text(
        width * 1.2, 
        p.get_y() + p.get_height() / 2,
        f'${width:,.0f}', 
        va='center', 
        ha='left', 
        fontsize=11, 
        fontweight='bold'
    )

# Configuración de etiquetas y título
plt.title('Projected Execution Costs: QML Hybrid Training (245,760 Circuits)', fontweight='bold', pad=15)
plt.xlabel('Total Cost (USD) - Logarithmic Scale', fontweight='bold')
plt.ylabel('QCaaS Provider & QPU', fontweight='bold')

# Ajustar límites del eje X para que quepa el texto (desde 10^4 hasta 10^8)
plt.xlim(10000, 100000000)

plt.tight_layout()

# Guardar la gráfica
plt.savefig('training_costs_log.png', dpi=300)
print("¡Gráfica 'training_costs_log.png' generada con éxito!")