import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configurar el estilo de las gráficas
sns.set_theme(style="whitegrid")

def generar_graficas():
    print("Generando gráfica de colas de AWS...")
    try:
        df_aws_colas = pd.read_csv("registro_colas_aws.csv", sep=";")
        df_aws_colas['Timestamp'] = pd.to_datetime(df_aws_colas['Timestamp'])
        
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=df_aws_colas, x='Timestamp', y='Tareas_Normales_Cola', hue='QPU_Name')
        plt.title("AWS: Evolución de las Tareas en Cola a lo largo del tiempo")
        plt.xlabel("Fecha")
        plt.ylabel("Tareas en Cola (Normales)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("aws_colas.png", dpi=150)
        plt.close()
    except Exception as e:
        print(f"Error al generar gráfica de AWS Colas: {e}")

    print("Generando gráfica de colas de IBM...")
    try:
        df_ibm_colas = pd.read_csv("registro_colas_ibm.csv", sep=";")
        df_ibm_colas['Timestamp'] = pd.to_datetime(df_ibm_colas['Timestamp'])
        
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=df_ibm_colas, x='Timestamp', y='Pending_Jobs', hue='Backend')
        plt.title("IBM: Evolución de Trabajos Pendientes en la Cola")
        plt.xlabel("Fecha")
        plt.ylabel("Trabajos Pendientes")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("ibm_colas.png", dpi=150)
        plt.close()
    except Exception as e:
        print(f"Error al generar gráfica de IBM Colas: {e}")

    print("Generando gráfica de ruido de AWS...")
    try:
        # Leemos tratando los 'N/A' correctamente
        df_aws_ruido = pd.read_csv("registro_ruido_aws.csv", sep=";", na_values=['N/A'])
        
        # Aseguramos que las columnas de fidelidad son numéricas
        cols_fidelidad = ['Fid_Media_1Q_%', 'Fid_Media_2Q_%', 'Fid_Lectura_%']
        for col in cols_fidelidad:
            df_aws_ruido[col] = pd.to_numeric(df_aws_ruido[col], errors='coerce')
        
        # Reorganizamos los datos para que Seaborn pueda hacer un boxplot múltiple fácilmente
        df_aws_ruido_melted = df_aws_ruido.melt(
            id_vars=['QPU'], 
            value_vars=cols_fidelidad,
            var_name='Métrica', 
            value_name='Fidelidad (%)'
        )
        
        plt.figure(figsize=(12, 6))
        sns.boxplot(data=df_aws_ruido_melted, x='Métrica', y='Fidelidad (%)', hue='QPU')
        plt.title("AWS: Distribución de las Fidelidades (Ruido) por QPU")
        plt.xlabel("Métrica de Fidelidad")
        plt.ylabel("Porcentaje de Fidelidad (%)")
        plt.tight_layout()
        plt.savefig("aws_ruido.png", dpi=150)
        plt.close()
    except Exception as e:
        print(f"Error al generar gráfica de AWS Ruido: {e}")

    print("Generando gráficas de ruido y coherencia de IBM...")
    try:
        df_ibm_ruido = pd.read_csv("registro_ruido_ibm.csv", sep=";", na_values=['N/A'])
        
        # Creamos una figura con dos subgráficas (1 fila, 2 columnas)
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Subgráfica 1: Tiempos de coherencia (T1 y T2)
        df_ibm_coh = df_ibm_ruido.melt(
            id_vars=['Backend'], 
            value_vars=['T1_Medio_us', 'T2_Medio_us'],
            var_name='Métrica', 
            value_name='Tiempo (us)'
        )
        sns.boxplot(data=df_ibm_coh, x='Métrica', y='Tiempo (us)', hue='Backend', ax=axes[0])
        axes[0].set_title("IBM: Tiempos de Coherencia (T1 y T2)")
        axes[0].set_xlabel("Métrica")
        axes[0].set_ylabel("Microsegundos (us)")
        
        # Subgráfica 2: Error de Lectura
        sns.boxplot(data=df_ibm_ruido, x='Backend', y='Error_Lectura_Medio_%', ax=axes[1])
        axes[1].set_title("IBM: Error de Lectura Medio (%)")
        axes[1].set_xlabel("Backend")
        axes[1].set_ylabel("Error de Lectura (%)")
        
        plt.tight_layout()
        plt.savefig("ibm_ruido.png", dpi=150)
        plt.close()
    except Exception as e:
        print(f"Error al generar gráfica de IBM Ruido: {e}")

    print("¡Proceso terminado! Revisa la carpeta para ver las imágenes.")

if __name__ == "__main__":
    generar_graficas()