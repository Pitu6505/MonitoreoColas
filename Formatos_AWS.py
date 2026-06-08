from braket.aws import AwsDevice
import json

# Los tres ARNs exactos que vas a investigar
ARNS = [
    "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
    "arn:aws:braket:eu-north-1::device/qpu/iqm/Garnet",
    "arn:aws:braket:us-east-1::device/qpu/ionq/Forte-1"
]

print("Extrayendo archivos de calibración JSON de AWS Braket...")

for arn in ARNS:
    try:
        device = AwsDevice(arn)
        props = device.properties.dict() # Obtenemos todo el diccionario
        
        # Limpiamos el nombre para el archivo
        nombre_archivo = f"calibracion_{device.name}.json"
        
        # Guardamos el JSON con indentación para que sea fácil de leer
        with open(nombre_archivo, 'w') as f:
            json.dump(props, f, indent=4)
            
        print(f"✅ Guardado con éxito: {nombre_archivo}")
        
    except Exception as e:
        print(f"❌ Error al consultar {arn}: {e}")

print("¡Proceso terminado!")