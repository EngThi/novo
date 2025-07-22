from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import subprocess
import os
import sys
import json
from datetime import datetime
from pathlib import Path
import uvicorn

# Adicionar diretório pai ao path para importar módulos
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from utils.sheets_tracker import SheetsTracker

app = FastAPI(title="Pipeline Automação de Vídeos")
templates = Jinja2Templates(directory="dashboard/templates")
app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")

# Cache de projetos recentes
recent_projects = []

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página inicial do dashboard"""
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "recent_projects": recent_projects}
    )

@app.get("/projects", response_class=HTMLResponse)
async def list_projects(request: Request):
    """Lista todos os projetos"""
    # Buscar projetos na pasta de output
    output_dir = parent_dir / "youtube_automation" / "output"
    projects = []
    
    if output_dir.exists():
        for item in output_dir.iterdir():
            if item.is_dir():
                # Extrair data e nome do projeto
                parts = item.name.split('_', 1)
                if len(parts) == 2:
                    date = parts[0]
                    name = parts[1].replace('_', ' ')
                    
                    # Verificar se há vídeo final
                    has_video = (item / "final" / "video_final.mp4").exists()
                    
                    projects.append({
                        "date": date,
                        "name": name,
                        "path": str(item),
                        "has_video": has_video,
                        "dir_name": item.name
                    })
    
    # Ordenar por data (mais recente primeiro)
    projects.sort(key=lambda x: x["date"], reverse=True)
    
    return templates.TemplateResponse(
        "projects.html", 
        {"request": request, "projects": projects}
    )

@app.get("/project/{dir_name}", response_class=HTMLResponse)
async def project_details(request: Request, dir_name: str):
    """Mostrar detalhes de um projeto específico"""
    output_dir = parent_dir / "youtube_automation" / "output" / dir_name
    
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    # Coletar informações do projeto
    project_info = {
        "name": dir_name.split('_', 1)[1].replace('_', ' ') if '_' in dir_name else dir_name,
        "date": dir_name.split('_', 1)[0] if '_' in dir_name else "",
        "dir_name": dir_name,
        "files": []
    }
    
    # Coletar informações dos arquivos
    for root, _, files in os.walk(output_dir):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, output_dir)
            size = os.path.getsize(file_path)
            project_info["files"].append({
                "name": file,
                "path": rel_path,
                "size": f"{size / 1024:.1f} KB",
                "is_video": file.endswith(('.mp4', '.avi', '.mov')),
                "is_audio": file.endswith(('.mp3', '.wav')),
                "is_image": file.endswith(('.jpg', '.png', '.jpeg'))
            })
    
    # Verificar se há script e segmentos
    script_path = output_dir / "script.txt"
    segments_path = output_dir / "segments.json"
    
    script_content = None
    segments = None
    
    if script_path.exists():
        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f.read()
    
    if segments_path.exists():
        with open(segments_path, "r", encoding="utf-8") as f:
            segments = json.load(f)
    
    return templates.TemplateResponse(
        "project_detail.html", 
        {
            "request": request, 
            "project": project_info,
            "script": script_content,
            "segments": segments
        }
    )

@app.post("/run")
async def run_pipeline(topic: str = Form(...)):
    """Inicia uma execução do pipeline com o tópico especificado"""
    try:
        # Executar o pipeline com o tópico fornecido
        cmd = [
            "python", 
            str(parent_dir / "pipeline_automatizado.py"),
            "--topic", topic
        ]
        
        # Iniciar processo em background
        subprocess.Popen(cmd)
        
        # Registrar no cache de projetos recentes
        recent_projects.append({
            "topic": topic,
            "status": "Iniciado",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Manter apenas os 5 projetos mais recentes
        global recent_projects
        recent_projects = recent_projects[-5:]
        
        # Adicionar à planilha de tracking
        try:
            tracker = SheetsTracker()
            tracker.update_status(topic, "Iniciado", "Descoberta")
        except Exception as e:
            print(f"Erro ao atualizar planilha: {e}")
        
        return {"status": "success", "message": f"Pipeline iniciado para o tópico: {topic}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/status")
async def get_status():
    """Retorna o status atual do sistema"""
    # Verificar execuções recentes
    pipeline_log = parent_dir / "pipeline.log"
    recent_logs = []
    
    if pipeline_log.exists():
        with open(pipeline_log, "r", encoding="utf-8") as f:
            lines = f.readlines()
            recent_logs = lines[-20:]  # últimas 20 linhas
    
    # Verificar uso de CPU/memória
    import psutil
    system_stats = {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }
    
    return {
        "recent_logs": recent_logs,
        "system_stats": system_stats,
        "recent_projects": recent_projects
    }

if __name__ == "__main__":
    # Criar diretório de templates se não existir
    templates_dir = Path("dashboard/templates")
    templates_dir.mkdir(exist_ok=True, parents=True)
    
    static_dir = Path("dashboard/static")
    static_dir.mkdir(exist_ok=True, parents=True)
    
    # Criar arquivos de template básicos se não existirem
    index_html = templates_dir / "index.html"
    if not index_html.exists():
        with open(index_html, "w", encoding="utf-8") as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Dashboard - Pipeline de Vídeos</title>
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
                <link rel="stylesheet" href="/static/style.css">
            </head>
            <body>
                <div class="container mt-4">
                    <h1>Dashboard - Pipeline de Automação de Vídeos</h1>
                    
                    <div class="row mt-4">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    Iniciar Nova Execução
                                </div>
                                <div class="card-body">
                                    <form id="run-form">
                                        <div class="mb-3">
                                            <label for="topic" class="form-label">Tópico do Vídeo</label>
                                            <input type="text" class="form-control" id="topic" name="topic" required>
                                        </div>
                                        <button type="submit" class="btn btn-primary">Iniciar Pipeline</button>
                                    </form>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    Status do Sistema
                                </div>
                                <div class="card-body">
                                    <div class="progress mb-3">
                                        <div id="cpu-usage" class="progress-bar" role="progressbar" style="width: 0%">CPU: 0%</div>
                                    </div>
                                    <div class="progress mb-3">
                                        <div id="memory-usage" class="progress-bar bg-info" role="progressbar" style="width: 0%">Memória: 0%</div>
                                    </div>
                                    <div class="progress">
                                        <div id="disk-usage" class="progress-bar bg-warning" role="progressbar" style="width: 0%">Disco: 0%</div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="card mt-3">
                                <div class="card-header">
                                    Execuções Recentes
                                </div>
                                <div class="card-body">
                                    <div id="recent-projects">
                                        {% if recent_projects %}
                                            <table class="table table-sm">
                                                <thead>
                                                    <tr>
                                                        <th>Tópico</th>
                                                        <th>Status</th>
                                                        <th>Timestamp</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {% for project in recent_projects %}
                                                    <tr>
                                                        <td>{{ project.topic }}</td>
                                                        <td>{{ project.status }}</td>
                                                        <td>{{ project.timestamp }}</td>
                                                    </tr>
                                                    {% endfor %}
                                                </tbody>
                                            </table>
                                        {% else %}
                                            <p>Nenhuma execução recente.</p>
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card mt-4">
                        <div class="card-header">
                            Log Recente
                        </div>
                        <div class="card-body">
                            <pre id="recent-logs" class="log-container">Carregando logs...</pre>
                        </div>
                    </div>
                    
                    <div class="mt-4">
                        <a href="/projects" class="btn btn-secondary">Ver Todos os Projetos</a>
                    </div>
                </div>
                
                <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
                <script>
                    // Atualizar status a cada 5 segundos
                    function updateStatus() {
                        $.ajax({
                            url: '/status',
                            success: function(data) {
                                // Atualizar uso de recursos
                                $('#cpu-usage').css('width', data.system_stats.cpu + '%')
                                    .text('CPU: ' + data.system_stats.cpu + '%');
                                
                                $('#memory-usage').css('width', data.system_stats.memory + '%')
                                    .text('Memória: ' + data.system_stats.memory + '%');
                                
                                $('#disk-usage').css('width', data.system_stats.disk + '%')
                                    .text('Disco: ' + data.system_stats.disk + '%');
                                
                                // Atualizar logs
                                $('#recent-logs').text(data.recent_logs.join(''));
                            }
                        });
                    }
                    
                    // Iniciar nova execução
                    $('#run-form').submit(function(e) {
                        e.preventDefault();
                        
                        $.ajax({
                            type: 'POST',
                            url: '/run',
                            data: {
                                topic: $('#topic').val()
                            },
                            success: function(response) {
                                if (response.status === 'success') {
                                    alert('Pipeline iniciado com sucesso!');
                                    $('#topic').val('');
                                    
                                    // Recarregar a página após 2 segundos
                                    setTimeout(function() {
                                        window.location.reload();
                                    }, 2000);
                                } else {
                                    alert('Erro: ' + response.message);
                                }
                            }
                        });
                    });
                    
                    // Atualizar status inicial e depois a cada 5 segundos
                    updateStatus();
                    setInterval(updateStatus, 5000);
                </script>
            </body>
            </html>
            """)
    
    # Criar arquivo CSS básico se não existir
    css_file = static_dir / "style.css"
    if not css_file.exists():
        with open(css_file, "w", encoding="utf-8") as f:
            f.write("""
            .log-container {
                max-height: 300px;
                overflow-y: auto;
                background-color: #f8f9fa;
                padding: 10px;
                font-size: 0.8em;
            }
            """)
    
    # Iniciar servidor na porta padrão do Replit
    port = int(os.getenv("DASHBOARD_PORT", 5000))
    host = os.getenv("DASHBOARD_HOST", "0.0.0.0")
    uvicorn.run("utils.dashboard.app:app", host=host, port=port, reload=True)