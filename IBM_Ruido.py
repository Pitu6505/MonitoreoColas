from qiskit_ibm_runtime import QiskitRuntimeService
import numpy as np
import time
import datetime
import csv

# --- CONFIGURACIÓN ---
IBM_TOKEN = "" 
IBM_INSTANCE =  ""
BACKENDS = ['ibm_fez', 'ibm_kingston', 'ibm_marrakesh']

service = QiskitRuntimeService(channel="ibm_cloud", token=IBM_TOKEN, instance=IBM_INSTANCE)
archivo_salida = "registro_ruido_ibm.csv"

with open(archivo_salida, mode='a', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    if file.tell() == 0:
        writer.writerow(["Timestamp", "Backend", "T1_Medio_us", "T2_Medio_us", "Error_Lectura_Medio_%"])

print("Iniciando monitorización de ruido en IBM. Consultando cada 12 horas...")

try:
    while True:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for qpu_name in BACKENDS:
            try:
                backend = service.backend(qpu_name)
                prop = backend.properties()
                
                if prop is not None:
                    t1_vals = []
                    t2_vals = []
                    readout_errors = []
                    
                    # Recorremos cada qubit y usamos try-except para ignorar los defectuosos
                    for q in range(backend.num_qubits):
                        try:
                            t1_vals.append(prop.t1(q) * 1e6)
                        except Exception:
                            pass # Ignora si falta el T1
                            
                        try:
                            t2_vals.append(prop.t2(q) * 1e6)
                        except Exception:
                            pass # Ignora si falta el T2
                            
                        try:
                            readout_errors.append(prop.readout_error(q) * 100)
                        except Exception:
                            pass # Ignora si falta el error de lectura
                    
                    # Calculamos la media solo con los qubits que sí tienen datos válidos
                    t1_avg = np.mean(t1_vals) if t1_vals else 0
                    t2_avg = np.mean(t2_vals) if t2_vals else 0
                    readout_avg = np.mean(readout_errors) if readout_errors else 0
                    
                    with open(archivo_salida, mode='a', newline='') as file:
                        csv.writer(file, delimiter=';').writerow([now, qpu_name, round(t1_avg, 2), round(t2_avg, 2), round(readout_avg, 2)])
                    
                    print(f"[{now}] {qpu_name}: T1={t1_avg:.2f}us | T2={t2_avg:.2f}us | Error Lectura={readout_avg:.2f}%")
                else:
                    print(f"[{now}] El backend {qpu_name} no tiene propiedades físicas disponibles ahora mismo.")
                    
            except Exception as e:
                print(f"[{now}] Error en {qpu_name}: {e}")
                
        # Consultamos cada 12 horas
        time.sleep(43200) 
except KeyboardInterrupt:
    print("\nMonitorización de ruido detenida.")