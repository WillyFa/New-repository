import csv
import os
import json
import base64

output_dir = r"C:\Users\ASUS\.gemini\antigravity\scratch"

def clean_data(data_list, key_field="CÓDIGO_NODO"):
    return [r for r in data_list if r.get(key_field, "").strip() != ""]

def run():
    pext_raw = []
    with open(os.path.join(output_dir, "Prueba_BD_PEXT.csv"), "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader: pext_raw.append(row)

    iao_raw = []
    with open(os.path.join(output_dir, "Prueba_BD_IAO.csv"), "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader: iao_raw.append(row)
        
    nodo_raw = []
    with open(os.path.join(output_dir, "Prueba_BD_NODO.csv"), "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader: nodo_raw.append(row)

    pext_data = clean_data(pext_raw)
    iao_data = clean_data(iao_raw)
    nodo_data = clean_data(nodo_raw)

    localidades = sorted(list(set([r["LOCALIDAD"] for r in pext_data if "LOCALIDAD" in r])))
    nodos = sorted(list(set([r["CÓDIGO_NODO"] for r in pext_data if "CÓDIGO_NODO" in r])))
    
    cuad_set = set()
    for r in pext_data: cuad_set.add(r.get("CUADRILLA",""))
    for r in iao_data: cuad_set.add(r.get("CUADRILLA",""))
    cuadrillas = sorted(list([c for c in cuad_set if c.strip()]))

    # Leer logo y convertir a base64
    logo_b64 = ""
    logo_path = os.path.join(output_dir, "Logo covepa.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as img_file:
            logo_b64 = base64.b64encode(img_file.read()).decode("utf-8")

    html_content = f"""<!DOCTYPE html>
<html lang="es" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Control Proyecto FTTH ICA - COVEPA</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>
    <style>
        :root {{
            --bg-color: #0f172a; --card-bg: rgba(30, 41, 59, 0.7); --card-border: rgba(255, 255, 255, 0.1);
            --text-primary: #f8fafc; --text-secondary: #94a3b8;
            --accent-1: #3b82f6; --accent-2: #10b981; --accent-3: #8b5cf6; --accent-warning: #f59e0b; --accent-danger: #ef4444;
            --input-bg: rgba(30, 41, 59, 0.9); --grid-color: rgba(255,255,255,0.05);
        }}
        [data-theme="light"] {{
            --bg-color: #f1f5f9; --card-bg: rgba(255, 255, 255, 0.9); --card-border: rgba(0, 0, 0, 0.1);
            --text-primary: #0f172a; --text-secondary: #475569;
            --input-bg: rgba(255, 255, 255, 0.9); --grid-color: rgba(0,0,0,0.05);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; transition: background-color 0.3s, color 0.3s; }}
        body {{ background-color: var(--bg-color); color: var(--text-primary); min-height: 100vh; padding: 1.5rem; 
               background-image: radial-gradient(at 0% 0%, rgba(59,130,246,0.1) 0, transparent 50%), radial-gradient(at 100% 100%, rgba(139,92,246,0.1) 0, transparent 50%); background-attachment: fixed; }}
        
        .header {{ margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between; max-width: 1400px; margin-left: auto; margin-right: auto; padding: 0.5rem 0; }}
        .header-left {{ display: flex; align-items: center; gap: 1rem; }}
        .header-logo {{ height: 48px; width: auto; object-fit: contain; }}
        [data-theme="dark"] .header-logo {{ filter: brightness(0) invert(1); }}
        .header-title {{ }}
        .header-title h1 {{ font-size: 1.6rem; font-weight: 800; background: linear-gradient(135deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.2; }}
        .header-title .subtitle {{ font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 2px; font-weight: 600; }}
        
        #theme-btn {{ padding: 0.5rem 1rem; border-radius: 2rem; border: 1px solid var(--card-border); background: var(--card-bg); color: var(--text-primary); cursor: pointer; font-weight: 600; font-size: 0.85rem; display: flex; align-items: center; gap: 0.5rem; white-space: nowrap; }}
        #theme-btn:hover {{ border-color: var(--accent-1); box-shadow: 0 0 12px rgba(59,130,246,0.2); }}

        .filters-panel {{ background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 1rem; padding: 1.5rem; max-width: 1400px; margin: 0 auto 1.5rem auto; display: flex; flex-wrap: wrap; gap: 1rem; justify-content: center; }}
        .filter-group {{ display: flex; flex-direction: column; gap: 0.4rem; }}
        .filter-group label {{ font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; }}
        select {{ background-color: var(--input-bg); color: var(--text-primary); border: 1px solid var(--accent-1); padding: 0.5rem 0.8rem; border-radius: 0.5rem; font-size: 0.85rem; outline: none; cursor: pointer; min-width: 160px; }}
        
        .dashboard-grid {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 1.2rem; max-width: 1400px; margin: 0 auto; }}
        .card {{ background: var(--card-bg); backdrop-filter: blur(12px); border: 1px solid var(--card-border); border-radius: 1rem; padding: 1.2rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
        .kpi-card {{ grid-column: span 4; text-align: center; }}
        @media (max-width: 1024px) {{ .kpi-card, .chart-container {{ grid-column: span 12 !important; }} }}
        
        .kpi-value {{ font-size: 2.2rem; font-weight: 800; margin: 0.3rem 0; color: var(--text-primary); }}
        .kpi-label {{ color: var(--text-secondary); font-size: 0.8rem; text-transform: uppercase; font-weight: 600; }}
        .kpi-1 .kpi-value {{ color: var(--accent-1); }} .kpi-2 .kpi-value {{ color: var(--accent-2); }} .kpi-3 .kpi-value {{ color: var(--accent-3); }}

        .chart-container {{ grid-column: span 4; min-height: 250px; display: flex; flex-direction: column; }}
        .chart-wrapper {{ position: relative; flex-grow: 1; height: 100%; min-height: 200px; }}
        .chart-title {{ font-size: 0.95rem; font-weight: 600; margin-bottom: 0.8rem; color: var(--text-primary); text-align: center; border-bottom: 1px solid var(--card-border); padding-bottom: 0.4rem; text-transform: uppercase; }}

        .table-container {{ grid-column: span 12; overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; }}
        th, td {{ padding: 0.8rem; border-bottom: 1px solid var(--card-border); }}
        th {{ color: var(--accent-1); font-weight: 600; font-size: 0.8rem; text-transform: uppercase; }}
        td {{ color: var(--text-primary); font-size: 0.85rem; }}
        .highlight-col {{ background-color: rgba(16, 185, 129, 0.1); font-weight: 600; }}
        .tag {{ padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; color: white; }}
        .tag-success {{ background-color: var(--accent-2); }}
        .tag-danger {{ background-color: var(--accent-danger); }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-left">
            <img src="data:image/png;base64,{logo_b64}" alt="COVEPA" class="header-logo" />
            <div class="header-title">
                <h1>CONTROL PROYECTO FTTH ICA</h1>
                <span class="subtitle">COVEPA — Panel de Gestión Directiva</span>
            </div>
        </div>
        <button id="theme-btn" onclick="toggleTheme()">☀️ Modo Día</button>
    </div>

    <!-- Panel de Filtros -->
    <div class="filters-panel">
        <div class="filter-group">
            <label>📍 Localidad</label>
            <select id="f_localidad" onchange="updateDashboard()"><option value="ALL">Todas</option></select>
        </div>
        <div class="filter-group">
            <label>🏷️ Código Nodo</label>
            <select id="f_nodo" onchange="updateDashboard()"><option value="ALL">Todos</option></select>
        </div>
        <div class="filter-group">
            <label>👷 Cuadrilla</label>
            <select id="f_cuadrilla" onchange="updateDashboard()"><option value="ALL">Todas las Cuadrillas</option></select>
        </div>
        <div class="filter-group">
            <label>🔌 Tipo Splitter PEXT</label>
            <select id="f_spl" onchange="updateDashboard()" style="border-color: var(--accent-warning);">
                <option value="ALL">Cualquiera</option>
                <option value="SPL_1X2">Localidades con Spl 1x2</option>
                <option value="SPL_1X4">Localidades con Spl 1x4</option>
                <option value="SPL_1X8">Localidades con Spl 1x8</option>
            </select>
        </div>
        <div class="filter-group">
            <label>⚡ Empalme ODF OK (ITM)</label>
            <select id="f_odf" onchange="updateDashboard()">
                <option value="ALL">Cualquiera</option>
                <option value="Sí">Completado (Sí)</option>
                <option value="No">Faltante</option>
            </select>
        </div>
        <div class="filter-group">
            <label>📸 Reporte Fotográfico</label>
            <select id="f_repo" onchange="updateDashboard()">
                <option value="ALL">Cualquiera</option>
                <option value="Sí">Realizado (Sí)</option>
            </select>
        </div>
    </div>

    <div class="dashboard-grid">
        <!-- KPIs -->
        <div class="card kpi-card kpi-1"><div class="kpi-label">FO Desplegada</div><div class="kpi-value" id="valFO">0 <span style="font-size:1rem">m</span></div></div>
        <div class="card kpi-card kpi-2"><div class="kpi-label">IAOs Abarcadas (Completadas)</div><div class="kpi-value" id="valIAO">0</div></div>
        <div class="card kpi-card kpi-3"><div class="kpi-label">Progreso Global PEXT</div><div class="kpi-value" id="valGlobalProg">0 <span style="font-size:1rem">%</span></div></div>

        <!-- Fila de Gráficas 1 -->
        <div class="card chart-container"><h2 class="chart-title">📊 Avance Físico del Proyecto (%)</h2><div class="chart-wrapper"><canvas id="cAvances"></canvas></div></div>
        <div class="card chart-container"><h2 class="chart-title">🏗️ Izado de Postes Nuevos</h2><div class="chart-wrapper"><canvas id="cPostesComp"></canvas></div></div>
        <div class="card chart-container"><h2 class="chart-title">📡 Instalación de Equipos NODO</h2><div class="chart-wrapper"><canvas id="cNodo"></canvas></div></div>

        <!-- Fila de Gráficas 2 -->
        <div class="card chart-container"><h2 class="chart-title">⚙️ Equipos Instalados PEXT</h2><div class="chart-wrapper"><canvas id="cEquiposPext"></canvas></div></div>
        <div class="card chart-container"><h2 class="chart-title">🏛️ Tipos de IAO</h2><div class="chart-wrapper"><canvas id="cTipos"></canvas></div></div>
        <div class="card chart-container"><h2 class="chart-title">👷 IAOS ABARCADAS (Por Cuadrilla)</h2><div class="chart-wrapper"><canvas id="cCuadrillas"></canvas></div></div>
        
        <!-- Progressive Disclosure Table -->
        <div class="card table-container">
            <h2 class="chart-title" id="tableTitle" style="text-align: left; font-size:1.1rem; text-transform:none;">📋 Detalle de Datos (Vista Dinámica)</h2>
            <table id="dataTable">
                <thead id="tableHead"></thead>
                <tbody id="tableBody"></tbody>
            </table>
        </div>
    </div>

    <script>
        const rawPext = {json.dumps(pext_data)};
        const rawIao = {json.dumps(iao_data)};
        const rawNodo = {json.dumps(nodo_data)};
        
        const selLoc = document.getElementById('f_localidad'); {json.dumps(localidades)}.forEach(l => selLoc.add(new Option(l, l)));
        const selNodo = document.getElementById('f_nodo'); {json.dumps(nodos)}.forEach(n => selNodo.add(new Option(n, n)));
        const selCuad = document.getElementById('f_cuadrilla'); {json.dumps(cuadrillas)}.forEach(c => selCuad.add(new Option(c, c)));

        Chart.defaults.color = '#94a3b8'; Chart.defaults.font.family = "'Inter', sans-serif";
        Chart.register(ChartDataLabels);
        const dlOpts = {{ display: true, color: '#f8fafc', font: {{ weight: 'bold', size: 12 }}, anchor: 'center', align: 'center' }};
        const dlOptsNone = {{ display: false }};
        let cAvances, cPostesComp, cNodo, cTipos, cEquiposPext, cCuadrillas;
        let isDarkTheme = true;

        function getGridColor() {{ return isDarkTheme ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'; }}
        function getDlColor() {{ return isDarkTheme ? '#f8fafc' : '#0f172a'; }}

        function initCharts() {{
            cAvances = new Chart(document.getElementById('cAvances'), {{ type: 'bar', data: {{ labels: ["NODO", "PEXT", "IAO"], datasets: [{{ data: [], backgroundColor: ['#3b82f6', '#10b981', '#8b5cf6'], borderRadius: 4 }}] }}, options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }}, datalabels: {{ ...dlOpts, formatter: v => v + '%' }} }}, scales: {{ x: {{ max: 100, grid: {{ color: getGridColor() }} }}, y: {{ grid: {{ display: false }} }} }} }} }});
            cPostesComp = new Chart(document.getElementById('cPostesComp'), {{ type: 'bar', data: {{ labels: ["Requeridos", "Izados"], datasets: [{{ data: [], backgroundColor: ['#ef4444', '#10b981'], borderRadius: 4 }}] }}, options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }}, datalabels: dlOpts }}, scales: {{ y: {{ ticks: {{ precision: 0 }}, grid: {{ color: getGridColor() }} }}, x: {{ grid: {{ display: false }} }} }} }} }});
            cNodo = new Chart(document.getElementById('cNodo'), {{ type: 'bar', data: {{ labels: ["OLT", "ODF", "SW", "ITM"], datasets: [{{ label: 'Instalados', data: [], backgroundColor: '#22d3ee', borderRadius: 4 }}, {{ label: 'Faltantes', data: [], backgroundColor: '#f43f5e', borderRadius: 4 }}] }}, options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'bottom', labels: {{ padding: 10, boxWidth: 12 }} }}, datalabels: {{ ...dlOpts, display: (ctx) => ctx.dataset.data[ctx.dataIndex] > 0 }} }}, scales: {{ x: {{ stacked: true, grid: {{ display: false }} }}, y: {{ stacked: true, ticks: {{ precision: 0 }}, grid: {{ color: getGridColor() }} }} }} }} }});
            cEquiposPext = new Chart(document.getElementById('cEquiposPext'), {{ type: 'bar', data: {{ labels: ["CTOs", "Mufas ER", "Mufas Dist."], datasets: [{{ data: [], backgroundColor: ['#f59e0b', '#06b6d4', '#a855f7'], borderRadius: 4 }}] }}, options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }}, datalabels: dlOpts }}, scales: {{ y: {{ ticks: {{ precision: 0 }}, grid: {{ color: getGridColor() }} }}, x: {{ grid: {{ display: false }} }} }} }} }});
            cTipos = new Chart(document.getElementById('cTipos'), {{ type: 'bar', data: {{ labels: [], datasets: [{{ data: [], backgroundColor: '#fb923c', borderRadius: 4 }}] }}, options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }}, datalabels: dlOpts }}, scales: {{ x: {{ ticks: {{ precision: 0 }}, grid: {{ color: getGridColor() }} }}, y: {{ grid: {{ display: false }} }} }} }} }});
            cCuadrillas = new Chart(document.getElementById('cCuadrillas'), {{ type: 'bar', data: {{ labels: [], datasets: [{{ data: [], backgroundColor: '#a78bfa', borderRadius: 4 }}] }}, options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }}, datalabels: dlOpts }}, scales: {{ y: {{ ticks: {{ precision: 0 }}, grid: {{ color: getGridColor() }} }}, x: {{ grid: {{ display: false }} }} }} }} }});
        }}

        function toggleTheme() {{
            isDarkTheme = !isDarkTheme;
            document.documentElement.setAttribute('data-theme', isDarkTheme ? 'dark' : 'light');
            document.getElementById('theme-btn').innerText = isDarkTheme ? "☀️ Modo Día" : "🌙 Modo Noche";
            Chart.defaults.color = isDarkTheme ? '#94a3b8' : '#475569';
            const dlC = getDlColor();
            [cAvances, cPostesComp, cNodo, cEquiposPext, cTipos, cCuadrillas].forEach(c => {{
                if(c.options.scales) {{
                    if(c.options.scales.x && c.options.scales.x.grid) c.options.scales.x.grid.color = getGridColor();
                    if(c.options.scales.y && c.options.scales.y.grid) c.options.scales.y.grid.color = getGridColor();
                }}
                if(c.options.plugins.datalabels && c.options.plugins.datalabels.color !== undefined) c.options.plugins.datalabels.color = dlC;
                c.update();
            }});
        }}

        function updateDashboard() {{
            const vLoc = selLoc.value; const vNodo = selNodo.value; const vCuad = selCuad.value;
            const vOdf = document.getElementById('f_odf').value;
            const vRepo = document.getElementById('f_repo').value;
            const vSpl = document.getElementById('f_spl').value;

            // Filtros de NODO (Base principal)
            let fNodo = rawNodo.filter(d => {{
                return (vLoc === "ALL" || d.LOCALIDAD === vLoc) &&
                       (vNodo === "ALL" || d.CÓDIGO_NODO === vNodo) &&
                       (vOdf === "ALL" || d.Empalme_ODF_OK === vOdf) &&
                       (vRepo === "ALL" || d.Reporte_Fotografico === vRepo);
            }});

            const validLocs = fNodo.map(n => n.LOCALIDAD);

            // Filtrar PEXT
            let fPext = rawPext.filter(d => {{
                return validLocs.includes(d.LOCALIDAD) &&
                       (vCuad === "ALL" || d.CUADRILLA === vCuad);
            }});

            // Filtro SPLITTERS
            if (vSpl === "SPL_1X2") fPext = fPext.filter(d => parseInt(d.Splitter_1x2_Cant) > 0);
            if (vSpl === "SPL_1X4") fPext = fPext.filter(d => parseInt(d.Splitter_1x4_Cant) > 0);
            if (vSpl === "SPL_1X8") fPext = fPext.filter(d => parseInt(d.Splitter_1x8_Cant) > 0);

            const validPextLocs = fPext.map(p => p.LOCALIDAD);

            // Filtrar IAO (Solo mostrar IAOs de las localidades que sobrevivieron el filtro PEXT)
            let fIao = rawIao.filter(d => {{
                return validPextLocs.includes(d.LOCALIDAD) &&
                       (vCuad === "ALL" || d.CUADRILLA === vCuad) &&
                       (vRepo === "ALL" || d.Reporte_Fotografico === vRepo);
            }});

            // Cálculos PEXT
            let totalFO = 0; let postesReq = 0, postesIza = 0;
            let ctos = 0, mufasER = 0, mufasDist = 0;
            fPext.forEach(p => {{
                let valFO = parseFloat(p.Metraje_Promedio_FO.replace('.', '').replace(',', '.'));
                if(!isNaN(valFO)) totalFO += valFO;
                postesReq += parseInt(p.Cant_Postes_Nuevos) || 0;
                postesIza += parseInt(p.Izados_Postes_Nuevos) || 0;
                ctos += parseInt(p.Cant_CTOs) || 0;
                mufasER += parseInt(p.Cant_Mufas_ER) || 0;
                mufasDist += parseInt(p.Cant_Mufas_Dist) || 0;
            }});

            // LOGICA IAO ABARCADAS: Solo válidas si tienen fecha inicio y fin
            let iaosAbarcadasValidas = [];
            fIao.forEach(i => {{
                if (i.Fecha_Inicio && i.Fecha_Inicio.trim() !== '' && i.Fecha_Fin && i.Fecha_Fin.trim() !== '') {{
                    iaosAbarcadasValidas.push(i);
                }}
            }});

            document.getElementById('valFO').innerHTML = totalFO.toLocaleString('en-US') + ' <span style="font-size:1rem">m</span>';
            document.getElementById('valIAO').innerText = iaosAbarcadasValidas.length;
            
            // Calculo de Avances (%) - Detalle por equipo NODO usando columnas _Instalado
            let totalEquiposEsperados = fNodo.length * 4; let equiposInstalados = 0;
            let nOLT = 0, nODF = 0, nSW = 0, nITM = 0;
            fNodo.forEach(n => {{
                if(n.OLT_Instalado === 'Sí') {{ equiposInstalados++; nOLT++; }}
                if(n.ODF_Instalado === 'Sí') {{ equiposInstalados++; nODF++; }}
                if(n.SW_Instalado === 'Sí') {{ equiposInstalados++; nSW++; }}
                if(n.ITM_Instalado === 'Sí') {{ equiposInstalados++; nITM++; }}
            }});
            let pctNodo = totalEquiposEsperados > 0 ? Math.round((equiposInstalados / totalEquiposEsperados) * 100) : 0;
            let pctPext = postesReq > 0 ? Math.round((postesIza / postesReq) * 100) : (fPext.length > 0 ? 100 : 0);
            
            let iaoTotales = rawIao.filter(d => validLocs.includes(d.LOCALIDAD)).length;
            let iaoDone = rawIao.filter(d => validLocs.includes(d.LOCALIDAD) && d.Reporte_Fotografico === "Sí").length;
            let pctIao = iaoTotales > 0 ? Math.round((iaoDone / iaoTotales) * 100) : 0;

            document.getElementById('valGlobalProg').innerHTML = pctPext + ' <span style="font-size:1rem">%</span>';

            // Actualizar Gráficas
            cAvances.data.datasets[0].data = [pctNodo, pctPext, pctIao]; cAvances.update();
            cPostesComp.data.datasets[0].data = [postesReq, postesIza]; cPostesComp.update();
            cNodo.data.datasets[0].data = [nOLT, nODF, nSW, nITM]; cNodo.data.datasets[1].data = [fNodo.length - nOLT, fNodo.length - nODF, fNodo.length - nSW, fNodo.length - nITM]; cNodo.update();
            cEquiposPext.data.datasets[0].data = [ctos, mufasER, mufasDist]; cEquiposPext.update();

            let countTipos = {{}}; let countCuadrillas = {{}};
            // Usamos las iaos validas (con fechas) para el gráfico de cuadrillas
            iaosAbarcadasValidas.forEach(i => {{
                let tipo = i.CODIGO_IAO.split('-').pop() || "Desc.";
                countTipos[tipo] = (countTipos[tipo] || 0) + 1;
                countCuadrillas[i.CUADRILLA] = (countCuadrillas[i.CUADRILLA] || 0) + 1;
            }});

            cTipos.data.labels = Object.keys(countTipos); cTipos.data.datasets[0].data = Object.values(countTipos); cTipos.update();
            cCuadrillas.data.labels = Object.keys(countCuadrillas); cCuadrillas.data.datasets[0].data = Object.values(countCuadrillas); cCuadrillas.update();

            // Render Tabla
            const thead = document.getElementById('tableHead');
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';

            if (vSpl !== "ALL") {{
                const tName = vSpl.replace("SPL_", "Splitter ");
                document.getElementById('tableTitle').innerText = `📋 Localidades usando ${{tName}}`;
                thead.innerHTML = `<tr><th>Código Nodo</th><th>Localidad</th><th>Cuadrilla PEXT</th><th>Spl 1x2</th><th>Spl 1x4</th><th>Spl 1x8</th></tr>`;
                if(fPext.length === 0) tbody.innerHTML = '<tr><td colspan="6">Ninguna localidad utiliza este splitter bajo los filtros actuales.</td></tr>';
                fPext.forEach(p => {{
                    let c1x2 = p.Splitter_1x2_Cant || "0"; let c1x4 = p.Splitter_1x4_Cant || "0"; let c1x8 = p.Splitter_1x8_Cant || "0";
                    let hl1 = vSpl==="SPL_1X2" ? "highlight-col" : ""; let hl4 = vSpl==="SPL_1X4" ? "highlight-col" : ""; let hl8 = vSpl==="SPL_1X8" ? "highlight-col" : "";
                    tbody.innerHTML += `<tr><td>${{p.CÓDIGO_NODO}}</td><td>${{p.LOCALIDAD}}</td><td>${{p.CUADRILLA}}</td><td class="${{hl1}}">${{c1x2}}</td><td class="${{hl4}}">${{c1x4}}</td><td class="${{hl8}}">${{c1x8}}</td></tr>`;
                }});
            }} else {{
                document.getElementById('tableTitle').innerText = "📋 IAOS Abarcadas (Completadas)";
                thead.innerHTML = `<tr><th>Localidad</th><th>IAO</th><th>Tipo</th><th>Serie ONT</th><th>Aterramiento</th><th>Inicio</th><th>Fin</th></tr>`;
                if(iaosAbarcadasValidas.length === 0) tbody.innerHTML = '<tr><td colspan="7">No hay IAOs abarcadas completamente (con fecha inicio/fin) para esta selección.</td></tr>';
                iaosAbarcadasValidas.forEach(i => {{
                    let tipo = i.CODIGO_IAO.split('-').pop();
                    tbody.innerHTML += `<tr><td>${{i.LOCALIDAD}}</td><td>${{i.CODIGO_IAO}}</td><td><span style="background:var(--accent-1);" class="tag">${{tipo}}</span></td><td><code>${{i.Serie_Eq_1_ONT}}</code></td><td>${{i.Aterramiento_OK}}</td><td>${{i.Fecha_Inicio}}</td><td>${{i.Fecha_Fin}}</td></tr>`;
                }});
            }}
        }}

        window.onload = function() {{ initCharts(); updateDashboard(); }};
    </script>
</body>
</html>
"""

    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Dashboard HTML V3 Generado: Splitters, Tema Día/Noche, IAOs Abarcadas y CTOs.")

if __name__ == "__main__":
    run()
