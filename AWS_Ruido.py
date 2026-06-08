from braket.aws import AwsDevice
import time
import datetime
import csv

# Los ARNs exactos
ARNS = [
    "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
    "arn:aws:braket:eu-north-1::device/qpu/iqm/Garnet",
    "arn:aws:braket:us-east-1::device/qpu/ionq/Forte-1"
]

archivo_salida = "registro_ruido_aws.csv"

# Crear archivo y cabeceras si no existe
with open(archivo_salida, mode='a', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    if file.tell() == 0:
        writer.writerow(["Timestamp", "QPU", "Fid_Media_1Q_%", "Fid_Media_2Q_%", "Fid_Lectura_%"])

print("Monitoreando ruido en AWS Braket (usando credenciales locales)...")

try:
    while True:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for arn in ARNS:
            try:
                device = AwsDevice(arn)
                
                # Intentamos extraer las propiedades estandarizadas primero, si no, las generales
                if hasattr(device.properties, 'standardized') and device.properties.standardized:
                    props = device.properties.standardized.dict()
                else:
                    props = device.properties.dict()

                fid_1q_avg = "N/A"
                fid_2q_avg = "N/A"
                readout_avg = "N/A"

                # ---------------------------------------------------------
                # CASO 1: Estructura Global (IonQ Forte)
                # ---------------------------------------------------------
                # Basado en el JSON que me has pasado:
                if 'readoutFidelity' in props or 'twoQubitGateFidelity' in props:
                    # Lectura (Readout)
                    read_list = props.get('readoutFidelity', [])
                    if read_list and isinstance(read_list, list) and len(read_list) > 0:
                        readout_avg = round(read_list[0].get('fidelity', 0) * 100, 2)
                    
                    # Puertas de 2 Qubits
                    tq_list = props.get('twoQubitGateFidelity', [])
                    if tq_list and isinstance(tq_list, list) and len(tq_list) > 0:
                        fid_2q_avg = round(tq_list[0].get('fidelity', 0) * 100, 2)
                        
                    # IonQ normalmente asume que la fidelidad 1Q es >99.99% y a veces no la reporta globalmente
                    # Si la encontramos, la guardamos, si no, se queda en "N/A"
                    sq_list = props.get('oneQubitGateFidelity', [])
                    if sq_list and isinstance(sq_list, list) and len(sq_list) > 0:
                        fid_1q_avg = round(sq_list[0].get('fidelity', 0) * 100, 2)

                # ---------------------------------------------------------
                # CASO 2: Estructura por Qubit (Rigetti Cepheus e IQM Garnet)
                # ---------------------------------------------------------
                elif 'oneQubitProperties' in props:
                    q1_fids = []
                    read_fids = []
                    
                    for q, q_props in props.get('oneQubitProperties', {}).items():
                        for fid_info in q_props.get('oneQubitFidelity', []):
                            name = fid_info.get('fidelityType', {}).get('name', '')
                            val = fid_info.get('fidelity', 0)
                            
                            if name == 'READOUT':
                                read_fids.append(val)
                            elif 'RANDOMIZED_BENCHMARKING' in name:
                                q1_fids.append(val)
                                
                    if q1_fids: fid_1q_avg = round((sum(q1_fids) / len(q1_fids)) * 100, 2)
                    if read_fids: readout_avg = round((sum(read_fids) / len(read_fids)) * 100, 2)
                    
                    # Puertas de 2 Qubits para superconductores
                    if 'twoQubitProperties' in props:
                        q2_fids = []
                        for edge, edge_props in props.get('twoQubitProperties', {}).items():
                            for fid_info in edge_props.get('twoQubitGateFidelity', []):
                                q2_fids.append(fid_info.get('fidelity', 0))
                                
                        if q2_fids: fid_2q_avg = round((sum(q2_fids) / len(q2_fids)) * 100, 2)

                # Guardar resultados
                with open(archivo_salida, mode='a', newline='') as file:
                    csv.writer(file, delimiter=';').writerow([now, device.name, fid_1q_avg, fid_2q_avg, readout_avg])
                
                print(f"[{now}] {device.name}: 1Q={fid_1q_avg}% | 2Q={fid_2q_avg}% | Lectura={readout_avg}%")
                
            except Exception as e:
                print(f"[{now}] Error consultando {arn}: {e}")
                
        # Consultamos cada 12 horas (43200 segundos)
        time.sleep(43200) 
        
except KeyboardInterrupt:
    print("\nDetenido.")