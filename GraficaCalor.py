import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import copy
from datetime import timedelta

# ==========================================
# 1. FUNCIÓN BASE PARA EL MAPA DE CALOR (MATRIZ COMPLETA)
# ==========================================
def plot_github_style_heatmap(df, time_col, qpu_col, value_col, cmap_name, cbar_label, agg_func='max', vmax_limit=None, over_color='#000000', font_size=22):
    """
    Genera una matriz tipo GitHub: semanas en columnas y días en filas.
    """
    # Preparar las fechas y garantizar que los valores sean numéricos.
    df[time_col] = pd.to_datetime(df[time_col])
    df['Date'] = df[time_col].dt.date
    df[value_col] = pd.to_numeric(df[value_col], errors='coerce')

    # Completar el calendario para que todas las máquinas compartan las mismas semanas.
    first_date = df['Date'].min()
    last_date = df['Date'].max()
    first_monday = first_date - timedelta(days=first_date.weekday())
    last_monday = last_date - timedelta(days=last_date.weekday())
    week_starts = pd.date_range(first_monday, last_monday, freq='7D').date

    df['Week'] = df['Date'].map(lambda date: date - timedelta(days=date.weekday()))
    df['Weekday'] = df[time_col].dt.weekday
    qpus = df[qpu_col].dropna().unique()
    
    # Configurar el mapa de colores para capar valores máximos
    cmap = copy.copy(plt.get_cmap(cmap_name))
    
    # Argumentos extra para la barra de color.
    cbar_kwargs = {'label': cbar_label, 'extend': 'max'} if vmax_limit is not None else {'label': cbar_label}
    if vmax_limit is not None:
        cmap.set_over(over_color)
    color_vmin = df[value_col].min()
    color_vmax = vmax_limit if vmax_limit is not None else df[value_col].max()

    # Un panel por QPU/backend, como una contribución de GitHub por repositorio.
    fig, axes = plt.subplots(
        len(qpus), 1, figsize=(12, max(4, 2.4 * len(qpus))),
        squeeze=False, sharex=True, constrained_layout=True
    )
    axes = axes.ravel()
    day_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    month_groups = {}
    for week_index, week in enumerate(week_starts):
        month_groups.setdefault(week.strftime('%b %Y'), []).append(week_index)
    month_centers = [sum(indices) / len(indices) + 0.5 for indices in month_groups.values()]
    month_labels = list(month_groups)
    heatmap_mesh = None

    for panel_index, (ax, qpu) in enumerate(zip(axes, qpus)):
        qpu_data = df[df[qpu_col] == qpu]
        pivot_df = qpu_data.pivot_table(index='Weekday', columns='Week', values=value_col, aggfunc=agg_func)
        pivot_df = pivot_df.reindex(index=range(7), columns=week_starts)

        sns.heatmap(
            pivot_df, ax=ax, cmap=cmap, linewidths=2, linecolor='white',
            cbar=False, annot=False, vmin=color_vmin, vmax=color_vmax
        )
        heatmap_mesh = ax.collections[0]
        ax.set_title(str(qpu), fontweight='bold', fontsize=font_size)
        ax.set_ylabel('Day', fontweight='bold', fontsize=font_size)
        ax.set_xlabel('')
        ax.set_yticks([day_index + 0.5 for day_index in range(7)])
        ax.set_yticklabels(day_labels, rotation=0, fontsize=font_size)
        ax.set_xticks(month_centers)
        ax.set_xticklabels(month_labels, rotation=0, fontsize=font_size)

        # Separar visualmente las semanas cuando comienza un nuevo mes.
        for column_index in range(1, len(week_starts)):
            if week_starts[column_index].month != week_starts[column_index - 1].month:
                ax.axvline(column_index, color='black', linewidth=3)

    axes[-1].set_xlabel('Month', fontweight='bold', fontsize=font_size)
    colorbar = fig.colorbar(
        heatmap_mesh, ax=axes.tolist(), pad=0.02, aspect=30,
        extend=cbar_kwargs.get('extend')
    )
    colorbar.ax.tick_params(labelsize=font_size)
    colorbar.set_label(cbar_label, fontsize=font_size, fontweight='bold')
    if vmax_limit is not None:
        colorbar.ax.text(
            0.5, 1.06, f'> {vmax_limit:,}',
            transform=colorbar.ax.transAxes, ha='center', va='bottom',
            fontsize=font_size, fontweight='bold', color=over_color
        )
    fig.suptitle(cbar_label, fontweight='bold', fontsize=font_size + 2)
    plt.show()

# ==========================================
# 2. CARGA Y TRANSFORMACIÓN DE DATOS
# ==========================================
archivo_aws_cola = "aws_cola.csv"
archivo_aws_estado = "aws_estado.csv"
archivo_ibm_cola = "ibm_cola.csv"
archivo_ibm_estado = "ibm_estado.csv"

try:
    df_aws_cola = pd.read_csv(archivo_aws_cola, sep=';')
    df_aws_estado = pd.read_csv(archivo_aws_estado, sep=';')
    df_ibm_cola = pd.read_csv(archivo_ibm_cola, sep=';')
    df_ibm_estado = pd.read_csv(archivo_ibm_estado, sep=';')
except FileNotFoundError as e:
    print(f"Error: Not found {e.filename}.")
    exit()

# Transformación clave: Convertir Fidelidad de AWS a Error para poder compararlo visualmente con IBM
df_aws_estado['Fid_Lectura_%'] = pd.to_numeric(df_aws_estado['Fid_Lectura_%'], errors='coerce')
df_aws_estado['Error_Lectura_Calculado_%'] = 100 - df_aws_estado['Fid_Lectura_%']

# ==========================================
# 3. GENERACIÓN DE LOS GRÁFICOS
# ==========================================

# Gráfico 1: Colas de AWS (CAPADO A 1.000)
plot_github_style_heatmap(
    df=df_aws_cola, 
    time_col='Timestamp', qpu_col='QPU_Name', value_col='Tareas_Normales_Cola',
    cmap_name="Blues", 
    cbar_label="Max Pending Jobs", 
    agg_func='max',
    vmax_limit=500, 
    over_color='#000000'
)

# Gráfico 2: ERROR de Lectura AWS (Homogeneizado con IBM)
plot_github_style_heatmap(
    df=df_aws_estado, 
    time_col='Timestamp', qpu_col='QPU', value_col='Error_Lectura_Calculado_%',
    cmap_name="Reds", 
    cbar_label="Mean Readout Error (%)", 
    agg_func='mean'
)

# Gráfico 3: Colas de IBM (CAPADO A 10.000)
plot_github_style_heatmap(
    df=df_ibm_cola, 
    time_col='Timestamp', qpu_col='Backend', value_col='Pending_Jobs',
    cmap_name="YlOrRd", 
    cbar_label="Max Pending Jobs", 
    agg_func='max',
    vmax_limit=10000, 
    over_color='#000000'
)

# Gráfico 4: Error de Lectura IBM
plot_github_style_heatmap(
    df=df_ibm_estado, 
    time_col='Timestamp', qpu_col='Backend', value_col='Error_Lectura_Medio_%',
    cmap_name="Reds", 
    cbar_label="Mean Readout Error (%)", 
    agg_func='mean'
)