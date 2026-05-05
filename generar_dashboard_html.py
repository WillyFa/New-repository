import os
import json
import base64
import pandas as pd
import numpy as np
import datetime

output_dir = r"C:\Users\ASUS\.gemini\antigravity\scratch"

def format_date(x):
    if pd.isna(x): return ""
    if isinstance(x, pd.Timestamp) or isinstance(x, datetime.datetime):
        return x.strftime("%Y-%m-%d")
    return str(x).strip()

def clean_df(df):
    df = df.replace({np.nan: "", "NaN": "", "nan": ""})
    for col in df.columns:
        if 'Fecha' in str(col):
            df[col] = df[col].apply(format_date)
    return df.to_dict(orient="records")

def run():
    print("Cargando archivos Excel...")
    try:
        df_nodo = pd.read_excel(os.path.join(output_dir, "Prueba_BD_NODO.xlsx"))
        df_pext = pd.read_excel(os.path.join(output_dir, "Prueba_BD_PEXT.xlsx"))
        
        xl_iao = pd.ExcelFile(os.path.join(output_dir, "Prueba_BD_IAO.xlsx"))
        df_iao = xl_iao.parse('Prueba_BD_IAO')
        df_hotspot = xl_iao.parse('HOTSPOT') if 'HOTSPOT' in xl_iao.sheet_names else pd.DataFrame()
        
    except Exception as e:
        print(f"Error loading excel files: {e}")
        return

    nodo_data = clean_df(df_nodo)
    pext_data = clean_df(df_pext)
    iao_data = clean_df(df_iao)
    hotspot_data = clean_df(df_hotspot)

    # Base64 Logo
    logo_b64 = ""
    logo_path = os.path.join(output_dir, "Logo_covepa.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as img_file:
            logo_b64 = base64.b64encode(img_file.read()).decode("utf-8")

    html_template = f"""<!DOCTYPE html>
<html lang="es" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FTTH Project Dashboard - COVEPA V5</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>
    <style>
        :root {{
            --bg-base: #0f172a;
            --bg-sidebar: #1e293b;
            --bg-card: rgba(30, 41, 59, 0.7);
            --border-color: rgba(255, 255, 255, 0.08);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #3b82f6;
            --secondary: #8b5cf6;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
        }}
        [data-theme="light"] {{
            --bg-base: #f1f5f9;
            --bg-sidebar: #ffffff;
            --bg-card: rgba(255, 255, 255, 0.9);
            --border-color: rgba(0, 0, 0, 0.08);
            --text-main: #0f172a;
            --text-muted: #475569;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }}
        body {{ background-color: var(--bg-base); color: var(--text-main); display: flex; height: 100vh; overflow: hidden; }}
        
        .sidebar {{ width: 260px; background-color: var(--bg-sidebar); border-right: 1px solid var(--border-color); display: flex; flex-direction: column; z-index: 10; }}
        .main-content {{ flex-grow: 1; overflow-y: auto; padding: 2rem; position: relative; scroll-behavior: smooth; }}
        .main-content::before {{ content: ""; position: absolute; top:0; left:0; width:100%; height:100%; z-index:-1;
            background-image: radial-gradient(at 0% 0%, rgba(59,130,246,0.1) 0, transparent 50%), radial-gradient(at 100% 100%, rgba(139,92,246,0.1) 0, transparent 50%);
            background-attachment: fixed; pointer-events: none; }}
        
        .brand {{ padding: 2rem 1.5rem; display: flex; align-items: center; gap: 1rem; border-bottom: 1px solid var(--border-color); }}
        .brand img {{ width: 40px; border-radius: 8px; background: white; padding: 4px; }}
        .brand-text {{ font-family: 'Outfit', sans-serif; font-size: 1.2rem; font-weight: 800; background: linear-gradient(135deg, var(--primary), var(--secondary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        
        .nav-menu {{ list-style: none; padding: 1.5rem 1rem; flex-grow: 1; display: flex; flex-direction: column; gap: 0.5rem; }}
        .nav-item {{ padding: 0.8rem 1rem; border-radius: 0.5rem; cursor: pointer; font-weight: 500; color: var(--text-muted); display: flex; align-items: center; gap: 0.8rem; transition: all 0.2s; }}
        .nav-item:hover {{ background: var(--border-color); color: var(--text-main); }}
        .nav-item.active {{ background: rgba(59, 130, 246, 0.1); color: var(--primary); font-weight: 600; border-left: 3px solid var(--primary); }}
        
        .section-view {{ display: none; animation: fadeIn 0.4s ease; }}
        .section-view.active {{ display: block; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        
        .filters-bar {{ background: var(--bg-card); backdrop-filter: blur(12px); border: 1px solid var(--border-color); border-radius: 1rem; padding: 1rem 1.5rem; display: flex; flex-wrap: wrap; gap: 1.2rem; margin-bottom: 2rem; }}
        .filter-group {{ display: flex; flex-direction: column; gap: 0.4rem; }}
        .filter-group label {{ font-size: 0.7rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }}
        .filter-group select {{ background-color: var(--bg-base); color: var(--text-main); border: 1px solid var(--border-color); padding: 0.4rem 0.6rem; border-radius: 0.4rem; font-size: 0.8rem; outline: none; cursor: pointer; min-width: 140px; }}
        
        .grid-dashboard {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 1.5rem; }}
        .card {{ background: var(--bg-card); backdrop-filter: blur(12px); border: 1px solid var(--border-color); border-radius: 1rem; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
        .chart-box {{ min-height: 300px; display: flex; flex-direction: column; }}
        .chart-header {{ font-family: 'Outfit', sans-serif; font-size: 1rem; font-weight: 600; margin-bottom: 1rem; color: var(--text-main); border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; text-transform: uppercase; }}
        .chart-wrap {{ position: relative; flex-grow: 1; min-height: 250px; }}
        
        .kpi-card {{ grid-column: span 3; text-align: center; }}
        .kpi-val {{ font-family: 'Outfit', sans-serif; font-size: 2rem; font-weight: 800; color: var(--text-main); }}
        .kpi-lbl {{ font-size: 0.7rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; }}

        .theme-toggle {{ padding: 1rem; border-top: 1px solid var(--border-color); }}
        .btn-theme {{ width: 100%; padding: 0.8rem; border-radius: 0.5rem; border: 1px solid var(--border-color); background: var(--bg-base); color: var(--text-main); cursor: pointer; font-weight: 600; }}
        
        @media (max-width: 1200px) {{ .grid-dashboard > * {{ grid-column: span 12 !important; }} }}
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="brand">
            <img src="data:image/png;base64,{logo_b64}" alt="COVEPA">
            <div class="brand-text">CONTROL<br>PROYECTO</div>
        </div>
        <ul class="nav-menu">
            <li class="nav-item active" onclick="switchTab('tab-nodo')">🌐 <span>NODO</span></li>
            <li class="nav-item" onclick="switchTab('tab-iao')">🏛️ <span>IAO's</span></li>
            <li class="nav-item" onclick="switchTab('tab-pext')">🔌 <span>PEXT</span></li>
            <li class="nav-item" onclick="switchTab('tab-hotspot')">📡 <span>HOTSPOT</span></li>
        </ul>
        <div class="theme-toggle"><button class="btn-theme" onclick="toggleTheme()">☀️ Modo Día</button></div>
    </div>

    <div class="main-content">
        <!-- SECCIÓN NODO -->
        <div id="tab-nodo" class="section-view active">
            <div class="filters-bar">
                <div class="filter-group"><label>Código Nodo</label><select id="n_nodo" onchange="updateNodo()"><option value="ALL">Todos</option></select></div>
                <div class="filter-group"><label>Tipo del Nodo</label><select id="n_tipo_nodo" onchange="updateNodo()"><option value="ALL">Todos</option></select></div>
                <div class="filter-group"><label>Tema Cultura</label><select id="n_cultura" onchange="updateNodo()"><option value="ALL">Todos</option></select></div>
                <div class="filter-group"><label>Cuadrilla</label><select id="n_cuad" onchange="updateNodo()"><option value="ALL">Todas</option></select></div>
                <div class="filter-group"><label>Altura Torre</label><select id="n_altura" onchange="updateNodo()"><option value="ALL">Todas</option></select></div>
                <div class="filter-group"><label>Fecha Inicio Ejec.</label><select id="n_fecha" onchange="updateNodo()"><option value="ALL">Todas</option></select></div>
            </div>
            <div class="grid-dashboard">
                <div class="card chart-box" style="grid-column: span 4;"><div class="chart-header">Progreso Global de Nodo</div><div class="chart-wrap"><canvas id="cNodoGlobal"></canvas></div></div>
                <div class="card chart-box" style="grid-column: span 4;"><div class="chart-header">TIPO DE NODO</div><div class="chart-wrap"><canvas id="cNodoTipos"></canvas></div></div>
                <div class="card chart-box" style="grid-column: span 4;"><div class="chart-header">Metraje de la Torre</div><div class="chart-wrap"><canvas id="cNodoAltura"></canvas></div></div>
                <div class="card chart-box" style="grid-column: span 6;"><div class="chart-header">INSTALACIÓN DE EQUIPOS</div><div class="chart-wrap"><canvas id="cNodoEquipos"></canvas></div></div>
                <div class="card chart-box" style="grid-column: span 6;"><div class="chart-header">Curva S - NODO</div><div class="chart-wrap"><canvas id="cNodoCurvaS"></canvas></div></div>
            </div>
        </div>

        <!-- SECCIÓN IAO -->
        <div id="tab-iao" class="section-view">
            <div class="filters-bar">
                <div class="filter-group"><label>Código Nodo</label><select id="i_nodo" onchange="updateIao()"><option value="ALL">Todos</option></select></div>
                <div class="filter-group"><label>Localidad</label><select id="i_loc" onchange="updateIao()"><option value="ALL">Todas</option></select></div>
                <div class="filter-group"><label>Cuadrilla</label><select id="i_cuad" onchange="updateIao()"><option value="ALL">Todas</option></select></div>
                <div class="filter-group"><label>Tipo IAO</label><select id="i_tipo" onchange="updateIao()"><option value="ALL">Todos</option></select></div>
                <div class="filter-group"><label>Reporte Foto</label><select id="i_repo" onchange="updateIao()"><option value="ALL">Todos</option><option value="Sí">Sí</option><option value="No">No</option></select></div>
            </div>
            <div class="grid-dashboard">
                <div class="card chart-box" style="grid-column: span 4;"><div class="chart-header">Progreso Global IAO</div><div class="chart-wrap"><canvas id="cIaoGlobal"></canvas></div></div>
                <div class="card chart-box" style="grid-column: span 4;"><div class="chart-header">Metraje Drop (Proyectado vs Real)</div><div class="chart-wrap"><canvas id="cIaoDrop"></canvas></div></div>
                <div class="card chart-box" style="grid-column: span 4;"><div class="chart-header">Instalación de Equipos</div><div class="chart-wrap"><canvas id="cIaoInstalacion"></canvas></div></div>
                <div class="card chart-box" style="grid-column: span 6;"><div class="chart-header">Equipos con Serie</div><div class="chart-wrap"><canvas id="cIaoEquipos"></canvas></div></div>
                <div class="card chart-box" style="grid-column: span 6;"><div class="chart-header">Curva S - IAO</div><div class="chart-wrap"><canvas id="cIaoCurvaS"></canvas></div></div>
            </div>
        </div>

        <!-- SECCIÓN PEXT -->
        <div id="tab-pext" class="section-view">
            <div class="filters-bar">
                <div class="filter-group"><label>Código Nodo</label><select id="p_nodo" onchange="updatePext()"><option value="ALL">Todos</option></select></div>
                <div class="filter-group"><label>Cuadrilla</label><select id="p_cuad" onchange="updatePext()"><option value="ALL">Todas</option></select></div>
                <div class="filter-group"><label>Fecha Inicio Ejec.</label><select id="p_fecha" onchange="updatePext()"><option value="ALL">Todas</option></select></div>
                <div class="filter-group"><label>Nivel Spliteo</label><select id="p_spl" onchange="updatePext()"><option value="ALL">Todos</option><option value="1x2">1x2</option><option value="1x4">1x4</option><option value="1x8">1x8</option></select></div>
            </div>
            <div class="grid-dashboard">
                <div class="card kpi-card"><div class="kpi-val" id="p_fo">0m</div><div class="kpi-lbl">FO Ejecutada</div></div>
                <div class="card kpi-card"><div class="kpi-val" id="p_postes">0</div><div class="kpi-lbl">Postes Izados</div></div>
                <div class="card chart-box" style="grid-column: span 6;"><div class="chart-header">FO (Proyectada vs Ejecutada)</div><div class="chart-wrap"><canvas id="cPextFO"></canvas></div></div>
                <div class="card chart-box" style="grid-column: span 12;"><div class="chart-header">Progreso de Infraestructura</div><div class="chart-wrap"><canvas id="cPextInfra"></canvas></div></div>
                <div class="card chart-box" style="grid-column: span 12;"><div class="chart-header">Curva S - PEXT</div><div class="chart-wrap"><canvas id="cPextCurvaS"></canvas></div></div>
            </div>
        </div>

        <!-- SECCIÓN HOTSPOT -->
        <div id="tab-hotspot" class="section-view">
            <div class="filters-bar">
                <div class="filter-group"><label>Código Nodo</label><select id="h_nodo" onchange="updateHot()"><option value="ALL">Todos</option></select></div>
                <div class="filter-group"><label>Localidad</label><select id="h_loc" onchange="updateHot()"><option value="ALL">Todas</option></select></div>
                <div class="filter-group"><label>Ubicación</label><select id="h_ubi" onchange="updateHot()"><option value="ALL">Todas</option></select></div>
                <div class="filter-group"><label>Fecha Inicio Ejec.</label><select id="h_fecha" onchange="updateHot()"><option value="ALL">Todas</option></select></div>
            </div>
            <div class="grid-dashboard">
                <div class="card chart-box" style="grid-column: span 6;"><div class="chart-header">Progreso Global Hotspot</div><div class="chart-wrap"><canvas id="cHotGlobal"></canvas></div></div>
                <div class="card chart-box" style="grid-column: span 6;"><div class="chart-header">Distribución por Ubicación</div><div class="chart-wrap"><canvas id="cHotLoc"></canvas></div></div>
            </div>
        </div>
    </div>

    <script>
        const rawNodo = {json.dumps(nodo_data)};
        const rawPext = {json.dumps(pext_data)};
        const rawIao = {json.dumps(iao_data)};
        const rawHot = {json.dumps(hotspot_data)};

        let isDarkTheme = true;
        Chart.defaults.color = '#94a3b8';
        Chart.defaults.font.family = "'Inter', sans-serif";
        Chart.register(ChartDataLabels);

        const getDatalabels = (isPie = true) => ({{
            display: true,
            color: '#fff',
            font: {{ weight: 'bold', size: 11 }},
            formatter: (val, ctx) => {{
                if (val === 0) return '';
                if (!isPie) return val;
                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                const perc = total > 0 ? ((val / total) * 100).toFixed(1) + '%' : '';
                return val + ' (' + perc + ')';
            }}
        }});

        const barPercDatalabels = {{
            display: true,
            color: '#fff',
            anchor: 'end',
            align: 'top',
            offset: -20,
            font: {{ weight: 'bold', size: 10 }},
            formatter: (val, ctx) => {{
                if (val === 0) return '';
                const idx = ctx.dataIndex;
                const total = ctx.chart.data.datasets.reduce((acc, ds) => acc + (ds.data[idx] || 0), 0);
                const perc = total > 0 ? ((val / total) * 100).toFixed(1) + '%' : '';
                return val + '\\n(' + perc + ')';
            }}
        }};

        let charts = {{}};
        function switchTab(id) {{
            document.querySelectorAll('.section-view').forEach(e => e.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(e => e.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            event.currentTarget.classList.add('active');
        }}

        function popSelect(id, list) {{
            const el = document.getElementById(id);
            [...new Set(list.map(x => String(x || "")))].filter(Boolean).sort().forEach(v => el.add(new Option(v, v)));
        }}

        function initApp() {{
            popSelect('n_nodo', rawNodo.map(d => d.CÓDIGO_NODO));
            popSelect('n_tipo_nodo', rawNodo.map(d => d['TIPO DE NODO']));
            popSelect('n_cultura', rawNodo.map(d => d['TEMA CULTURA?']));
            popSelect('n_cuad', rawNodo.map(d => d.CUADRILLA));
            popSelect('n_altura', rawNodo.map(d => d['ALTURA DE TORRE (m)']));
            popSelect('n_fecha', rawNodo.map(d => d.Fecha_Inicio_Ejecutado));

            popSelect('i_nodo', rawIao.map(d => d.CÓDIGO_NODO));
            popSelect('i_loc', rawIao.map(d => d.LOCALIDAD));
            popSelect('i_cuad', rawIao.map(d => d.CUADRILLA));
            popSelect('i_tipo', rawIao.map(d => d['TIPO DE IAO']));

            popSelect('p_nodo', rawPext.map(d => d.CÓDIGO_NODO));
            popSelect('p_cuad', rawPext.map(d => d.CUADRILLA));
            popSelect('p_fecha', rawPext.map(d => d.Fecha_Inicio_Ejecutado));

            popSelect('h_nodo', rawHot.map(d => d['CODIGO DEL NODO ASIGNADO']));
            popSelect('h_loc', rawHot.map(d => d.LOCALIDAD));
            popSelect('h_ubi', rawHot.map(d => d['UBICACIN DE HOTSPOT'] || d['UBICACIÓN DE HOTSPOT']));
            popSelect('h_fecha', rawHot.map(d => d.Fecha_Inicio_Ejecutado));

            initCharts();
            updateAll();
        }}

        function initCharts() {{
            const pieOpts = {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{position:'right'}}, datalabels: getDatalabels() }} }};
            const barStack = {{ responsive: true, maintainAspectRatio: false, plugins: {{ datalabels: barPercDatalabels }}, scales: {{ x:{{stacked:true}}, y:{{stacked:true}} }} }};
            const lineOpts = {{ responsive: true, maintainAspectRatio: false, plugins: {{ datalabels: {{display:false}} }} }};

            // NODO
            charts.nGlobal = new Chart(document.getElementById('cNodoGlobal'), {{ type:'doughnut', data:{{labels:['Completado','Pendiente'], datasets:[{{backgroundColor:['#10b981','#3b82f6'], data:[0,0]}}]}}, options:pieOpts }});
            charts.nTipos = new Chart(document.getElementById('cNodoTipos'), {{ type:'pie', data:{{labels:[], datasets:[{{backgroundColor:['#f59e0b','#8b5cf6','#06b6d4'], data:[]}}]}}, options:pieOpts }});
            charts.nAlt = new Chart(document.getElementById('cNodoAltura'), {{ type:'bar', data:{{labels:[], datasets:[{{label:'Metros', backgroundColor:'#ec4899', data:[]}}]}}, options:lineOpts }});
            charts.nEq = new Chart(document.getElementById('cNodoEquipos'), {{ type:'bar', data:{{labels:['OLT','ODF','SW','ITM'], datasets:[{{label:'Instalado', backgroundColor:'#10b981', data:[]}},{{label:'Faltante', backgroundColor:'#ef4444', data:[]}}]}}, options:barStack }});
            charts.nS = new Chart(document.getElementById('cNodoCurvaS'), {{ type:'line', data:{{labels:[], datasets:[{{label:'Programado', borderColor:'#f59e0b', fill:false, data:[]}},{{label:'Real', borderColor:'#10b981', fill:false, data:[]}}]}}, options:lineOpts }});

            // IAO
            charts.iGlobal = new Chart(document.getElementById('cIaoGlobal'), {{ type:'doughnut', data:{{labels:['Completado','Pendiente'], datasets:[{{backgroundColor:['#10b981','#3b82f6'], data:[0,0]}}]}}, options:pieOpts }});
            charts.iDrop = new Chart(document.getElementById('cIaoDrop'), {{ type:'bar', data:{{labels:['Proyectado','Ejecutado'], datasets:[{{backgroundColor:['#3b82f6','#10b981'], data:[0,0]}}]}}, options:lineOpts }});
            charts.iInst = new Chart(document.getElementById('cIaoInstalacion'), {{ type:'bar', data:{{labels:['ONT','Switch','Mikrotik','PPLINK'], datasets:[{{label:'Instalado', backgroundColor:'#10b981', data:[]}},{{label:'No Instalado', backgroundColor:'#ef4444', data:[]}}]}}, options:barStack }});
            charts.iEq = new Chart(document.getElementById('cIaoEquipos'), {{ type:'bar', data:{{labels:['ONT','Switch','Mikrotik','PPLINK'], datasets:[{{label:'Series Registradas', backgroundColor:'#8b5cf6', data:[]}}]}}, options:lineOpts }});
            charts.iS = new Chart(document.getElementById('cIaoCurvaS'), {{ type:'line', data:{{labels:[], datasets:[{{label:'Programado', borderColor:'#f59e0b', fill:false, data:[]}},{{label:'Real', borderColor:'#10b981', fill:false, data:[]}}]}}, options:lineOpts }});

            // PEXT
            charts.pFO = new Chart(document.getElementById('cPextFO'), {{ type:'bar', data:{{labels:['Proyectada','Ejecutada'], datasets:[{{backgroundColor:['#3b82f6','#10b981'], data:[0,0]}}]}}, options:lineOpts }});
            charts.pInfra = new Chart(document.getElementById('cPextInfra'), {{ type:'bar', data:{{labels:['Poste Nuevo','Poste BT','Poste MT','CTOs','Mufas ER','Mufas Dist'], datasets:[{{label:'Avanzado', backgroundColor:'#10b981', data:[]}},{{label:'Faltante', backgroundColor:'#ef4444', data:[]}}]}}, options:barStack }});
            charts.pS = new Chart(document.getElementById('cPextCurvaS'), {{ type:'line', data:{{labels:[], datasets:[{{label:'Programado', borderColor:'#f59e0b', fill:false, data:[]}},{{label:'Real', borderColor:'#10b981', fill:false, data:[]}}]}}, options:lineOpts }});

            // HOTSPOT
            charts.hGlobal = new Chart(document.getElementById('cHotGlobal'), {{ type:'doughnut', data:{{labels:['Completado','Pendiente'], datasets:[{{backgroundColor:['#10b981','#3b82f6'], data:[0,0]}}]}}, options:pieOpts }});
            charts.hLoc = new Chart(document.getElementById('cHotLoc'), {{ type:'pie', data:{{labels:[], datasets:[{{backgroundColor:['#f59e0b','#8b5cf6','#06b6d4'], data:[]}}]}}, options:pieOpts }});
        }}

        function updateAll() {{ updateNodo(); updateIao(); updatePext(); updateHot(); }}

        function getSCurve(data, labelProg, labelReal) {{
            let eventsP = {{}}, eventsR = {{}};
            data.forEach(d => {{
                if(d.Fecha_Fin_Programado) eventsP[d.Fecha_Fin_Programado] = (eventsP[d.Fecha_Fin_Programado]||0)+1;
                if(d.Fecha_Fin_Ejecutado) eventsR[d.Fecha_Fin_Ejecutado] = (eventsR[d.Fecha_Fin_Ejecutado]||0)+1;
            }});
            let allD = [...new Set([...Object.keys(eventsP), ...Object.keys(eventsR)])].sort();
            let cP = [], cR = [], accP = 0, accR = 0;
            allD.forEach(day => {{ accP += (eventsP[day]||0); accR += (eventsR[day]||0); cP.push(accP); cR.push(accR); }});
            return {{ labels: allD, prog: cP, real: cR }};
        }}

        function updateNodo() {{
            const fNodo = document.getElementById('n_nodo').value;
            const fTipo = document.getElementById('n_tipo_nodo').value;
            const fCult = document.getElementById('n_cultura').value;
            const fCuad = document.getElementById('n_cuad').value;
            const fAlt = document.getElementById('n_altura').value;
            const fFec = document.getElementById('n_fecha').value;

            const d = rawNodo.filter(x => 
                (fNodo==='ALL'||x.CÓDIGO_NODO===fNodo) &&
                (fTipo==='ALL'||x['TIPO DE NODO']===fTipo) &&
                (fCult==='ALL'||x['TEMA CULTURA?']===fCult) &&
                (fCuad==='ALL'||x.CUADRILLA===fCuad) &&
                (fAlt==='ALL'||String(x['ALTURA DE TORRE (m)'])===fAlt) &&
                (fFec==='ALL'||x.Fecha_Inicio_Ejecutado===fFec)
            );

            let done = d.filter(x => x.OLT_Instalado==='Sí' && x.ODF_Instalado==='Sí' && x.SW_Instalado==='Sí' && x.Reporte_Fotografico==='Sí').length;
            charts.nGlobal.data.datasets[0].data = [done, d.length - done]; charts.nGlobal.update();

            let t = {{}}; d.forEach(x => t[x['TIPO DE NODO']] = (t[x['TIPO DE NODO']]||0)+1);
            charts.nTipos.data.labels = Object.keys(t); charts.nTipos.data.datasets[0].data = Object.values(t); charts.nTipos.update();

            charts.nAlt.data.labels = d.map(x => x.CÓDIGO_NODO); charts.nAlt.data.datasets[0].data = d.map(x => parseFloat(x['ALTURA DE TORRE (m)'])||0); charts.nAlt.update();

            let oltS = d.filter(x => x.OLT_Instalado==='Sí').length;
            let odfS = d.filter(x => x.ODF_Instalado==='Sí').length;
            let swS = d.filter(x => x.SW_Instalado==='Sí').length;
            let itmS = d.reduce((a, b) => a + (parseInt(b.ITM_Instalados)||0), 0);
            charts.nEq.data.datasets[0].data = [oltS, odfS, swS, itmS];
            charts.nEq.data.datasets[1].data = [d.length-oltS, d.length-odfS, d.length-swS, (d.length*2)-itmS];
            charts.nEq.update();

            let s = getSCurve(d); charts.nS.data.labels = s.labels; charts.nS.data.datasets[0].data = s.prog; charts.nS.data.datasets[1].data = s.real; charts.nS.update();
        }}

        function updateIao() {{
            const fNodo = document.getElementById('i_nodo').value;
            const fLoc = document.getElementById('i_loc').value;
            const fCuad = document.getElementById('i_cuad').value;
            const fTipo = document.getElementById('i_tipo').value;
            const fRepo = document.getElementById('i_repo').value;

            const d = rawIao.filter(x => 
                (fNodo==='ALL'||x.CÓDIGO_NODO===fNodo) &&
                (fLoc==='ALL'||x.LOCALIDAD===fLoc) &&
                (fCuad==='ALL'||x.CUADRILLA===fCuad) &&
                (fTipo==='ALL'||x['TIPO DE IAO']===fTipo) &&
                (fRepo==='ALL'||x.Reporte_Fotografico===fRepo)
            );

            let done = d.filter(x => x.Reporte_Fotografico==='Sí').length;
            charts.iGlobal.data.datasets[0].data = [done, d.length - done]; charts.iGlobal.update();

            let pDrop = d.reduce((a, b) => a + (parseFloat(b.Metraje_Cable_Drop_Proyectado)||0), 0);
            let eDrop = d.reduce((a, b) => a + (parseFloat(b.Metraje_Cable_Drop_Ejecutado)||0), 0);
            charts.iDrop.data.datasets[0].data = [pDrop, eDrop]; charts.iDrop.update();

            let q1s = d.filter(x => x['Instalacin_Eq_1_ONT']==='SI').length;
            let q2s = d.filter(x => x['Instalacin_Eq_2_Switch']==='SI').length;
            let q3s = d.filter(x => x['Instalacin_Eq_3_Mikrotik']==='SI').length;
            let q4s = d.filter(x => x['Instalacin_Eq_4_PPLINK']==='SI').length;
            charts.iInst.data.datasets[0].data = [q1s, q2s, q3s, q4s];
            charts.iInst.data.datasets[1].data = [d.length-q1s, d.length-q2s, d.length-q3s, d.length-q4s];
            charts.iInst.update();

            let s1 = d.filter(x => String(x.Serie_Eq_1_ONT).length > 2).length;
            let s2 = d.filter(x => String(x.Serie_Eq_2_Switch).length > 2).length;
            let s3 = d.filter(x => String(x.Serie_Eq_3_Mikrotik).length > 2).length;
            let s4 = d.filter(x => String(x.Serie_Eq_4_PPLINK).length > 2).length;
            charts.iEq.data.datasets[0].data = [s1, s2, s3, s4]; charts.iEq.update();

            let s = getSCurve(d); charts.iS.data.labels = s.labels; charts.iS.data.datasets[0].data = s.prog; charts.iS.data.datasets[1].data = s.real; charts.iS.update();
        }}

        function updatePext() {{
            const fNodo = document.getElementById('p_nodo').value;
            const fCuad = document.getElementById('p_cuad').value;
            const fFec = document.getElementById('p_fecha').value;
            const fSpl = document.getElementById('p_spl').value;

            let d = rawPext.filter(x => 
                (fNodo==='ALL'||x.CÓDIGO_NODO===fNodo) &&
                (fCuad==='ALL'||x.CUADRILLA===fCuad) &&
                (fFec==='ALL'||x.Fecha_Inicio_Ejecutado===fFec)
            );
            if(fSpl!=='ALL') d = d.filter(x => parseFloat(x['Splitter_'+fSpl+'_Cant']) > 0);

            let foP = d.reduce((a, b) => a + (parseFloat(b.Metraje_FO_Proyectado)||0), 0);
            let foE = d.reduce((a, b) => a + (parseFloat(b.Metraje_FO_Ejecutado)||0), 0);
            document.getElementById('p_fo').innerText = foE.toFixed(0) + 'm';
            charts.pFO.data.datasets[0].data = [foP, foE]; charts.pFO.update();

            let pnR = d.reduce((a, b) => a + (parseFloat(b.Cant_Postes_Nuevos)||0), 0);
            let btR = d.reduce((a, b) => a + (parseFloat(b.Cant_Postes_Electricos_BT)||0), 0);
            let mtR = d.reduce((a, b) => a + (parseFloat(b.Cant_Postes_Electricos_MT)||0), 0);
            let pnE = d.reduce((a, b) => a + (parseFloat(b.Izados_Postes_Nuevos)||0), 0);
            // Asumiendo que Izados aplica a nuevos por ahora, si no hay columna de izados por tipo.
            
            let ctoE = d.reduce((a, b) => a + (parseFloat(b.Cant_CTOs)||0), 0);
            let erE = d.reduce((a, b) => a + (parseFloat(b.Cant_Mufas_ER)||0), 0);
            let diE = d.reduce((a, b) => a + (parseFloat(b.Cant_Mufas_Dist)||0), 0);
            
            document.getElementById('p_postes').innerText = pnE;
            charts.pInfra.data.datasets[0].data = [pnE, 0, 0, ctoE, erE, diE];
            charts.pInfra.data.datasets[1].data = [pnR-pnE, btR, mtR, 0, 0, 0];
            charts.pInfra.update();

            let s = getSCurve(d); charts.pS.data.labels = s.labels; charts.pS.data.datasets[0].data = s.prog; charts.pS.data.datasets[1].data = s.real; charts.pS.update();
        }}

        function updateHot() {{
            const fNodo = document.getElementById('h_nodo').value;
            const fLoc = document.getElementById('h_loc').value;
            const fUbi = document.getElementById('h_ubi').value;
            const fFec = document.getElementById('h_fecha').value;

            const d = rawHot.filter(x => 
                (fNodo==='ALL'||x['CODIGO DEL NODO ASIGNADO']===fNodo) &&
                (fLoc==='ALL'||x.LOCALIDAD===fLoc) &&
                (fUbi==='ALL'||(x['UBICACIN DE HOTSPOT']||x['UBICACIÓN DE HOTSPOT'])===fUbi) &&
                (fFec==='ALL'||x.Fecha_Inicio_Ejecutado===fFec)
            );

            let done = d.filter(x => x.Reporte_Fotografico==='Sí').length;
            charts.hGlobal.data.datasets[0].data = [done, d.length - done]; charts.hGlobal.update();

            let t = {{}}; d.forEach(x => {{ let k = x['UBICACIN DE HOTSPOT']||x['UBICACIÓN DE HOTSPOT']; t[k] = (t[k]||0)+1; }});
            charts.hLoc.data.labels = Object.keys(t); charts.hLoc.data.datasets[0].data = Object.values(t); charts.hLoc.update();
        }}

        window.onload = initApp;
        function toggleTheme() {{ isDarkTheme = !isDarkTheme; document.documentElement.setAttribute('data-theme', isDarkTheme?'dark':'light'); }}
    </script>
</body>
</html>
"""

    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_template)
    print("Dashboard FTTH V5 Generado Exitosamente.")

if __name__ == "__main__":
    run()
