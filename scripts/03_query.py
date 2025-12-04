#!/usr/bin/env python3
# 03_query.py
#
# Consulta el índice de embeddings y genera una respuesta
# usando el modelo local (.gguf) definido en config.yaml.
#
# Uso:
#   python3 scripts/03_query.py "¿Quién es el Ukuku?"

import json
import yaml
import numpy as np
import sys
import warnings

from sentence_transformers import SentenceTransformer
import llama_cpp
from llama_cpp import Llama

# Silenciar algunos warnings molestos
warnings.filterwarnings("ignore", category=UserWarning)

# Parche: desactivar destructor problemático de Llama para que
# no aparezca el traceback "NoneType object is not callable" al salir.
def _safe_del(self):
    # No hacemos nada al destruir el modelo.
    # La memoria se libera al terminar el proceso.
    pass

llama_cpp.Llama.__del__ = _safe_del

# ============================
# 1. Cargar configuración
# ============================

CFG = yaml.safe_load(open("config.yaml", encoding="utf-8"))

TTL_FILE    = CFG["paths"]["ttl"]              # no se usa aún, pero queda para futuro
ENT_FILE    = CFG["paths"]["entities"]         # index/entities.json (simple)
INDEX_FILE  = CFG["paths"]["index"]            # index/index.npz

MODEL_PATH    = CFG["model"]["path"]
MODEL_CTX     = CFG["model"].get("ctx", 2048)
MODEL_THREADS = CFG["model"].get("threads", 4)

TOP_K = 5  # número de entidades a recuperar para el contexto


# ============================
# 2. Utilidades
# ============================

def load_index(path_npz):
    """
    Carga embeddings y URIs desde el archivo .npz.
    Soporta diferentes nombres de clave ('vectors'/'embeddings', 'ids'/'uris').
    """
    data = np.load(path_npz)
    keys = list(data.files)

    # vectores
    if "vectors" in keys:
        vectors = data["vectors"]
    elif "embeddings" in keys:
        vectors = data["embeddings"]
    else:
        raise KeyError(
            f"No se encontraron claves 'vectors' ni 'embeddings' en {path_npz}. "
            f"Claves disponibles: {keys}"
        )

    # identificadores
    if "ids" in keys:
        ids = data["ids"]
    elif "uris" in keys:
        ids = data["uris"]
    else:
        raise KeyError(
            f"No se encontraron claves 'ids' ni 'uris' en {path_npz}. "
            f"Claves disponibles: {keys}"
        )

    return vectors, ids.tolist()


def normalize(vectors: np.ndarray) -> np.ndarray:
    """Normaliza cada fila de una matriz de vectores (para usar producto punto como coseno)."""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    return vectors / norms


# ============================
# 3. Carga de datos y modelos
# ============================

print("📘 Cargando entidades...")
entities = json.load(open(ENT_FILE, encoding="utf-8"))
uri_to_entity = {e["uri"]: e for e in entities}   # entities.json viene de 01_extract_entities.py

print("📦 Cargando índice de embeddings...")
VEC, IDS = load_index(INDEX_FILE)
VEC = normalize(VEC)

print("🧠 Cargando modelo de embeddings (SentenceTransformer)...")
emb_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

print("🤖 Cargando modelo LLM local...")
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=MODEL_CTX,
    n_threads=MODEL_THREADS,
    verbose=False,         # para que no imprima métricas de tiempo
)


# ============================
# 4. Recuperación semántica
# ============================

def retrieve(query: str, top_k: int = TOP_K):
    """
    Devuelve las top_k entidades más cercanas a la consulta,
    con score de similitud y metadatos.
    """
    q_vec = emb_model.encode(query, convert_to_numpy=True)
    q_vec = q_vec / (np.linalg.norm(q_vec) + 1e-9)

    scores = VEC @ q_vec  # coseno porque todo está normalizado
    idxs = np.argsort(-scores)[:top_k]

    results = []
    for i in idxs:
        uri = IDS[i]
        score = float(scores[i])
        ent = uri_to_entity.get(uri, {"uri": uri, "label": uri, "text": ""})
        results.append(
            {
                "uri": uri,
                "score": score,
                "label": ent.get("label", uri),
                "text": ent.get("text", ""),
            }
        )
    return results


def build_context(results):
    """
    Construye el texto de contexto a partir de las entidades recuperadas.
    - Elimina duplicados por URI.
    - Limita el número de líneas para evitar repetición.
    """
    seen = set()
    lines = []

    for r in results:
        if r["uri"] in seen:
            continue
        seen.add(r["uri"])

        label = r["label"]
        text = r.get("text", "")
        line = f"- {label}: {text}"
        lines.append(line)

    # limitar a máximo 5 entradas en el contexto
    return "\n".join(lines[:5])


# ============================
# 5. Llamada al LLM local
# ============================

def ask_llm(query: str, context: str) -> str:
    """
    Llama al modelo local con un prompt estilo RAG.
    Se fuerza a:
      - no repetir frases
      - responder breve
    """
    prompt = (
        "Eres un asistente experto en festividades andinas, personajes rituales "
        "y patrimonio cultural.\n"
        "Responde en español, con precisión y SIN repetir frases.\n"
        "Si el contexto es redundante, sintetiza la información.\n\n"
        "Contexto:\n"
        f"{context}\n\n"
        "Pregunta:\n"
        f"{query}\n\n"
        "Respuesta (máximo 5 líneas, clara y sin repeticiones):\n"
    )

    out = llm(
        prompt,
        max_tokens=256,
        temperature=0.25,
        top_k=40,
        top_p=0.9,
        repeat_penalty=1.3,  # clave para evitar repeticiones
        stop=["\n\n", "</s>"],
    )

    if isinstance(out, dict) and "choices" in out:
        return out["choices"][0]["text"].strip()

    return str(out).strip()


# ============================
# 6. Entrada principal
# ============================

def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("❓ Escribe tu pregunta (Ctrl+C para salir): ").strip()

    if not query:
        print("No se ingresó ninguna pregunta.")
        return

    print("\n🔎 Recuperando entidades relevantes...")
    results = retrieve(query, TOP_K)

    for r in results:
        print(f"  • {r['label']}  (score={r['score']:.3f})")

    context = build_context(results)

    print("\n🧵 Contexto pasado al modelo:")
    print(context)
    print("\n💬 Generando respuesta con el LLM local...\n")

    answer = ask_llm(query, context)
    print("🡆 Respuesta:")
    print(answer)


if __name__ == "__main__":
    main()
