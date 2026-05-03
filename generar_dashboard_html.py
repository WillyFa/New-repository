import csv
import os
import json

output_dir = r"C:\Users\ASUS\.gemini\antigravity\scratch"

def run():
    # 1. Leer datos CSV
    pext_data = []
    with open(os.path.join(output_dir, "Prueba_BD_PEXT.csv"), "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader: pext_data.append(row)

    iao_data = []
    with open(os.path.join(output_dir, "Prueba_BD_IAO.csv"), "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader: iao_data.append(row)

    # Lista única de localidades
    localidades_dict = {}
    for r in pext_data:
        localidades_dict[r["ID_Localidad"]] = r["Nombre_Localidad"]
    
    localidades = [{"id": k, "nombre": v} for k, v in localidades_dict.items()]

    pext_json = json.dumps(pext_data)
    iao_json = json.dumps(iao_data)
    localidades_json = json.dumps(localidades)

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FTTH Pronatel - Dashboard Directivo</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --card-border: rgba(255, 255, 255, 0.1);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-1: #3b82f6;
            --accent-2: #10b981;
            --accent-3: #8b5cf6;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }}

        body {{
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.15) 0px, transparent 50%);
            background-attachment: fixed;
            color: var(--text-primary);
            min-height: 100vh;
            padding: 2rem;
        }}

        .header {{ margin-bottom: 2rem; text-align: center; }}
        .header h1 {{ font-size: 2.2rem; font-weight: 800; background: linear-gradient(to right, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; }}
        
        .filter-container {{ display: flex; justify-content: center; align-items: center; gap: 1rem; margin-bottom: 1.5rem; }}
        .filter-container label {{ font-weight: 600; color: var(--text-secondary); font-size: 0.9rem; }}
        select {{
            background-color: rgba(15, 23, 42, 0.8);
            color: var(--text-primary);
            border: 1px solid var(--accent-1);
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            font-size: 0.9rem;
            font-weight: 600;
            outline: none;
            cursor: pointer;
        }}

        .dashboard-grid {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 1rem; max-width: 1400px; margin: 0 auto; }}
        
        .card {{
            background: var(--card-bg); backdrop-filter: blur(12px); border: 1px solid var(--card-border);
            border-radius: 1rem; padding: 1.2rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        }}

        .kpi-card {{ grid-column: span 4; text-align: center; padding: 1.5rem 1rem; }}
        @media (max-width: 1024px) {{ .kpi-card {{ grid-column: span 12; }} }}

        .kpi-value {{ font-size: 2.5rem; font-weight: 800; margin: 0.3rem 0; color: var(--text-primary); transition: opacity 0.3s ease; }}
        .kpi-label {{ color: var(--text-secondary); font-size: 0.85rem; text-transform: uppercase; font-weight: 600; }}

        .kpi-1 .kpi-value {{ color: var(--accent-1); }}
        .kpi-2 .kpi-value {{ color: var(--accent-2); }}
        .kpi-3 .kpi-value {{ color: var(--accent-3); }}

        /* REDUCED SIZE CHART CONTAINERS */
        .chart-container {{ grid-column: span 4; min-height: 250px; display: flex; flex-direction: column; }}
        .chart-wrapper {{ position: relative; flex-grow: 1; height: 100%; min-height: 200px; }}
        @media (max-width: 1024px) {{ .chart-container {{ grid-column: span 12; min-height: 300px; }} }}
        
        .chart-title {{ font-size: 1rem; font-weight: 600; margin-bottom: 0.8rem; color: var(--text-primary); text-align: center; }}

        .table-container {{ grid-column: span 12; margin-top: 1rem; padding: 1.5rem; overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; }}
        th, td {{ padding: 0.8rem; border-bottom: 1px solid var(--card-border); }}
        th {{ color: var(--accent-1); font-weight: 600; font-size: 0.85rem; }}
        td {{ color: var(--text-primary); font-size: 0.9rem; }}
    </style>
