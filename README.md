# kg-llm

**kg-llm** es un pipeline mínimo y modular que conecta un **grafo RDF (TTL)** con un **modelo LLM local**, utilizando 
un **índice vectorial ligero** para recuperación semántica. En este proyecto, lo aplicamos para modelar el 
conocimiento cultural de dos festividades andinas fundamentales: la **Virgen del Carmen de Paucartambo** y 
el **Señor de Qoyllur Rit’i**, integrando información sobre danzas, personajes rituales, comunidades y prácticas 
ceremoniales. Este enfoque permite consultar el grafo mediante lenguaje natural sin depender de APIs externas, 
ofreciendo una solución eficiente para proyectos de **patrimonio cultural**, **humanidades digitales** y prototipos 
rápidos de **RAG local** orientados a la preservación y análisis computacional de tradiciones vivas.

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

## Guía completa para trabajo colaborativo con GitHub Desktop, GitHub Web y Raspberry Pi (terminal)

Este documento explica **cómo deben trabajar 2–3 personas** sobre el proyecto `kg-llm`, usando:

- **GitHub Desktop** (para trabajar en PC/Mac con interfaz gráfica)  
- **GitHub Web** (para crear Pull Requests y revisarlos)  
- **Raspberry Pi con terminal** (para actualizar el proyecto y regenerar índices)

Todo es claro, ordenado y paso a paso.

---

# 1. Estructura del equipo

- **Cuenta A**  
  Dueña del repositorio original en GitHub.  
  La Raspberry Pi está conectada a este repositorio (hace `git pull`, `git push` si corresponde).

- **Cuenta B, Cuenta C**  
  Personas que editan la ontología con **Protégé Desktop**.  
  Trabajan sobre **forks** usando GitHub Desktop + GitHub Web.

---

# 2. Flujo general del trabajo colaborativo

1. B y C crean **forks** del repo de A.  
2. B y C clonan sus propios forks en GitHub Desktop.  
3. B y C editan `grafo.ttl` en Protégé Desktop.  
4. B y C hacen commit y push desde GitHub Desktop a sus forks.  
5. B y C crean un **Pull Request** desde GitHub Web.  
6. Cuenta A revisa y hace **Merge** del Pull Request.  
7. Raspberry Pi actualiza el proyecto con `git pull` y regenera el índice.

---

# 3. Instrucciones para usuarios con GitHub Desktop (B y C)

## 3.1. Crear el fork desde GitHub Web

1. Ir a: `https://github.com/CuentaA/kg-llm`  
2. Haz clic en **Fork**.  
3. GitHub creará tu propio repositorio: `https://github.com/TuCuenta/kg-llm`.

---

## 3.2. Clonar el fork con GitHub Desktop

1. Abre **GitHub Desktop**.  
2. Menú: **File → Clone Repository**.  
3. Elige el fork que aparece bajo tu cuenta.  
4. Clóvalo en tu PC.

---

## 3.3. Editar la ontología en Protégé Desktop

1. Abre Protégé Desktop.  
2. File → Open.  
3. Selecciona `kg-llm/data/grafo.ttl`.  
4. Realiza los cambios.  
5. Guarda con  
   **File → Save**.

---

## 3.4. Hacer commit y push desde GitHub Desktop

1. Vuelve a GitHub Desktop.  
2. Verás los cambios listados (incluyendo `grafo.ttl`).  
3. Escribe un mensaje de commit:  
   _"Actualización de ontología desde Protégé"_  
4. Presiona **Commit to main** (o la rama donde estés).  
5. Presiona **Push origin**.

Ahora tu fork contiene los cambios.

---

## 3.5. Crear un Pull Request desde GitHub Web

1. Haz clic en **View on GitHub** desde GitHub Desktop **o** abre tu fork en el navegador.  
2. GitHub mostrará un aviso:  
   **“You have recent pushes… Compare & Pull Request”**  
3. Si no aparece:  
   - Ir a **Pull requests → New pull request**  
4. Configurar:  
   - **base repository:** `CuentaA/kg-llm`  
   - **base branch:** `main`  
   - **head repository:** tu fork  
   - **compare branch:** tu rama con cambios  
5. Clic en **Create Pull Request**.

Fin del proceso para B/C.  
Cuenta A ahora debe aprobar el PR.

---

# 4. Instrucciones para la persona dueña del repositorio (Cuenta A)

## 4.1. Revisar y aceptar Pull Requests

1. Ir al repo original: `https://github.com/CuentaA/kg-llm`.  
2. Abrir la pestaña **Pull Requests**.  
3. Seleccionar el PR enviado por B o C.  
4. Revisar los cambios (GitHub muestra el diff).  
5. Si todo está correcto:  
   - Clic en **Merge pull request**  
   - Clic en **Confirm merge**

El repositorio original queda actualizado.

---

# 5. Instrucciones para la Raspberry Pi (terminal)

La Raspberry está conectada al repo de **Cuenta A**, no a los forks.

Cada vez que Cuenta A haga Merge de un PR:

## 5.1. Actualizar el repositorio en Raspberry

```bash
cd /home/pi/kg-llm
git pull

## 5.2. Regenerar los índices del proyecto

```bash
source llm-env/bin/activate
python scripts/extract_entities.py
python scripts/build_index.py



