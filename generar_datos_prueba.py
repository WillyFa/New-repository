import csv
import os
import random
from datetime import datetime, timedelta

output_dir = r"C:\Users\ASUS\.gemini\antigravity\scratch"

nodo_headers = [
    "ID_Localidad", "Nombre_Localidad", "Cuadrilla_NODO", 
    "Fecha_Inicio", "Fecha_Fin", "Serie_OLT", "Serie_ODF", 
    "Serie_SW", "Empalme_ODF_OK", "Reporte_Fotografico", "Observaciones"
]

pext_headers = [
    "ID_Localidad", "Nombre_Localidad", "Cuadrilla_PEXT",
    "Fecha_Inicio", "Fecha_Fin", "Metraje_Promedio_FO", "Span_Promedio_FO",
    "Cant_Postes_Nuevos", "Cant_Postes_Electricos", "Cant_Postes_Terceros",
    "Cant_Mufas_Dist", "Cant_CTO_NAPs", "Splitter_1x2_Cant", "Splitter_1x4_Cant",
    "Splitter_1x8_Cant", "Reservas_Mantenimiento_Crucetas", "Observaciones"
]

iao_headers = [
    "ID_Localidad", "Nombre_Localidad", "ID_IAO", "Tipo_IAO",
    "Cuadrilla_IAO", "Fecha_Inicio", "Fecha_Fin", "Metraje_Cable_Drop",
    "Armella_y_Templador_OK", "Recorrido_Grapas_OK", "Aterramiento_OK",
    "Ambiente_Instalacion", "Serie_Eq_1_ONT", "Serie_Eq_2_Switch",
    "Serie_Eq_3_Regleta", "Serie_Eq_4_Adicional", "Reporte_Fotografico", "Observaciones"
]

# Generación de datos de prueba
localidades = [
    ("LOC-001", "San Miguel de Pallaques"),
    ("LOC-002", "Huamachuco"),
    ("LOC-003", "Celendin"),
    ("LOC-004", "Cutervo"),
    ("LOC-005", "Chota")
]

cuadrillas_nodo = ["Cuadrilla NODO A", "Cuadrilla NODO B"]
cuadrillas_pext = ["Cuadrilla PEXT 1", "Cuadrilla PEXT 2", "Cuadrilla PEXT 3"]
cuadrillas_iao = ["Cuadrilla IAO X", "Cuadrilla IAO Y", "Cuadrilla IAO Z"]

tipos_iao = ["CS01", "IE01", "IE02", "IE03", "C001"]
ambientes = ["Sala RF", "Sala de Computo"]

def random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

def format_date(d):
    return d.strftime("%d/%m/%Y")

nodo_data = []
pext_data = []
iao_data = []

base_start = datetime(2023, 1, 1)
base_end = datetime(2023, 12, 31)

for id_loc, nom_loc in localidades:
    # Fechas simuladas
    inicio_nodo = random_date(base_start, base_end)
    fin_nodo = inicio_nodo + timedelta(days=random.randint(1, 5))
    
    inicio_pext = fin_nodo + timedelta(days=random.randint(1, 10))
    fin_pext = inicio_pext + timedelta(days=random.randint(7, 21))
    
    # Datos NODO
    nodo_data.append([
        id_loc, nom_loc, random.choice(cuadrillas_nodo),
        format_date(inicio_nodo), format_date(fin_nodo),
        f"OLT-{random.randint(1000, 9999)}", f"ODF-{random.randint(1000, 9999)}",
        f"SW-{random.randint(1000, 9999)}", "Sí", "Sí", "Instalación correcta en nodo."
    ])
    
    # Datos PEXT
    mufas = random.randint(2, 6)
    ctos = random.randint(5, 15)
    pext_data.append([
        id_loc, nom_loc, random.choice(cuadrillas_pext),
        format_date(inicio_pext), format_date(fin_pext),
        random.randint(2000, 5000), random.randint(40, 80),
        random.randint(10, 30), random.randint(20, 50), random.randint(0, 10),
        mufas, ctos,
        random.randint(0, mufas), mufas, ctos, # Splitters: 1x2(opcional), 1x4(mufas), 1x8(ctos obligatorio)
        random.randint(5, 15), "Tendido aéreo finalizado con uso de postes de MT."
    ])
    
    # Datos IAO
    num_iaos = random.randint(2, 5)
    for i in range(num_iaos):
        inicio_iao = fin_pext + timedelta(days=random.randint(1, 5))
        fin_iao = inicio_iao + timedelta(days=random.randint(1, 3))
        tipo = random.choice(tipos_iao)
        iao_data.append([
            id_loc, nom_loc, f"{id_loc}-{tipo}-{i+1}", tipo,
            random.choice(cuadrillas_iao), format_date(inicio_iao), format_date(fin_iao),
            random.randint(50, 150),
            "Sí", "Sí", "Sí", random.choice(ambientes),
            f"ONT-{random.randint(10000, 99999)}", f"SWA-{random.randint(10000, 99999)}",
            f"REG-{random.randint(10000, 99999)}", "-", "Sí", "Empalme de drop y conexión correctas."
        ])

def create_csv(filename, headers, data):
    filepath = os.path.join(output_dir, filename)
    with open(filepath, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=';') # CSV delimitado por punto y coma para Excel en español
        writer.writerow(headers)
        writer.writerows(data)

if __name__ == "__main__":
    create_csv("Prueba_BD_NODO.csv", nodo_headers, nodo_data)
    create_csv("Prueba_BD_PEXT.csv", pext_headers, pext_data)
    create_csv("Prueba_BD_IAO.csv", iao_headers, iao_data)
    print("Mock data templates generated successfully.")
