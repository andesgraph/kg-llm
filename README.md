kg-llm

Pipeline mínimo para conectar un grafo RDF (TTL) con un modelo LLM local usando un índice vectorial ligero para recuperación semántica.

Estructura del proyecto

kg-llm/
├── README.md
├── config.yaml
├── data/
│   ├── grafo.ttl
│   └── index_entities.json
├── index/
│   └── entity_vectors.npz
├── modelos/
│   └── qwen2.5-0.5b.gguf
└── scripts/
    ├── extract_entities.py
    ├── build_index.py
    └── answer.py

Requisitos

- Python 3.9+
- pip
- Archivo RDF en formato Turtle (data/grafo.ttl)
- Modelo LLM local en formato .gguf (modelos/qwen2.5-0.5b.gguf)

Instalación

python3 -m venv llm-env
source llm-env/bin/activate
pip install rdflib sentence-transformers numpy transformers

Configuración

El archivo config.yaml define las rutas y parámetros básicos del sistema. Ejemplo:

graph_file: data/grafo.ttl
entities_file: data/index_entities.json
vectors_path: index/entity_vectors.npz
model_path: modelos/qwen2.5-0.5b.gguf
top_k: 5

Pasos detallados

1. Preparar el entorno

   - Activar el entorno virtual:
     source llm-env/bin/activate

   - Verificar que existen:
     - data/grafo.ttl
     - modelos/qwen2.5-0.5b.gguf
     - config.yaml (con rutas correctas)

2. Extraer entidades desde el grafo

   python scripts/extract_entities.py

   Este comando lee data/grafo.ttl y genera data/index_entities.json con las entidades y metadatos básicos.

3. Construir el índice vectorial

   python scripts/build_index.py

   Este comando lee data/index_entities.json, calcula embeddings y guarda index/entity_vectors.npz.

4. Hacer consultas con recuperación + LLM

   python scripts/answer.py "¿Quién es el Ukuku?"

   El script usa el índice vectorial y el modelo definido en config.yaml para generar una respuesta basada en las entidades más cercanas a la pregunta.

Configurar GitHub

git init
git add .
git commit -m "Initial kg-llm pipeline"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/kg-llm.git
git push -u origin main
