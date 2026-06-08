from braket.aws import AwsDevice
import time
import datetime
import csv

# Lista de ARNs de las QPUs que estás analizando en el artículo
arns_to_monitor = [
    "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
    "arn:aws:braket:eu-north-1::device/qpu/iqm/Garnet",
    "arn:aws:braket:us-east-1::device/qpu/ionq/Forte-1"
]

archivo_salida = "registro_colas_aws.csv"

# Escribimos la cabecera si el archivo no existe
with open(archivo_salida, mode='a', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(["Timestamp", "QPU_Name", "Estado", "Tareas_Normales_Cola", "Trabajos_Hibridos_Cola"])

print("Iniciando monitorización de colas en AWS Braket. Pulsa Ctrl+C para detener.")

try:
    while True:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for arn in arns_to_monitor:
            try:
                # Conectarse al dispositivo
                device = AwsDevice(arn)
                
                # Obtener si la máquina está ONLINE, OFFLINE, etc.
                estado = device.status
                
                # Obtener la profundidad de la cola
                cola = device.queue_depth()
                
                # AWS devuelve un objeto con dos atributos principales:
                # quantum_tasks (tareas estándar) y jobs (trabajos prioritarios/híbridos)
                # Como es un diccionario, extraemos la cuenta normal:
                tareas_normales = cola.quantum_tasks.get('Normal', 0)
                trabajos_hibridos = cola.jobs
                
                # Guardar en el CSV
                with open(archivo_salida, mode='a', newline='') as file:
                    writer = csv.writer(file, delimiter=';')
                    writer.writerow([now, device.name, estado, tareas_normales, trabajos_hibridos])
                
                print(f"[{now}] {device.name} ({estado}): {tareas_normales} Tareas en cola | {trabajos_hibridos} Trabajos Híbridos.")
                
            except Exception as e:
                print(f"[{now}] Error consultando {arn}: {e}")
                
        # Esperar 1 hora (3600 segundos) antes de volver a consultar
        time.sleep(3600)
        
except KeyboardInterrupt:
    print("\nMonitorización de AWS detenida.")