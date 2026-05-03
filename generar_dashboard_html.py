import csv
import os
import json

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
    
    # Cuadrillas únicas de todas las fases
    cuad_set = set()
    for r in pext_data: cuad_set.add(r.get("CUADRILLA",""))
    for r in iao_data: cuad_set.add(r.get("CUADRILLA",""))
    cuadrillas = sorted(list([c for c in cuad_set if c.strip()]))

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FTTH Pronatel - Dashboard Analítico Global</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-color: #0f172a; --card-bg: rgba(30, 41, 59, 0.7); --card-border: rgba(255, 255, 255, 0.1);
            --text-primary: #f8fafc; --text-secondary: #94a3b8;
            --accent-1: #3b82f6; --accent-2: #10b981; --accent-3: #8b5cf6; --accent-warning: #f59e0b; --accent-danger: #ef4444;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }}
        body {{ background-color: var(--bg-color); color: var(--text-primary); min-height: 100vh; padding: 1.5rem; 
               background-image: radial-gradient(at 0% 0%, rgba(59,130,246,0.1) 0, transparent 50%), radial-gradient(at 100% 100%, rgba(139,92,246,0.1) 0, transparent 50%); background-attachment: fixed; }}
        
        .header {{ margin-bottom: 1.5rem; text-align: center; }}
        .header h1 {{ font-size: 2rem; font-weight: 800; background: linear-gradient(to right, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 1rem; }}
        
        .filters-panel {{ background: rgba(15, 23, 42, 0.6); border: 1px solid var(--card-border); border-radius: 1rem; padding: 1.5rem; max-width: 1400px; margin: 0 auto 1.5rem auto; display: flex; flex-wrap: wrap; gap: 1rem; justify-content: center; }}
        .filter-group {{ display: flex; flex-direction: column; gap: 0.4rem; }}
        .filter-group label {{ font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; }}
        select {{ background-color: rgba(30, 41, 59, 0.9); color: var(--text-primary); border: 1px solid var(--accent-1); padding: 0.5rem 0.8rem; border-radius: 0.5rem; font-size: 0.85rem; outline: none; cursor: pointer; min-width: 160px; }}
        select:focus {{ border-color: #60a5fa; box-shadow: 0 0 10px rgba(59,130,246,0.3); }}
        
        .subfilter-panel {{ background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 0.8rem 1rem; border-radius: 0.8rem; display: flex; align-items: center; gap: 1rem; width: 100%; justify-content: center; margin-top: 0.5rem; }}
        .subfilter-panel label {{ color: var(--accent-warning); }}
        .subfilter-panel select {{ border-color: var(--accent-warning); }}

        .dashboard-grid {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 1.2rem; max-width: 1400px; margin: 0 auto; }}
        .card {{ background: var(--card-bg); backdrop-filter: blur(12px); border: 1px solid var(--card-border); border-radius: 1rem; padding: 1.2rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
        .kpi-card {{ grid-column: span 4; text-align: center; }}
        @media (max-width: 1024px) {{ .kpi-card, .chart-container {{ grid-column: span 12 !important; }} }}
        
        .kpi-value {{ font-size: 2.2rem; font-weight: 800; margin: 0.3rem 0; color: var(--text-primary); }}
        .kpi-label {{ color: var(--text-secondary); font-size: 0.8rem; text-transform: uppercase; font-weight: 600; }}
        .kpi-1 .kpi-value {{ color: var(--accent-1); }} .kpi-2 .kpi-value {{ color: var(--accent-2); }} .kpi-3 .kpi-value {{ color: var(--accent-3); }}

        .chart-container {{ grid-column: span 4; min-height: 250px; display: flex; flex-direction: column; }}
        .chart-wrapper {{ position: relative; flex-grow: 1; height: 100%; min-height: 200px; }}
        .chart-title {{ font-size: 0.95rem; font-weight: 600; margin-bottom: 0.8rem; color: var(--text-primary); text-align: center; border-bottom: 1px solid var(--card-border); padding-bottom: 0.4rem; }}

        .table-container {{ grid-column: span 12; overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; }}
        th, td {{ padding: 0.8rem; border-bottom: 1px solid var(--card-border); }}
        th {{ color: var(--accent-1); font-weight: 600; font-size: 0.8rem; text-transform: uppercase; }}
        td {{ color: var(--text-primary); font-size: 0.85rem; }}
        tr:hover td {{ background-color: rgba(255,255,255,0.05); }}
        .highlight-col {{ background-color: rgba(16, 185, 129, 0.1); font-weight: 600; }}
        .tag {{ padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; color: white; }}
        .tag-success {{ background-color: var(--accent-2); }}
        .tag-danger {{ background-color: var(--accent-danger); }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Dashboard Integral FTTH - Gilat/Pronatel</h1>
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
        
        <div class="subfilter-panel">
            <label>🔍 Análisis Especial:</label>
            <select id="f_pext" onchange="updateDashboard()">
                <option value="ALL">Vista Predeterminada</option>
                <option value="SPL_1X2">Localidades con Splitter 1x2</option>
                <option value="SPL_1X4">Localidades con Splitter 1x4</option>
                <option value="SPL_1X8">Localidades con Splitter 1x8</option>
                <option value="POSTES_NUEVOS">Localidades con Postes Nuevos (Izados vs Req)</option>
            </select>
        </div>
    </div>

    <div class="dashboard-grid">
        <!-- KPIs -->
        <div class="card kpi-card kpi-1"><div class="kpi-label">FO Desplegada</div><div class="kpi-value" id="valFO">0 <span style="font-size:1rem">m</span></div></div>
        <div class="card kpi-card kpi-2"><div class="kpi-label">IAOs Instaladas</div><div class="kpi-value" id="valIAO">0</div></div>
        <div class="card kpi-card kpi-3"><div class="kpi-label">Progreso Global PEXT</div><div class="kpi-value" id="valGlobalProg">0 <span style="font-size:1rem">%</span></div></div>

        <!-- Fila de Gráficas 1 -->
        <div class="card chart-container"><h2 class="chart-title">📊 Avance Físico del Proyecto (%)</h2><div class="chart-wrapper"><canvas id="cAvances"></canvas></div></div>
        <div class="card chart-container"><h2 class="chart-title">🏗️ Izado de Postes Nuevos</h2><div class="chart-wrapper"><canvas id="cPostesComp"></canvas></div></div>
        <div class="card chart-container"><h2 class="chart-title">📡 Instalación de Equipos NODO</h2><div class="chart-wrapper"><canvas id="cNodo"></canvas></div></div>

        <!-- Fila de Gráficas 2 -->
        <div class="card chart-container"><h2 class="chart-title">🏛️ Tipos de IAO</h2><div class="chart-wrapper"><canvas id="cTipos"></canvas></div></div>
        <div class="card chart-container"><h2 class="chart-title">⚙️ Infraestructura PEXT</h2><div class="chart-wrapper"><canvas id="cPostes"></canvas></div></div>
        <div class="card chart-container"><h2 class="chart-title">👷 Rendimiento por Cuadrilla (IAOs)</h2><div class="chart-wrapper"><canvas id="cCuadrillas"></canvas></div></div>
        
        <!-- Progressive Disclosure Table -->
        <div class="card table-container">
            <h2 class="chart-title" id="tableTitle" style="text-align: left; font-size:1.1rem;">📋 Detalle de Datos</h2>
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
        
        // Poblar selects
        const locs = {json.dumps(localidades)};
        const nodos = {json.dumps(nodos)};
        const cuadrillas = {json.dumps(cuadrillas)};
        
        const selLoc = document.getElementById('f_localidad'); locs.forEach(l => selLoc.add(new Option(l, l)));
        const selNodo = document.getElementById('f_nodo'); nodos.forEach(n => selNodo.add(new Option(n, n)));
        const selCuad = document.getElementById('f_cuadrilla'); cuadrillas.forEach(c => selCuad.add(new Option(c, c)));

        Chart.defaults.color = '#94a3b8'; Chart.defaults.font.family = "'Inter', sans-serif";
        let cAvances, cPostesComp, cNodo, cTipos, cPostes, cCuadrillas;

        function initCharts() {{
            cAvances = new Chart(document.getElementById('cAvances'), {{ type: 'bar', data: {{ labels: ["NODO", "PEXT", "IAO"], datasets: [{{ data: [], backgroundColor: ['#3b82f6', '#10b981', '#8b5cf6'], borderRadius: 4 }}] }}, options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ max: 100, grid: {{ color: 'rgba(255,255,255,0.05)' }} }}, y: {{ grid: {{ display: false }} }} }} }} }});
            cPostesComp = new Chart(document.getElementById('cPostesComp'), {{ type: 'bar', data: {{ labels: ["Requeridos", "Izados"], datasets: [{{ data: [], backgroundColor: ['#ef4444', '#10b981'], borderRadius: 4 }}] }}, options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ ticks: {{ precision: 0 }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }}, x: {{ grid: {{ display: false }} }} }} }} }});
            cNodo = new Chart(document.getElementById('cNodo'), {{ type: 'doughnut', data: {{ labels: ["Instalados", "Faltantes"], datasets: [{{ data: [], backgroundColor: ['#3b82f6', '#334155'], borderWidth: 0 }}] }}, options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'bottom', labels: {{ padding: 10, boxWidth: 10, color: '#f8fafc' }} }} }} }} }});
            cTipos = new Chart(document.getElementById('cTipos'), {{ type: 'bar', data: {{ labels: [], datasets: [{{ data: [], backgroundColor: '#f59e0b', borderRadius: 4 }}] }}, options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ ticks: {{ precision: 0 }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }}, y: {{ grid: {{ display: false }} }} }} }} }});
            cPostes = new Chart(document.getElementById('cPostes'), {{ type: 'pie', data: {{ labels: ["Nuevos", "Eléctricos", "Terceros"], datasets: [{{ data: [], backgroundColor: ['#10b981', '#3b82f6', '#f59e0b'], borderWidth: 0 }}] }}, options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'bottom', labels: {{ padding: 10, boxWidth: 10, color: '#f8fafc' }} }} }} }} }});
            cCuadrillas = new Chart(document.getElementById('cCuadrillas'), {{ type: 'bar', data: {{ labels: [], datasets: [{{ data: [], backgroundColor: '#8b5cf6', borderRadius: 4 }}] }}, options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ ticks: {{ precision: 0 }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }}, x: {{ grid: {{ display: false }} }} }} }} }});
        }}

        function updateDashboard() {{
            const vLoc = selLoc.value; const vNodo = selNodo.value; const vCuad = selCuad.value;
            const vOdf = document.getElementById('f_odf').value;
            const vRepo = document.getElementById('f_repo').value;
            const vPext = document.getElementById('f_pext').value;

            // Filtros de NODO (Base principal para la localidad si aplica)
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

            if (vPext === "SPL_1X2") fPext = fPext.filter(d => parseInt(d.Splitter_1x2_Cant) > 0);
            if (vPext === "SPL_1X4") fPext = fPext.filter(d => parseInt(d.Splitter_1x4_Cant) > 0);
            if (vPext === "SPL_1X8") fPext = fPext.filter(d => parseInt(d.Splitter_1x8_Cant) > 0);
            if (vPext === "POSTES_NUEVOS") fPext = fPext.filter(d => parseInt(d.Cant_Postes_Nuevos) > 0);

            // Filtrar IAO
            let fIao = rawIao.filter(d => {{
                return validLocs.includes(d.LOCALIDAD) &&
                       (vCuad === "ALL" || d.CUADRILLA === vCuad) &&
                       (vRepo === "ALL" || d.Reporte_Fotografico === vRepo);
            }});

            // Cálculos KPIs
            let totalFO = 0; let postesReq = 0, postesIza = 0, postesE = 0, postesT = 0;
            fPext.forEach(p => {{
                let valFO = parseFloat(p.Metraje_Promedio_FO.replace('.', '').replace(',', '.'));
                if(!isNaN(valFO)) totalFO += valFO;
                postesReq += parseInt(p.Cant_Postes_Nuevos) || 0;
                postesIza += parseInt(p.Izados_Postes_Nuevos) || 0;
                postesE += parseInt(p.Cant_Postes_Electricos_BT || 0) + parseInt(p.Cant_Postes_Electricos_MT || 0);
                postesT += parseInt(p.Cant_Postes_Terceros || 0);
            }});

            document.getElementById('valFO').innerHTML = totalFO.toLocaleString('en-US') + ' <span style="font-size:1rem">m</span>';
            document.getElementById('valIAO').innerText = fIao.length;
            
            // Calculo de Avances (%)
            // 1. NODO: 4 equipos por fila (OLT, ODF, SW, ITM)
            let totalEquiposEsperados = fNodo.length * 4;
            let equiposInstalados = 0;
            fNodo.forEach(n => {{
                if(n.Serie_OLT && n.Serie_OLT.trim() !== '') equiposInstalados++;
                if(n.Serie_ODF && n.Serie_ODF.trim() !== '') equiposInstalados++;
                if(n.Serie_SW && n.Serie_SW.trim() !== '') equiposInstalados++;
                if(n.ITM === 'Sí' || n.Empalme_ODF_OK === 'Sí') equiposInstalados++;
            }});
            let pctNodo = totalEquiposEsperados > 0 ? Math.round((equiposInstalados / totalEquiposEsperados) * 100) : 0;

            // 2. PEXT: Izados vs Requeridos
            let pctPext = postesReq > 0 ? Math.round((postesIza / postesReq) * 100) : (fPext.length > 0 ? 100 : 0);

            // 3. IAO: Usamos el Reporte Fotografico como done
            let iaoTotales = rawIao.filter(d => validLocs.includes(d.LOCALIDAD)).length;
            let iaoDone = rawIao.filter(d => validLocs.includes(d.LOCALIDAD) && d.Reporte_Fotografico === "Sí").length;
            let pctIao = iaoTotales > 0 ? Math.round((iaoDone / iaoTotales) * 100) : 0;

            document.getElementById('valGlobalProg').innerHTML = pctPext + ' <span style="font-size:1rem">%</span>';

            // Actualizar Gráficas
            cAvances.data.datasets[0].data = [pctNodo, pctPext, pctIao]; cAvances.update();
            cPostesComp.data.datasets[0].data = [postesReq, postesIza]; cPostesComp.update();
            cNodo.data.datasets[0].data = [equiposInstalados, totalEquiposEsperados - equiposInstalados]; cNodo.update();
            cPostes.data.datasets[0].data = [postesReq, postesE, postesT]; cPostes.update();

            let countTipos = {{}}; let countCuadrillas = {{}};
            fIao.forEach(i => {{
                // FIX: Parsear Tipo_IAO del CODIGO_IAO
                let tipo = i.CODIGO_IAO.split('-').pop();
                if(!tipo || tipo === "undefined") tipo = "Desc.";
                countTipos[tipo] = (countTipos[tipo] || 0) + 1;
                countCuadrillas[i.CUADRILLA] = (countCuadrillas[i.CUADRILLA] || 0) + 1;
            }});

            cTipos.data.labels = Object.keys(countTipos); cTipos.data.datasets[0].data = Object.values(countTipos); cTipos.update();
            cCuadrillas.data.labels = Object.keys(countCuadrillas); cCuadrillas.data.datasets[0].data = Object.values(countCuadrillas); cCuadrillas.update();

            // Render Tabla
            const thead = document.getElementById('tableHead');
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';

            if (vCuad !== "ALL" && vPext === "ALL") {{
                document.getElementById('tableTitle').innerText = `📋 Localidades Abarcadas por ${{vCuad}}`;
                thead.innerHTML = `<tr><th>Código Nodo</th><th>Localidad</th><th>Rol de la Cuadrilla</th><th>FO Desplegada</th><th>IAOs Instaladas</th></tr>`;
                
                // Agrupar por localidad para la cuadrilla
                let res = {{}};
                fPext.forEach(p => {{
                    if(!res[p.LOCALIDAD]) res[p.LOCALIDAD] = {{nodo: p.CÓDIGO_NODO, fo:0, iaos:0, rol: "PEXT"}};
                    res[p.LOCALIDAD].fo += parseFloat(p.Metraje_Promedio_FO.replace('.', '').replace(',', '.')) || 0;
                }});
                fIao.forEach(i => {{
                    if(!res[i.LOCALIDAD]) res[i.LOCALIDAD] = {{nodo: i.CÓDIGO_NODO, fo:0, iaos:0, rol: "IAO"}};
                    else res[i.LOCALIDAD].rol = "PEXT e IAO";
                    res[i.LOCALIDAD].iaos += 1;
                }});

                Object.keys(res).forEach(loc => {{
                    let d = res[loc];
                    tbody.innerHTML += `<tr><td>${{d.nodo}}</td><td>${{loc}}</td><td><span class="tag tag-success">${{d.rol}}</span></td><td>${{d.fo}} m</td><td>${{d.iaos}}</td></tr>`;
                }});
                if(Object.keys(res).length === 0) tbody.innerHTML = '<tr><td colspan="5">La cuadrilla no tiene registros en la selección actual.</td></tr>';

            }} else if (vPext === "ALL") {{
                document.getElementById('tableTitle').innerText = "📋 Detalle de Nodos e IAOs";
                thead.innerHTML = `<tr><th>Localidad</th><th>IAO</th><th>Tipo</th><th>Serie ONT</th><th>Aterramiento</th><th>Reporte IAO</th><th>Empalme Nodo OK</th></tr>`;
                if(fIao.length === 0) tbody.innerHTML = '<tr><td colspan="7">No hay datos que coincidan.</td></tr>';
                fIao.forEach(i => {{
                    let tipo = i.CODIGO_IAO.split('-').pop();
                    let nodoRel = fNodo.find(n => n.LOCALIDAD === i.LOCALIDAD) || {{}};
                    let nodoOK = nodoRel.Empalme_ODF_OK === 'Sí' ? '<span class="tag tag-success">Sí</span>' : '<span class="tag tag-danger">No</span>';
                    tbody.innerHTML += `<tr><td>${{i.LOCALIDAD}}</td><td>${{i.CODIGO_IAO}}</td><td><span style="background:var(--accent-1);" class="tag">${{tipo}}</span></td><td><code>${{i.Serie_Eq_1_ONT}}</code></td><td>${{i.Aterramiento_OK}}</td><td>${{i.Reporte_Fotografico}}</td><td>${{nodoOK}}</td></tr>`;
                }});
            }} else if (vPext.startsWith("SPL_")) {{
                const tName = vPext.replace("SPL_", "Splitter ");
                document.getElementById('tableTitle').innerText = `📋 Localidades con ${{tName}}`;
                thead.innerHTML = `<tr><th>Código Nodo</th><th>Localidad</th><th>Cuadrilla PEXT</th><th>Spl 1x2</th><th>Spl 1x4</th><th>Spl 1x8</th></tr>`;
                if(fPext.length === 0) tbody.innerHTML = '<tr><td colspan="6">No hay localidades.</td></tr>';
                fPext.forEach(p => {{
                    let c1x2 = p.Splitter_1x2_Cant || "0"; let c1x4 = p.Splitter_1x4_Cant || "0"; let c1x8 = p.Splitter_1x8_Cant || "0";
                    let hl1 = vPext==="SPL_1X2" ? "highlight-col" : ""; let hl4 = vPext==="SPL_1X4" ? "highlight-col" : ""; let hl8 = vPext==="SPL_1X8" ? "highlight-col" : "";
                    tbody.innerHTML += `<tr><td>${{p.CÓDIGO_NODO}}</td><td>${{p.LOCALIDAD}}</td><td>${{p.CUADRILLA}}</td><td class="${{hl1}}">${{c1x2}}</td><td class="${{hl4}}">${{c1x4}}</td><td class="${{hl8}}">${{c1x8}}</td></tr>`;
                }});
            }} else if (vPext === "POSTES_NUEVOS") {{
                document.getElementById('tableTitle').innerText = `📋 Avance de Postes Nuevos por Localidad`;
                thead.innerHTML = `<tr><th>Código Nodo</th><th>Localidad</th><th>Postes Nuevos Requeridos</th><th>Postes Izados</th><th>Avance %</th></tr>`;
                if(fPext.length === 0) tbody.innerHTML = '<tr><td colspan="5">No hay localidades con postes nuevos.</td></tr>';
                fPext.forEach(p => {{
                    let req = parseInt(p.Cant_Postes_Nuevos) || 0; let iza = parseInt(p.Izados_Postes_Nuevos) || 0;
                    let pct = req > 0 ? Math.round((iza / req) * 100) : 0;
                    let clr = pct === 100 ? "color: var(--accent-2)" : (pct < 50 ? "color: var(--accent-danger)" : "color: var(--accent-warning)");
                    tbody.innerHTML += `<tr><td>${{p.CÓDIGO_NODO}}</td><td>${{p.LOCALIDAD}}</td><td class="highlight-col">${{req}}</td><td class="highlight-col">${{iza}}</td><td><strong style="${{clr}}">${{pct}}%</strong></td></tr>`;
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
    print("Dashboard HTML con KPIs Avanzados generado exitosamente.")

if __name__ == "__main__":
    run()
