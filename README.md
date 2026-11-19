# Laboratorio 1 · Catálogo de libros

Solución del laboratorio de scraping y análisis de `books.toscrape.com`. El notebook obtiene los libros por categoría, sigue las páginas siguientes, limpia los campos, explora los resultados y guarda el CSV que utiliza la aplicación Streamlit.

Se requiere Python 3.10 o posterior.

## Instalación

Desde esta carpeta, en PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Abre JupyterLab con `jupyter lab`, selecciona el intérprete de `.venv` y ejecuta `lab1_catalogo_libros.ipynb` de arriba abajo. El scraping realiza una pausa entre peticiones y guarda los ficheros en `data/raw/` y `data/processed/`.

## Aplicación

Después de ejecutar el notebook:

```powershell
streamlit run app.py
```

La app permite filtrar libros por categoría, valoración y precio, y muestra gráficos y una tabla interactiva.

## Estructura

```text
├── app.py
├── catalogo.py
├── lab1_catalogo_libros.ipynb
├── requirements.txt
└── data/
    ├── raw/libros_raw.csv
    └── processed/libros.csv
```

El sitio es ficticio y se utiliza con fines educativos. El código identifica las peticiones, no accede a las fichas individuales y espera entre solicitudes para reducir la carga del servidor.
