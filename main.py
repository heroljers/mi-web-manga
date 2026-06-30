from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import List
import json

app = FastAPI(title="Manga & Manhua Stream Premium")

# --- MODELOS DE DATOS ---
class Capitulo(BaseModel):
    numero: float
    titulo_capitulo: str
    paginas: List[str]

class Serie(BaseModel):
    id: int
    titulo: str
    sinopsis: str
    imagen_portada: str
    capitulos: List[Capitulo] = []

# --- BASE DE DATOS (En memoria) ---
bd_series = [
    Serie(
        id=1,
        titulo="La Venganza del Sabueso de Sangre de Hierro",
        sinopsis="Un manhua espectacular sobre venganza, regresión y combates intensos.",
        imagen_portada="https://images.unsplash.com/photo-1578632767115-351597cf2477?w=500",
        capitulos=[
            Capitulo(
                numero=1, 
                titulo_capitulo="Prólogo del Sabueso", 
                paginas=[
                    "https://picsum.photos/800/1200?random=1",
                    "https://picsum.photos/800/1200?random=2",
                    "https://picsum.photos/800/1200?random=3"
                ]
            )
        ]
    )
]

# --- INTERFAZ PREMIUM (Estilo Olympus Scanlation) ---
HTML_COMPLETO = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MangaVerse - Premium Stream</title>
    <style>
        * { box-sizing: border-box; transition: all 0.2s ease; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #0c0e17; color: #f8f9fa; margin: 0; padding: 0; padding-bottom: 60px; }
        
        /* Navbar Superior */
        header { display: flex; justify-content: space-between; align-items: center; background: #121626; border-bottom: 2px solid #ffb703; padding: 15px 20px; position: sticky; top: 0; z-index: 1000; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        header h1 { color: #ffb703; margin: 0; font-size: 24px; font-weight: 800; letter-spacing: 1px; cursor: pointer; }
        .btn-nav { background: #ffb703; color: #0c0e17; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px; }
        .btn-nav:hover { background: #fff; transform: translateY(-2px); }
        
        /* Contenedor Principal */
        .container { max-width: 1000px; margin: 20px auto; padding: 0 15px; }
        
        /* Secciones de Títulos */
        .section-title { font-size: 20px; color: #ffb703; border-left: 4px solid #ffb703; padding-left: 10px; margin-bottom: 20px; font-weight: 700; }
        
        /* Grid de Series */
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 20px; }
        .card { background: #121626; border-radius: 12px; overflow: hidden; border: 1px solid #1f263f; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }
        .card:hover { transform: translateY(-5px); border-color: #ffb703; box-shadow: 0 6px 15px rgba(255,183,3,0.2); }
        .card img { width: 100%; height: 220px; object-fit: cover; }
        .card-body { padding: 10px; text-align: center; }
        .card-body h3 { margin: 0; font-size: 14px; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        
        /* Perfil de Serie Expandido */
        .serie-header { background: #121626; padding: 20px; border-radius: 14px; border: 1px solid #1f263f; margin-bottom: 25px; }
        .serie-header h2 { margin-top: 0; color: #ffb703; }
        .sinopsis { color: #a0a5c1; font-size: 14px; line-height: 1.6; }
        
        /* Lista de Capítulos */
        ul { list-style: none; padding: 0; }
        li { background: #161c33; padding: 15px; margin-bottom: 10px; border-radius: 8px; border: 1px solid #1f263f; display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
        li:hover { background: #1f263f; border-color: #ffb703; }
        li span { color: #fff; font-weight: 600; }
        
        /* Lector en Cascada Profesional */
        .manga-lector { background: #000; padding: 10px 0; border-radius: 8px; margin-top: 15px; }
        .manga-lector img { display: block; max-width: 100%; width: 100%; height: auto; margin: 0 auto; content-visibility: auto; }
        
        /* Paneles de Control (Admin) */
        .admin-box { background: #121626; padding: 20px; border-radius: 12px; margin-top: 40px; border: 1px solid #ffb703; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }
        .admin-box h2 { margin-top: 0; color: #ffb703; font-size: 18px; border-bottom: 1px solid #1f263f; padding-bottom: 10px; }
        label { display: block; margin-bottom: 5px; font-size: 13px; color: #a0a5c1; font-weight: 600; }
        input, textarea, select { width: 100%; padding: 12px; margin-bottom: 15px; background: #0c0e17; border: 1px solid #1f263f; color: white; border-radius: 6px; font-size: 14px; }
        input:focus, textarea:focus { border-color: #ffb703; outline: none; }
        .btn-submit { background: #ffb703; color: #0c0e17; border: none; padding: 12px; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; font-size: 15px; }
        .btn-submit:hover { background: #fff; }
    </style>
</head>
<body>
    <header>
        <h1 onclick="irAInicio()">MangaVerse</h1>
        <button class="btn-nav" onclick="irAInicio()">Catálogo</button>
    </header>

    <div class="container" id="app"></div>

    <div class="container">
        <div class="admin-box">
            <h2>Panel de Control: Agregar Nueva Serie</h2>
            <form action="/admin/crear_serie" method="post">
                <label>ID único de la Serie (Ej: 2, 3, 4):</label>
                <input type="number" name="id" required>
                <label>Título del Manhua / Manga:</label>
                <input type="text" name="titulo" required>
                <label>Sinopsis:</label>
                <textarea name="sinopsis" rows="2" required></textarea>
                <label>URL de la Imagen de Portada:</label>
                <input type="text" name="imagen_portada" required>
                <button type="submit" class="btn-submit">Registrar Serie</button>
            </form>
        </div>

        <div class="admin-box">
            <h2>Panel de Control: Publicar Capítulo (Masivo)</h2>
            <form action="/admin/subir_capitulo" method="post">
                <label>ID de la Serie a la que pertenece:</label>
                <input type="number" name="serie_id" required>
                <label>Número de Capítulo (Ej: 1 o 1.5):</label>
                <input type="number" step="0.1" name="numero" required>
                <label>Nombre del Capítulo (Opcional):</label>
                <input type="text" name="titulo_capitulo" required>
                <label>Pegar todas las URLs de las Páginas (Separadas por comas o saltos de línea):</label>
                <textarea name="paginas_raw" rows="6" placeholder="https://enlace1.com/p1.jpg&#10;https://enlace2.com/p2.jpg" required></textarea>
                <button type="submit" class="btn-submit" style="background: #2196f3; color: white;">Publicar Capítulo</button>
            </form>
        </div>
    </div>

    <script>
        const series = {series_json};

        function irAInicio() {
            let html = '<div class="section-title">Últimas Series Agregadas</div><div class="grid">';
            series.forEach(s => {
                html += `
                    <div class="card" onclick="verSerie(${s.id})">
                        <img src="${s.imagen_portada}" alt="${s.titulo}">
                        <div class="card-body">
                            <h3>${s.titulo}</h3>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            document.getElementById('app').innerHTML = html;
        }

        function verSerie(id) {
            const serie = series.find(s => s.id === id);
            let html = `
                <div class="serie-header">
                    <h2>${serie.titulo}</h2>
                    <p class="sinopsis">${serie.sinopsis}</p>
                </div>
                <div class="section-title">Lista de Capítulos</div>
                <ul>
            `;
            if(serie.capitulos.length === 0) html += '<p style="color:#a0a5c1; padding-left:10px;">Próximamente más capítulos.</p>';
            
            // Ordenar capítulos de mayor a menor número
            const capsOrdenados = [...serie.capitulos].sort((a,b) => b.numero - a.numero);
            
            capsOrdenados.forEach((c) => {
                const indexOriginal = serie.capitulos.findIndex(orig => orig.numero === c.numero);
                html += `
                    <li onclick="verCapitulo(${id}, ${indexOriginal})">
                        <span>Capítulo ${c.numero}: ${c.titulo_capitulo}</span>
                        <span style="color:#ffb703; font-size:12px;">LEER →</span>
                    </li>
                `;
            });
            html += '</ul>';
            document.getElementById('app').innerHTML = html;
            window.scrollTo(0,0);
        }

        function verCapitulo(serieId, capIndex) {
            const serie = series.find(s => s.id === serieId);
            const cap = serie.capitulos[capIndex];
            let html = `
                <button class="btn-nav" onclick="verSerie(${serieId})" style="margin-bottom:15px;">← Lista de Caps</button>
                <h2 style="color:#ffb703; margin-bottom:5px;">${serie.titulo}</h2>
                <h4 style="margin-top:0; color:#a0a5c1;">Capítulo ${cap.numero}: ${cap.titulo_capitulo}</h4>
                <div class="manga-lector">
            `;
            cap.paginas.forEach(url => {
                if(url.trim()) {
                    html += `<img src="${url.trim()}" alt="Página" loading="lazy">`;
                }
            });
            html += '</div>';
            document.getElementById('app').innerHTML = html;
            window.scrollTo(0,0);
        }

        // Ejecución Inicial
        irAInicio();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    series_json = json.dumps([s.dict() for s in bd_series])
    return HTML_COMPLETO.replace("{series_json}", series_json)

@app.post("/admin/crear_serie")
async def crear_serie(id: int = Form(...), titulo: str = Form(...), sinopsis: str = Form(...), imagen_portada: str = Form(...)):
    for s in bd_series:
        if s.id == id:
            return HTMLResponse("<h2>Error: El ID ya existe. Regresa e intenta con otro.</h2>")
    
    nueva_serie = Serie(id=id, titulo=titulo, sinopsis=sinopsis, imagen_portada=imagen_portada, capitulos=[])
    bd_series.append(nueva_serie)
    return RedirectResponse(url="/", status_code=303)

@app.post("/admin/subir_capitulo")
async def admin_subir(serie_id: int = Form(...), numero: float = Form(...), titulo_capitulo: str = Form(...), paginas_raw: str = Form(...)):
    lineas = paginas_raw.replace(",", "\\n").split("\\n")
    lista_paginas = [url.strip() for url in lineas if url.strip()]
    
    nuevo_cap = Capitulo(numero=numero, titulo_capitulo=titulo_capitulo, paginas=lista_paginas)
    
    for serie in bd_series:
        if serie.id == serie_id:
            serie.capitulos = [c for c in serie.capitulos if c.numero != numero]
            serie.capitulos.append(nuevo_cap)
            break
            
    return RedirectResponse(url="/", status_code=303)
    
