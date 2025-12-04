from rdflib import Graph, RDFS, RDF, Namespace
import json, yaml, os

# Cargar configuración
cfg = yaml.safe_load(open("/home/pi/Documents/kg-llm/config.yaml", encoding="utf-8"))

TTL = cfg["paths"]["ttl"]
OUT = cfg["paths"]["entities"]       # versión simple
EXP = cfg["paths"]["expanded"]       # versión expandida

# Namespace de tu ontología
FEST = Namespace("http://example.org/festividades#")

# Propiedades de anotación para texto
DESC_BREVE = FEST.descripcionBreve
DESC_ETNO = FEST.descripcionEtnografica
FUENTE_TXT = FEST.fuenteTexto


def extract_entities():
    g = Graph()
    g.parse(TTL, format="turtle")

    entities = {}

    for s in g.subjects():
        label = g.value(s, RDFS.label)
        if not label:
            continue  # solo entidades con label

        comment = g.value(s, RDFS.comment)

        # nuevas anotaciones textuales
        desc_breve = g.value(s, DESC_BREVE)
        desc_etno = g.value(s, DESC_ETNO)
        fuente_txt = g.value(s, FUENTE_TXT)

        types = [str(t) for t in g.objects(s, RDF.type)]

        # relaciones (para contexto estructural si luego lo quieres usar)
        relations = []
        for p, o in g.predicate_objects(s):
            if p in (RDFS.label, RDFS.comment, RDF.type,
                     DESC_BREVE, DESC_ETNO, FUENTE_TXT):
                continue
            relations.append({"property": str(p), "object": str(o)})

        # texto agregado para embeddings
        text_parts = [
            str(label),
            str(desc_breve) if desc_breve else "",
            str(desc_etno) if desc_etno else "",
            str(comment) if comment else "",
        ]
        full_text = " ".join(t for t in text_parts if t).strip()

        entities[str(s)] = {
            "uri": str(s),
            "label": str(label),
            "comment": str(comment) if comment else "",
            "descripcionBreve": str(desc_breve) if desc_breve else "",
            "descripcionEtnografica": str(desc_etno) if desc_etno else "",
            "fuenteTexto": str(fuente_txt) if fuente_txt else "",
            "types": types,
            "relations": relations,
            "text": full_text,  # <- este es el que usarás para embeddings
        }

    # versión simple: lo mínimo para el índice
    simple_list = [
        {
            "uri": e["uri"],
            "label": e["label"],
            "text": e["text"],  # para que build_index.py no tenga que recomponer nada
        }
        for e in entities.values()
    ]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    os.makedirs(os.path.dirname(EXP), exist_ok=True)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(simple_list, f, indent=2, ensure_ascii=False)

    with open(EXP, "w", encoding="utf-8") as f:
        json.dump(list(entities.values()), f, indent=2, ensure_ascii=False)

    print(f"Extraídas {len(entities)} entidades.")
    print(f"Guardado simple en: {OUT}")
    print(f"Guardado expandido en: {EXP}")


if __name__ == "__main__":
    extract_entities()
