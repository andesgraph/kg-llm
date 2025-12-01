import yaml
import json
import numpy as np
from rdflib import Graph
from llama_cpp import Llama

# Cargar configuración
CFG = yaml.safe_load(open("/home/pi/Documents/kg-llm/config.yaml"))

TTL_PATH      = CFG["paths"]["ttl"]
ENTITIES_JSON = CFG["paths"]["entities"]
INDEX_FILE    = CFG["paths"]["index"]

MODEL_PATH = CFG["model"]["path"]
CTX        = CFG["model"]["ctx"]
THREADS    = CFG["model"]["threads"]
TOP_K      = 5  # puedes ajustar

print("🔵 Cargando grafo RDF...")
g = Graph()
g.parse(TTL_PATH, format="turtle")

print("🔵 Cargando entidades...")
entities_list = json.load(open(ENTITIES_JSON, encoding="utf-8"))

# Usamos el índice (0,1,2,…) como ID interno
entities = {i: e for i, e in enumerate(entities_list)}

print("🔵 Cargando índice de embeddings...")
data  = np.load(INDEX_FILE, allow_pickle=True)
IDS   = data["ids"]      # índices numéricos
LABELS= data["labels"]
VECS  = data["vecs"]

print("🔵 Cargando modelo LLM...")
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=CTX,
    n_threads=THREADS,
    embedding=True
)

def embed(text: str):
    """Devuelve vector embedding usando llama.cpp, tolerando distintos formatos."""
    out = llm.embed(text)

    # Caso 1: dict con "data"
    if isinstance(out, dict) and "data" in out:
        emb = out["data"][0]["embedding"]

    # Caso 2: lista de dicts con "embedding"
    elif isinstance(out, list) and len(out) > 0 and isinstance(out[0], dict) and "embedding" in out[0]:
        emb = out[0]["embedding"]

    # Caso 3: lista de listas/floats
    elif isinstance(out, list) and len(out) > 0 and isinstance(out[0], (list, tuple)):
        emb = out[0]

    else:
        raise ValueError(f"Formato inesperado de salida de embed(): {type(out)}")

    return np.array(emb, dtype=np.float32)

def cosine_sim(qv, M):
    """Similitud coseno entre un vector qv y una matriz M (cada fila es un vector)."""
    qv = qv / np.linalg.norm(qv)
    M_n = M / np.linalg.norm(M, axis=1, keepdims=True)
    return M_n @ qv

def retrieve_entities(question: str, k: int = TOP_K):
    qv = embed(question)
    sims = cosine_sim(qv, VECS)
    idx = np.argsort(-sims)[:k]
    results = []
    for i in idx:
        eid = int(IDS[i])         # índice numérico
        lab = str(LABELS[i])
        sim = float(sims[i])
        results.append((eid, lab, sim))
    return results

def build_context(eids):
    """Construir contexto textual simple para el LLM."""
    snippets = []
    for eid in eids:
        ent = entities.get(eid)
        if not ent:
            continue
        label = ent.get("label", f"entidad_{eid}")
        desc  = ent.get("description", "")
        text  = ent.get("text", "")
        snippet = f"[{label}]\n{desc}\n{text}"
        snippets.append(snippet.strip())
    return "\n\n".join(snippets)

NO_INFO = "No encuentro suficiente información sobre esa entidad en el grafo."

def answer(question: str):
    hits = retrieve_entities(question)
    eids = [h[0] for h in hits]
    context = build_context(eids).strip()

    print("\n--- ENTIDADES RELEVANTES ---")
    if not hits:
        print("(ninguna)")
    else:
        for eid, lab, sim in hits:
            print(f"{lab} (idx={eid})  sim={sim:.3f}")

    # Regla 1: si NO hay contexto, no usamos el LLM
    if not context:
        print("\n--- RESPUESTA ---")
        print(NO_INFO)
        return

    # Regla 2: si el contexto es muy pobre (por ejemplo < 80 caracteres),
    # asumimos que el grafo no tiene info suficiente para describir nada.
    if len(context) < 80:
        print("\n--- RESPUESTA ---")
        print(NO_INFO)
        return

    prompt = f"""
Eres un asistente que responde exclusivamente con la información del CONTEXTO.

CONTEXTO:
{context}

REGLAS IMPORTANTES:
1. No inventes información.
2. Si la entidad o el dato NO aparece en el CONTEXTO, responde literalmente:
   "No encuentro suficiente información sobre esa entidad en el grafo."
3. No uses conocimientos externos.
4. Responde en español, de manera clara y breve.

PREGUNTA:
{question}

RESPUESTA:
""".strip()

    out = llm(
        prompt,
        max_tokens=120,
        temperature=0.1,
        top_p=0.9,
        repeat_penalty=1.3,
    )

    raw = out["choices"][0]["text"].strip()

    # Si el modelo menciona la frase de NO_INFO, nos quedamos SOLO con eso
    if NO_INFO in raw:
        answer_text = NO_INFO
    else:
        # Si no, nos quedamos solo con la primera línea para evitar divagues largos
        answer_text = raw.split("\n")[0].strip()

    print("\n--- RESPUESTA ---")
    print(answer_text)


if __name__ == "__main__":
    try:
        while True:
            q = input("\nPregunta> ").strip()
            if not q:
                continue
            if q.lower() in {"salir", "exit", "quit"}:
                break
            answer(q)
    except KeyboardInterrupt:
        pass
