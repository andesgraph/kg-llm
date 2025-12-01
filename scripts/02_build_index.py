import json
import yaml
import numpy as np
from llama_cpp import Llama

CFG = yaml.safe_load(open("/home/pi/Documents/kg-llm/config.yaml"))

ENTITIES_JSON = CFG["paths"]["entities"]
OUTPUT_INDEX  = CFG["paths"]["index"]
MODEL_PATH    = CFG["model"]["path"]
CTX           = CFG["model"]["ctx"]
THREADS       = CFG["model"]["threads"]

print("🔵 Cargando modelo GGUF para embeddings...")
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=CTX,
    n_threads=THREADS,
    embedding=True
)

def embed(text: str):
    """Devuelve un vector embedding usando llama.cpp, tolerando distintos formatos."""
    out = llm.embed(text)

    # Caso 1: dict con "data" (algunos builds recientes)
    if isinstance(out, dict) and "data" in out:
        emb = out["data"][0]["embedding"]

    # Caso 2: lista de dicts con "embedding"
    elif isinstance(out, list) and len(out) > 0 and isinstance(out[0], dict) and "embedding" in out[0]:
        emb = out[0]["embedding"]

    # Caso 3: lista de listas/floats (tu caso: [[...], [...], ...])
    elif isinstance(out, list) and len(out) > 0 and isinstance(out[0], (list, tuple)):
        emb = out[0]

    else:
        raise ValueError(f"Formato inesperado de salida de embed(): {type(out)}")

    return np.array(emb, dtype=np.float32)



print("🔵 Cargando entidades...")
entities = json.load(open(ENTITIES_JSON, encoding="utf-8"))

ids = []
labels = []
vecs = []

print(f"🔵 Generando embeddings para {len(entities)} entidades...")

for idx, ent in enumerate(entities):
    text = (ent.get("text") or ent.get("label") or "").strip()
    if not text:
        continue

    label = ent.get("label", f"entidad_{idx}")
    print(f"   → {label}")
    v = embed(text)

    ids.append(idx)          # usamos índice numérico como ID
    labels.append(label)
    vecs.append(v)

vecs = np.stack(vecs, axis=0)

# Guardar índice como NPZ
np.savez(OUTPUT_INDEX, ids=np.array(ids), labels=np.array(labels), vecs=vecs)

print(f"\n✅ Índice creado en: {OUTPUT_INDEX}")
print(f"📦 Vectores: {vecs.shape}")
