from rdflib import Graph, RDFS, RDF
import json, yaml, os

cfg = yaml.safe_load(open("/home/pi/Documents/kg-llm/config.yaml"))
TTL = cfg["paths"]["ttl"]
OUT = cfg["paths"]["entities"]
EXP = cfg["paths"]["expanded"]

def extract_entities():
    g = Graph()
    g.parse(TTL, format="turtle")

    entities = {}
    
    for s in g.subjects():
        label = g.value(s, RDFS.label)
        if not label:
            continue  # solo entidades con label
        
        comment = g.value(s, RDFS.comment)
        types = [str(t) for t in g.objects(s, RDF.type)]
        
        relations = []
        for p, o in g.predicate_objects(s):
            if p == RDFS.label or p == RDFS.comment or p == RDF.type:
                continue
            relations.append({"property": str(p), "object": str(o)})

        entities[str(s)] = {
            "uri": str(s),
            "label": str(label),
            "comment": str(comment) if comment else "",
            "types": types,
            "relations": relations
        }

    # versión simple
    simple_list = [{"uri": e["uri"], "label": e["label"]} for e in entities.values()]
    json.dump(simple_list, open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    # versión expandida
    json.dump(list(entities.values()), open(EXP, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    print(f"Extraídas {len(entities)} entidades.")
    print(f"Guardado simple en: {OUT}")
    print(f"Guardado expandido en: {EXP}")

if __name__ == "__main__":
    extract_entities()
