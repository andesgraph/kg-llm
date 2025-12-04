#!/usr/bin/env python3
# 03_query.py
#
# Consulta el índice de embeddings y genera una respuesta
# usando el modelo local (.gguf) definido en config.yaml.

import json
import yaml
import numpy as np
import sys
from sentence_transformers import SentenceTransformer
from llama_cpp import Llama

# ============================
# Cargar configuración
# ============================

CFG = yaml.safe_load(open("config.yaml", encoding="utf-8"))

TTL_FILE    = CFG["paths"]["ttl"]            # no lo usamos aún, pero queda para futuro
ENT_FILE    = CFG["paths"]["entities"]       # entities.json (simple)
INDEX_FILE  = CFG["paths"]["index"]          # index.npz

MODEL_PATH  = CFG["model"]["path"]
MODEL_CTX   = CFG["model"].get("ctx", 2048)
MODEL_THREADS = CFG["model"].get("threads", 4)

TOP_K = 5  # número de entidades a recuperar


# ============================
# Utilidades
# ============================

def load_index(path_npz):
    """Carga embeddings y URIs desde el archivo .npz, siendo robusto a nombres de claves."""
    data = np.load(path_npz)

    files = list(data.files)

    # vectores
    if "vectors" in files:
        vectors = data["vectors"]
    elif "embeddings" in files:
        vectors = data["embeddings"]
    else:
        raise KeyError(f"No se encontraron claves 'vectors' ni 'embeddings' en {path_npz}. Claves: {files}")

    # identificadores
    if "ids" in files:
        ids = data["ids"]
    elif "uris" in files:
        ids = data["uris"]
    else:
        raise KeyError(f"No se encontraron claves 'ids' ni 'uris' en {path_npz}. Claves: {files}")

    return vectors, ids.tolist()


def normalize(vectors: np.ndarray) -> np.ndarray:
    """Normaliza filas de una matriz de vectores."""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    return vectors / norms


# ============================
# Carga de recursos
# ============================

print("📘 Cargando entidades...")
entities = json.load(open(ENT_FILE, encoding="utf-8"))
uri_to_entity = {e["uri"]: e for e in entities}

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
)

# ============================
# Bucle de consulta
# ============================

def retrieve(query: str, top_k: int = TOP_K):
    """Devuelve las top_k entidades más cercanas a la consulta."""
    q_vec = emb_model.encode(query, convert_to_numpy=True)
    q_vec = q_vec / (np.linalg.norm(q_vec) + 1e-9)

    scores = VEC @ q_vec  # producto punto con vectores normalizados
    idxs = np.argsort(-scores)[:top_k]

    results = []
    for i in idxs:
        uri = IDS[i]
        score = float(scores[i])
        ent = uri_to_entity.get(uri, {"uri": uri, "label": uri, "text": ""})
        results.append({"uri": uri, "score": score, **ent})
    return results


def build_context(results):
    """Construye un texto de contexto para el LLM usando las entidades recuperadas."""
    lines = []
    for r in results:
        label = r.get("label", r["uri"])
        text = r.get("text") or r.get("comment", "")
        line = f"- {label} ({r['uri']}): {text}"
        lines.append(line)
    return "\n".join(lines)


def ask_llm(query: str, context: str) -> str:
    """Llama al modelo local con un prompt simple de RAG."""
    prompt = (
        "Eres un asistente que responde sobre festividades andinas, personajes rituales "
        "y patrimonio cultural. Usa SOLO la información del contexto cuando sea posible.\n\n"
        f"Contexto:\n{context}\n\n"
        f"Pregunta: {query}\n\n"
        "Respuesta (en español, clara y concisa):\n"
    )

    out = llm(
        prompt,
        max_tokens=512,
        temperature=0.3,
        top_p=0.95,
        stop=["</s>"],
    )
    # llama_cpp devuelve un dict si se llama con argumentos nombrados; pero con esta
    # interfaz devuelve directamente el texto generado.
    if isinstance(out, dict) and "choices" in out:
        return out["choices"][0]["text"].strip()
    return str(out).strip()


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
        print(f"  • {r.get('label', r['uri'])}  (score={r['score']:.3f})")

    context = build_context(results)

    print("\n🧵 Contexto pasado al modelo:")
    print(context)
    print("\n💬 Generando respuesta con el LLM local...\n")

    answer = ask_llm(query, context)
    print("🡆 Respuesta:")
    print(answer)


if __name__ == "__main__":
    main()
