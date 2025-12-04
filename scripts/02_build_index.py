import json
import numpy as np
from sentence_transformers import SentenceTransformer
import yaml
import os

cfg = yaml.safe_load(open("/home/pi/Documents/kg-llm/config.yaml", encoding="utf-8"))
ENT_FILE = cfg["paths"]["entities"]
OUT_VEC = cfg["paths"]["vectors"]

def build_index():
    print("Cargando modelo...")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    print("Leyendo entidades...")
    entities = json.load(open(ENT_FILE, "r", encoding="utf-8"))

    uris = []
    vectors = []

    for ent in entities:
        text = ent.get("text", ent["label"])  # fallback si algo falta
        embedding = model.encode(text, convert_to_numpy=True)
        
        uris.append(ent["uri"])
        vectors.append(embedding)

    vectors = np.array(vectors)

    os.makedirs(os.path.dirname(OUT_VEC), exist_ok=True)
    np.savez(OUT_VEC, uris=uris, vectors=vectors)

    print(f"Índice generado con {len(uris)} entidades.")
    print(f"Guardado en {OUT_VEC}")

if __name__ == "__main__":
    build_index()