</head>
<body>

    <div class="header">
        <h1>Control Estratégico FTTH</h1>
        <div class="filter-container">
            <label for="localidadFilter">📍 Filtrar por Localidad:</label>
            <select id="localidadFilter" onchange="updateDashboard()">
                <option value="ALL">🌐 Todas las Localidades</option>
            </select>
        </div>
    </div>

    <div class="dashboard-grid">
        <!-- KPIs -->
        <div class="card kpi-card kpi-1">
            <div class="kpi-label">Fibra Óptica Desplegada</div>
            <div class="kpi-value" id="valFO">0 <span style="font-size:1.2rem">m</span></div>
        </div>
        <div class="card kpi-card kpi-2">
            <div class="kpi-label">Total IAOs Instaladas</div>
            <div class="kpi-value" id="valIAO">0</div>
        </div>
        <div class="card kpi-card kpi-3">
            <div class="kpi-label">Postes Intervenidos</div>
            <div class="kpi-value" id="valPostes">0</div>
        </div>

        <!-- Charts en 3 columnas para que sean más pequeños -->
        <div class="card chart-container">
            <h2 class="chart-title">Tipos de IAO (Barras Horizontales)</h2>
            <div class="chart-wrapper"><canvas id="chartTipos"></canvas></div>
        </div>

        <div class="card chart-container">
            <h2 class="chart-title">Postes Usados (Dona)</h2>
            <div class="chart-wrapper"><canvas id="chartPostes"></canvas></div>
        </div>

        <div class="card chart-container">
            <h2 class="chart-title">IAOs por Cuadrilla (Barras)</h2>
            <div class="chart-wrapper"><canvas id="chartCuadrillas"></canvas></div>
        </div>
        
        <!-- Tabla de Detalle -->
        <div class="card table-container" id="detailsSection" style="display: none;">
            <h2 class="chart-title" style="text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 1rem;">📋 Detalle Local</h2>
            <table id="iaoTable">
                <thead>
                    <tr>
                        <th>ID IAO</th>
                        <th>Tipo</th>
                        <th>Cuadrilla</th>
                        <th>Drop (m)</th>
                        <th>Serie ONT</th>
                        <th>Ambiente</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>

    <script>
        const rawPext = {pext_json};
        const rawIao = {iao_json};
        const localidades = {localidades_json};

        const selectElement = document.getElementById('localidadFilter');
        localidades.forEach(loc => {{
            let option = document.createElement('option');
            option.value = loc.id; option.textContent = loc.nombre + " (" + loc.id + ")"; selectElement.appendChild(option);
        }});

        Chart.defaults.color = '#94a3b8';
        Chart.defaults.font.family = "'Inter', sans-serif";
        const colors = ['#3b82f6', '#10b981', '#8b5cf6', '#f59e0b', '#ec4899'];

        let chartTiposInstance, chartPostesInstance, chartCuadrillasInstance;

        function initCharts() {{
            // 1. Barras Horizontales para Tipos
            chartTiposInstance = new Chart(document.getElementById('chartTipos'), {{
                type: 'bar', 
                data: {{ labels: [], datasets: [{{ data: [], backgroundColor: '#3b82f6', borderRadius: 4 }}] }},
                options: {{ 
                    indexAxis: 'y', 
                    responsive: true, maintainAspectRatio: false, 
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{ x: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }} }}, y: {{ grid: {{ display: false }} }} }}
                }}
            }});

            // 2. Dona para Postes
            chartPostesInstance = new Chart(document.getElementById('chartPostes'), {{
                type: 'doughnut', 
                data: {{ labels: ["Nuevos", "Eléctricos", "Terceros"], datasets: [{{ data: [], backgroundColor: ['#10b981', '#3b82f6', '#f59e0b'], borderWidth: 0, cutout: '65%' }}] }},
                options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'bottom', labels: {{ padding: 15, boxWidth: 12 }} }} }} }}
            }});

            // 3. Barras Verticales para Cuadrillas
            chartCuadrillasInstance = new Chart(document.getElementById('chartCuadrillas'), {{
                type: 'bar', 
                data: {{ labels: [], datasets: [{{ data: [], backgroundColor: '#8b5cf6', borderRadius: 4 }}] }},
                options: {{ 
                    responsive: true, maintainAspectRatio: false, 
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{ y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }} }}, x: {{ grid: {{ display: false }} }} }}
                }}
            }});
        }}

        function updateDashboard() {{
            const selectedLoc = selectElement.value;
            let fPext = selectedLoc === "ALL" ? rawPext : rawPext.filter(d => d.ID_Localidad === selectedLoc);
            let fIao = selectedLoc === "ALL" ? rawIao : rawIao.filter(d => d.ID_Localidad === selectedLoc);

            let totalFO = 0; let postesN = 0, postesE = 0, postesT = 0;
            fPext.forEach(p => {{
                let valFO = parseFloat(p.Metraje_Promedio_FO.replace('.', '').replace(',', '.'));
                if(!isNaN(valFO)) totalFO += valFO;
                postesN += parseInt(p.Cant_Postes_Nuevos) || 0;
                postesE += parseInt(p.Cant_Postes_Electricos) || 0;
                postesT += parseInt(p.Cant_Postes_Terceros) || 0;
            }});

            document.getElementById('valFO').innerHTML = totalFO.toLocaleString('en-US') + ' <span style="font-size:1.2rem">m</span>';
            document.getElementById('valIAO').innerText = fIao.length;
            document.getElementById('valPostes').innerText = (postesN + postesE + postesT);

            let countTipos = {{}}; let countCuadrillas = {{}};
            fIao.forEach(i => {{
                countTipos[i.Tipo_IAO] = (countTipos[i.Tipo_IAO] || 0) + 1;
                countCuadrillas[i.Cuadrilla_IAO] = (countCuadrillas[i.Cuadrilla_IAO] || 0) + 1;
            }});

            chartTiposInstance.data.labels = Object.keys(countTipos);
            chartTiposInstance.data.datasets[0].data = Object.values(countTipos);
            chartTiposInstance.update();

            chartPostesInstance.data.datasets[0].data = [postesN, postesE, postesT];
            chartPostesInstance.update();

            chartCuadrillasInstance.data.labels = Object.keys(countCuadrillas);
            chartCuadrillasInstance.data.datasets[0].data = Object.values(countCuadrillas);
            chartCuadrillasInstance.update();

            const tbody = document.querySelector('#iaoTable tbody');
            tbody.innerHTML = '';
            if (selectedLoc === "ALL") {{
                document.getElementById('detailsSection').style.display = "none";
            }} else {{
                document.getElementById('detailsSection').style.display = "block";
                if (fIao.length === 0) tbody.innerHTML = '<tr><td colspan="6">No hay datos.</td></tr>';
                else {{
                    fIao.forEach(i => {{
                        tbody.innerHTML += `<tr>
                            <td>${{i.ID_IAO}}</td>
                            <td><span style="background:var(--accent-1); padding:2px 6px; border-radius:6px;">${{i.Tipo_IAO}}</span></td>
                            <td>${{i.Cuadrilla_IAO}}</td><td>${{i.Metraje_Cable_Drop}}m</td>
                            <td><code>${{i.Serie_Eq_1_ONT}}</code></td><td>${{i.Ambiente_Instalacion}}</td>
                        </tr>`;
                    }});
                }}
            }}
        }}

        window.onload = function() {{ initCharts(); updateDashboard(); }};
    </script>
</body>
</html>
"""

    with open(os.path.join(output_dir, "dashboard.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Dashboard HTML ajustado (Gráficos más pequeños y claros) generado.")

if __name__ == "__main__":
    run()
