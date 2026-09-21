import pandas as pd
import traceback

def analizar_datos():
    try:
        # Cargar datos asegurando que el separador es correcto y limpiando espacios
        df_aws_cola = pd.read_csv("aws_cola.csv", sep=';', skipinitialspace=True)
        df_aws_estado = pd.read_csv("aws_estado.csv", sep=';', skipinitialspace=True)
        df_ibm_cola = pd.read_csv("ibm_cola.csv", sep=';', skipinitialspace=True)
        df_ibm_estado = pd.read_csv("ibm_estado.csv", sep=';', skipinitialspace=True)
        
        # Limpiar nombres de columnas por si hay espacios ocultos
        df_aws_cola.columns = df_aws_cola.columns.str.strip()
        df_aws_estado.columns = df_aws_estado.columns.str.strip()
        df_ibm_cola.columns = df_ibm_cola.columns.str.strip()
        df_ibm_estado.columns = df_ibm_estado.columns.str.strip()

        print("="*50)
        print(" RESUMEN TELEMÉTRICO PARA EL ARTÍCULO ")
        print("="*50)

        # --- CONVERSIÓN FORZADA A NUMÉRICO (FLOAT) ---
        # Esto evita el error 'TypeError: Cannot perform reduction 'mean' with string dtype'
        df_aws_cola['Tareas_Normales_Cola'] = pd.to_numeric(df_aws_cola['Tareas_Normales_Cola'], errors='coerce').astype(float)
        df_ibm_cola['Pending_Jobs'] = pd.to_numeric(df_ibm_cola['Pending_Jobs'], errors='coerce').astype(float)

        # --- ANÁLISIS DE COLAS AWS ---
        print("\n[1] COLAS AWS BRAKET:")
        for qpu in df_aws_cola['QPU_Name'].unique():
            datos_qpu = df_aws_cola[df_aws_cola['QPU_Name'] == qpu].dropna(subset=['Tareas_Normales_Cola'])
            if not datos_qpu.empty:
                max_cola = datos_qpu['Tareas_Normales_Cola'].max()
                media_cola = datos_qpu['Tareas_Normales_Cola'].mean()
                tiempo_libre = (len(datos_qpu[datos_qpu['Tareas_Normales_Cola'] == 0]) / len(datos_qpu)) * 100
                print(f"  - {qpu}: Máx={max_cola:.0f} tareas | Media={media_cola:.2f} | Libre el {tiempo_libre:.1f}% del tiempo")

        # --- ANÁLISIS DE COLAS IBM ---
        print("\n[2] COLAS IBM QUANTUM:")
        df_ibm_cola['Timestamp'] = pd.to_datetime(df_ibm_cola['Timestamp'], errors='coerce')
        df_ibm_cola['Hora'] = df_ibm_cola['Timestamp'].dt.hour
        
        for qpu in df_ibm_cola['Backend'].unique():
            datos_qpu = df_ibm_cola[df_ibm_cola['Backend'] == qpu].copy().dropna(subset=['Pending_Jobs'])
            if not datos_qpu.empty:
                max_cola = datos_qpu['Pending_Jobs'].max()
                media_cola = datos_qpu['Pending_Jobs'].mean()
                tiempo_libre = (len(datos_qpu[datos_qpu['Pending_Jobs'] == 0]) / len(datos_qpu)) * 100
                
                # Buscar "horas valle"
                horas_valle = datos_qpu.groupby('Hora')['Pending_Jobs'].mean().nsmallest(3)
                horas_valle_str = ", ".join([f"{int(h):02d}:00h ({val:.0f} jobs)" for h, val in horas_valle.items()])
                
                print(f"  - {qpu}: Máx={max_cola:.0f} jobs | Media={media_cola:.2f} | Libre el {tiempo_libre:.1f}% del tiempo")
                print(f"    * Mejores horas (UTC): {horas_valle_str}")

        # --- ANÁLISIS DE RUIDO AWS ---
        print("\n[3] ERROR DE LECTURA AWS BRAKET:")
        df_aws_estado['Fid_Lectura_%'] = pd.to_numeric(df_aws_estado['Fid_Lectura_%'], errors='coerce').astype(float)
        df_aws_estado['Error'] = 100.0 - df_aws_estado['Fid_Lectura_%']
        
        for qpu in df_aws_estado['QPU'].unique():
            datos_qpu = df_aws_estado[df_aws_estado['QPU'] == qpu]['Error'].dropna()
            if not datos_qpu.empty:
                print(f"  - {qpu}: Error Medio = {datos_qpu.mean():.2f}% | Peor pico = {datos_qpu.max():.2f}%")

        # --- ANÁLISIS DE RUIDO IBM ---
        print("\n[4] ERROR DE LECTURA IBM QUANTUM:")
        df_ibm_estado['Error_Lectura_Medio_%'] = pd.to_numeric(df_ibm_estado['Error_Lectura_Medio_%'], errors='coerce').astype(float)
        
        for qpu in df_ibm_estado['Backend'].unique():
            datos_qpu = df_ibm_estado[df_ibm_estado['Backend'] == qpu]['Error_Lectura_Medio_%'].dropna()
            if not datos_qpu.empty:
                print(f"  - {qpu}: Error Medio = {datos_qpu.mean():.2f}% | Peor pico = {datos_qpu.max():.2f}%")
                
        print("\n" + "="*50)

    except Exception as e:
        print("Ocurrió un error procesando los datos:")
        traceback.print_exc()

if __name__ == "__main__":
    analizar_datos()