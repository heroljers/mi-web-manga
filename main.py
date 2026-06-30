from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import List
import json

app = FastAPI(title="Manga & Anime Móvil")

# --- MODELOS DE DATOS ---
class Capitulo(BaseModel):
    numero: float
    titulo_capitulo: str
    tipo: str  # "manga" o "anime"
    contenido_url: str 

class Serie(BaseModel):
    id: int
    titulo: str
    sinopsis: str
    imagen_portada: str
    capitulos: List[Capitulo] = []

# --- BASE DE DATOS DE PRUEBA ---
bd_series = [
    Serie(
        id=1,
        titulo="Anime de Prueba",
        sinopsis="Gestiona este contenido desde el panel de administración inferior.",
        imagen_portada="https://picsum.photos/200/300",
        capitulos=[
            Capitulo(numero=1, titulo_capitulo="Episodio Piloto", tipo="anime", contenido_url="https://www.w3schools.com/html/mov_bbb.mp4")
        ]
    )
]

# --- INTERFAZ WEB COMPLETA (Responsiva para Celulares) ---
HTML_COMPLETO = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MangaAnime Móvil</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #0f0f14; color: #ffffff; margin: 0; padding: 15px; }
        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #ff4a5a; padding-bottom: 10px; margin-bottom: 20px; }
        header h1 { color: #ff4a5a; margin: 0; font-size: 22px; }
        .btn { background: #ff4a5a; color: white; border: none; padding: 10px 15px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 15px; }
        .card { background: #181824; border-radius: 8px; overflow: hidden; border: 1px solid #2d2d3f; }
        .card img { width: 100%; height: 200px; object-fit: cover; }
        .card-body { padding: 8px; }
        .card-body h3 { margin: 0 0 5px 0; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        
        /* Panel Admin Form */
        .admin-section { background: #1c1c28; padding: 15px; border-radius: 8px; margin-top: 40px; border-top: 3px solid #00b4d8; }
        .admin-section h2 { margin-top: 0; color: #00b4d8; font-size: 18px; }
        input, textarea, select { width: 100%; padding: 10px; margin-bottom: 10px; background: #10101a; border: 1px solid #333; color: white; border-radius: 5px; font-size: 14px; }
        
        /* Lector y Reproductor */
        .manga-lector img { display: block; max-width: 100%; margin: 8px auto; }
        video { width: 100%; border-radius: 8px; background: #000; max-height: 240px; }
        ul { list-style: none; padding: 0; }
        li { background: #222533; padding: 12px; margin-bottom: 8px; border-radius: 6px; font-size: 14px; }
    </style>
</head>
<body>
    <header>
        <h1 onclick="irAInicio()" style="cursor:pointer;">OtakuStream</h1>
        <button class="btn" onclick="irAInicio()">Inicio</button>
    </header>

    <div id="app"></div>

    <div class="admin-section">
        <h2>Panel de Control (Añadir Contenido)</h2>
        <form action="/admin/subir_capitulo" method="post">
            <label>ID de la Serie (Ej: 1):</label>
            <input type="number" name="serie_id" required>
            <label>Número de Capítulo:</label>
            <input type="number" step="0.1" name="numero" required>
            <label>Título del Capítulo:</label>
            <input type="text" name="titulo_capitulo" required>
            <label>Tipo:</label>
            <select name="tipo">
                <option value="anime">Anime (Video)</option>
                <option value="manga">Manga (Imágenes)</option>
            </select>
            <label>URL del contenido (Enlace .mp4 o URLs de imágenes separadas por comas):</label>
            <textarea name="contenido_url" rows="3" required></textarea>
            <button type="submit" class="btn" style="background:#00b4d8; width:100%;">Publicar Capítulo Ahora</button>
        </form>
    </div>

    <script>
        const series = {series_json};

        function irAInicio() {
            let html = '<div class="grid">';
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
                <h2>${serie.titulo}</h2>
                <p style="color:#aaa; font-size:13px;">${serie.sinopsis}</p>
                <h3>Capítulos:</h3>
                <ul>
            `;
            if(serie.capitulos.length === 0) html += '<p>No hay capítulos aún.</p>';
            serie.capitulos.forEach((c, index) => {
                html += `<li onclick="verCapitulo(${id}, ${index})">Cap. ${c.numero}: ${c.titulo_capitulo} [${c.tipo.toUpperCase()}]</li>`;
            });
            html += '</ul>';
            document.getElementById('app').innerHTML = html;
        }

        function verCapitulo(serieId, capIndex) {
            const serie = series.find(s => s.id === serieId);
            const cap = serie.capitulos[capIndex];
            let html = `<button class="btn" onclick="verSerie(${serieId})" style="margin-bottom:10px;">← Volver</button>
                        <h2>${cap.titulo_capitulo}</h2>`;

            if (cap.tipo === 'anime') {
                html += `<video controls autoplay playsinline src="${cap.contenido_url}"></video>`;
            } else if (cap.tipo === 'manga') {
                html += '<div class="manga-lector">';
                const paginas = cap.contenido_url.split(',');
                paginas.forEach(url => { html += `<img src="${url.trim()}">`; });
                html += '</div>';
            }
            document.getElementById('app').innerHTML = html;
            window.scrollTo(0,0);
        }

        irAInicio();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    series_json = json.dumps([s.dict() for s in bd_series])
    return HTML_COMPLETO.replace("{series_json}", series_json)

@app.post("/admin/subir_capitulo")
async def admin_subir(serie_id: int = Form(...), numero: float = Form(...), titulo_capitulo: str = Form(...), tipo: str = Form(...), contenido_url: str = Form(...)):
    nuevo_cap = Capitulo(numero=numero, titulo_capitulo=titulo_capitulo, tipo=tipo, contenido_url=contenido_url)
    for serie in bd_series:
        if serie.id == serie_id:
            serie.capitulos.append(nuevo_cap)
            break
    return RedirectResponse(url="/", status_code=303)
