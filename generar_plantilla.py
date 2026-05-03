import csv
import os

output_dir = r"C:\Users\ASUS\.gemini\antigravity\scratch"

# Categoría NODO
nodo_headers = [
    "ID_Localidad", "Nombre_Localidad", "Cuadrilla_NODO", 
    "Fecha_Inicio", "Fecha_Fin", "Serie_OLT", "Serie_ODF", 
    "Serie_SW", "Empalme_ODF_OK", "Reporte_Fotografico", "Observaciones"
]

# Categoría PEXT
pext_headers = [
    "ID_Localidad", "Nombre_Localidad", "Cuadrilla_PEXT",
    "Fecha_Inicio", "Fecha_Fin", "Metraje_Promedio_FO", "Span_Promedio_FO",
    "Cant_Postes_Nuevos", "Cant_Postes_Electricos", "Cant_Postes_Terceros",
    "Cant_Mufas_Dist", "Cant_CTO_NAPs", "Splitter_1x2_Cant", "Splitter_1x4_Cant",
    "Splitter_1x8_Cant", "Reservas_Mantenimiento_Crucetas", "Observaciones"
]

# Categoría IAO
iao_headers = [
    "ID_Localidad", "Nombre_Localidad", "ID_IAO", "Tipo_IAO",
    "Cuadrilla_IAO", "Fecha_Inicio", "Fecha_Fin", "Metraje_Cable_Drop",
    "Armella_y_Templador_OK", "Recorrido_Grapas_OK", "Aterramiento_OK",
    "Ambiente_Instalacion", "Serie_Eq_1_ONT", "Serie_Eq_2_Switch",
    "Serie_Eq_3_Regleta", "Serie_Eq_4_Adicional", "Reporte_Fotografico", "Observaciones"
]

def create_csv(filename, headers):
    filepath = os.path.join(output_dir, filename)
    with open(filepath, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(headers)

if __name__ == "__main__":
    create_csv("Plantilla_BD_NODO.csv", nodo_headers)
    create_csv("Plantilla_BD_PEXT.csv", pext_headers)
    create_csv("Plantilla_BD_IAO.csv", iao_headers)
    print("CSV templates generated successfully.")
