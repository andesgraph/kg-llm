import json
import numpy as np
from sentence_transformers import SentenceTransformer
import yaml

cfg = yaml.safe_load(open("config.yaml"))

ENT = cfg["paths"]["expanded"]
OUT_VEC = cfg["paths"]["vectors"]

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# cargar entidades
entities = json.load(open(ENT, "r", encoding="utf-8"))

texts = []
ids = []

for e in entities:
    text = e["label"] + " " + e.get("comment", "")
    texts.append(text)
    ids.append(e["uri"])

# generar embeddings
vectors = model.encode(texts, convert_to_numpy=True)

# guardar correctamente
np.savez(OUT_VEC, vectors=vectors, ids=np.array(ids))

print("Índice generado con:", len(ids), "entidades.")
print("Guardado en:", OUT_VEC)
