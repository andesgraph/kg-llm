# kg-llm

**kg-llm** es un pipeline mínimo y modular que conecta un **grafo RDF (TTL)** con un **modelo LLM local**, utilizando un **índice vectorial ligero** para recuperación semántica.  
Está diseñado para casos donde se requiere consultar un grafo de conocimiento desde lenguaje natural sin depender de APIs externas — ideal para patrimonio cultural, humanidades digitales o prototipos rápidos de RAG local.

---

## Características

- Procesa un grafo RDF y extrae entidades relevantes.
- Genera un índice vectorial a partir de embeddings ligeros.
- Conecta preguntas en lenguaje natural con entidades del grafo.
- Funciona completamente **offline** con modelos `.gguf`.
- Código simple, modular y fácil de extender.

---

## Estructura del proyecto

```text
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
```

---

## Requisitos

- Python 3.9+
- pip
- Archivo RDF en formato Turtle (`data/grafo.ttl`)
- Modelo LLM local en formato `.gguf` compatible con llama.cpp

---

## Instalación

1. Crear entorno virtual:

```bash
python3 -m venv llm-env
source llm-env/bin/activate
```

2. Instalar dependencias:

```bash
pip install rdflib sentence-transformers numpy transformers
```

---

## Configuración

Editar `config.yaml` según tus rutas:

```yaml
graph_file: data/grafo.ttl
entities_file: data/index_entities.json
vectors_path: index/entity_vectors.npz
model_path: modelos/qwen2.5-0.5b.gguf
top_k: 5
```

---

## Uso

### 1. Extraer entidades del grafo

```bash
python scripts/extract_entities.py
```

Genera `data/index_entities.json`.

---

### 2. Construir el índice vectorial

```bash
python scripts/build_index.py
```

Genera `index/entity_vectors.npz`.

---

### 3. Hacer consultas con recuperación + LLM

```bash
python scripts/answer.py "¿Quién es el Ukuku?"
```

La respuesta combina la recuperación del grafo y el modelo local.

---

## Subir el proyecto a GitHub

```bash
git init
git add .
git commit -m "Initial kg-llm pipeline"
git branch -M main
git remote add origin https://github.com/andesgraph/kg-llm.git
git push -u origin main
```

---

## Licencia

MIT License. Puedes usarlo y modificarlo libremente.

---

## Contribuciones

Pull requests y mejoras son bienvenidas.  
Si deseas reportar errores, usa los Issues del repositorio.

