from qiskit_ibm_runtime import QiskitRuntimeService
import time, datetime, csv

# --- CONFIGURACIÓN DE CREDENCIALES ---
IBM_TOKEN = ""
IBM_INSTANCE = "" 
BACKENDS = ['ibm_fez', 'ibm_kingston', 'ibm_marrakesh']

# Inicializar servicio en una línea
service = QiskitRuntimeService(channel="ibm_cloud", token=IBM_TOKEN, instance=IBM_INSTANCE)

archivo_salida = "registro_colas_ibm.csv"
with open(archivo_salida, mode='a', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    if file.tell() == 0: writer.writerow(["Timestamp", "Backend", "Pending_Jobs", "Status"])

print(f"Monitoreando IBM con Token: {IBM_TOKEN[:5]}...")

try:
    while True:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for qpu_name in BACKENDS:
            try:
                backend = service.backend(qpu_name)
                status = backend.status()
                with open(archivo_salida, mode='a', newline='') as file:
                    csv.writer(file, delimiter=';').writerow([now, qpu_name, status.pending_jobs, status.operational])
                print(f"[{now}] {qpu_name}: {status.pending_jobs} trabajos.")
            except Exception as e: print(f"Error en {qpu_name}: {e}")
        time.sleep(3600)
except KeyboardInterrupt: print("Detenido.")