#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path
from collections import defaultdict

import networkx as nx
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD

from pyvis.network import Network


# -------------------------
# Utilidades
# -------------------------

def ensure_parent_dir(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)

def short(uri: str) -> str:
    if "#" in uri:
        return uri.split("#")[-1]
    return uri.rsplit("/", 1)[-1]

def is_uri(x) -> bool:
    return isinstance(x, URIRef)

def is_lit(x) -> bool:
    return isinstance(x, Literal)

def looks_technical_pred(pu: str) -> bool:
    # Permitimos RDF.type y RDFS.subClassOf a propósito (los queremos ver)
    if pu in {str(RDF.type), str(RDFS.subClassOf)}:
        return False
    return (
        pu.startswith(str(OWL)) or
        pu.startswith(str(RDFS)) or
        pu.startswith(str(RDF)) or
        pu.startswith(str(XSD))
    )

# -------------------------
# Clasificación (para color y forma)
# -------------------------

def detect_kinds(rdf: Graph):
    """
    Devuelve sets de URIs (str):
      - classes: owl:Class
      - objprops: owl:ObjectProperty
      - annprops: owl:AnnotationProperty
      - individuals: owl:NamedIndividual (si no están tipados, igual pueden aparecer como nodos)
    """
    classes = set(str(s) for s, _, _ in rdf.triples((None, RDF.type, OWL.Class)) if is_uri(s))
    objprops = set(str(s) for s, _, _ in rdf.triples((None, RDF.type, OWL.ObjectProperty)) if is_uri(s))
    annprops = set(str(s) for s, _, _ in rdf.triples((None, RDF.type, OWL.AnnotationProperty)) if is_uri(s))
    individuals = set(str(s) for s, _, _ in rdf.triples((None, RDF.type, OWL.NamedIndividual)) if is_uri(s))
    return classes, objprops, annprops, individuals

def load_labels(rdf: Graph):
    labels = {}
    for s, _, o in rdf.triples((None, RDFS.label, None)):
        if is_uri(s) and (is_lit(o)):
            labels[str(s)] = str(o)
    return labels

def bucket_for_node(u: str, classes, objprops, annprops, individuals) -> str:
    if u in classes:
        return "Clase"
    if u in objprops:
        return "PropiedadObjeto"
    if u in annprops:
        return "PropiedadAnotacion"
    if u in individuals:
        return "Individuo"
    # nodos no tipados explícitamente
    return "Otro"

# -------------------------
# Cargar TTL -> grafo para visualizar
# -------------------------

def load_graph_for_visualization(
    ttl_path: str,
    mode: str = "full",                 # full | semantic
    allowed_pred_localnames: set | None = None,
    include_literals: bool = False,     # si True, crea nodos para literales (suele ensuciar)
):
    rdf = Graph()
    rdf.parse(ttl_path, format="turtle")

    classes, objprops, annprops, individuals = detect_kinds(rdf)
    labels = load_labels(rdf)

    # tipos rdf:type (para hover / análisis)
    types = defaultdict(set)
    for s, _, o in rdf.triples((None, RDF.type, None)):
        if is_uri(s) and is_uri(o):
            types[str(s)].add(str(o))

    G = nx.DiGraph()

    # Reglas de inclusión de triples
    for s, p, o in rdf:
        if not is_uri(s):
            continue

        su, pu = str(s), str(p)

        # MODO semantic: solo algunas relaciones entre URIs
        if mode == "semantic":
            if allowed_pred_localnames is None:
                continue
            # solo edges s->o donde o es URI
            if not is_uri(o):
                continue
            if short(pu) not in allowed_pred_localnames:
                continue
            # omitimos predicados "técnicos" en semantic (excepto type/subClassOf si los incluyes en allowed)
            if looks_technical_pred(pu):
                continue

            ou = str(o)
            G.add_node(su)
            G.add_node(ou)
            G.add_edge(su, ou, predicate=short(pu))
            continue

        # MODO full: queremos ver TODO lo estructural
        # - incluimos rdf:type, rdfs:subClassOf, tus object properties
        # - omitimos solo predicados MUY técnicos (si quieres verlos, puedes desactivar)
        if looks_technical_pred(pu):
            continue

        # Si es literal:
        if is_lit(o):
            if not include_literals:
                continue
            # Creamos un nodo para literal (corto), útil solo si quieres ver descripciones como nodos
            ou = f"lit:{str(o)[:80]}"
            G.add_node(ou)
            G.add_edge(su, ou, predicate=short(pu))
            continue

        if not is_uri(o):
            continue

        ou = str(o)
        G.add_node(su)
        G.add_node(ou)
        G.add_edge(su, ou, predicate=short(pu))

    meta = {
        "classes": classes,
        "objprops": objprops,
        "annprops": annprops,
        "individuals": individuals,
        "labels": labels,
        "types": types,
    }
    return G, meta

# -------------------------
# HTML interactivo con PyVis
# -------------------------

def nx_to_pyvis_html(
    G: nx.DiGraph,
    meta: dict,
    out_html: str,
    physics: str = "barnesHut",
    max_nodes: int = 1200,
    top_labels: int = 60,
    show_all_labels_if_leq: int = 300,
    font_size: int = 10,
    edge_font_size: int = 8,
    largest_component: bool = False,
):
    ensure_parent_dir(out_html)

    if G.number_of_nodes() == 0:
        net = Network(height="900px", width="100%", directed=True, notebook=False, cdn_resources="in_line")
        html = net.generate_html()
        with open(out_html, "w", encoding="utf-8") as f:
            f.write(html)
        return 0, 0

    H = G

    # Si lo pides, recorta a mayor componente (útil cuando se fragmenta demasiado)
    if largest_component:
        comps = list(nx.weakly_connected_components(H))
        if comps:
            H = H.subgraph(max(comps, key=len)).copy()

    # Si es enorme, recorta por grado (para que el navegador no muera)
    if H.number_of_nodes() > max_nodes:
        deg = dict(H.degree())
        keep_nodes = {n for n, _ in sorted(deg.items(), key=lambda x: x[1], reverse=True)[:max_nodes]}
        H = H.subgraph(keep_nodes).copy()

    # Etiquetas: todas si es pequeño; si no, solo top por centralidad
    show_all = H.number_of_nodes() <= show_all_labels_if_leq
    try:
        cent = nx.betweenness_centrality(H)
        top = sorted(cent.items(), key=lambda x: x[1], reverse=True)[:top_labels]
    except Exception:
        deg = dict(H.degree())
        top = sorted(deg.items(), key=lambda x: x[1], reverse=True)[:top_labels]

    label_nodes = {n for n, _ in top}

    classes = meta["classes"]
    objprops = meta["objprops"]
    annprops = meta["annprops"]
    individuals = meta["individuals"]
    labels = meta["labels"]
    types = meta["types"]

    # estilo por tipo de nodo
    bucket_color = {
        "Clase": "#e67e22",
        "PropiedadObjeto": "#2980b9",
        "PropiedadAnotacion": "#16a085",
        "Individuo": "#8e44ad",
        "Otro": "#7f8c8d",
    }
    bucket_shape = {
        "Clase": "triangle",
        "PropiedadObjeto": "square",
        "PropiedadAnotacion": "square",
        "Individuo": "dot",
        "Otro": "dot",
    }

    net = Network(height="900px", width="100%", directed=True, notebook=False, cdn_resources="in_line")

    if physics.lower() == "repulsion":
        net.repulsion(node_distance=160, spring_length=140)
    elif physics.lower() == "forceatlas2":
        net.force_atlas_2based(gravity=-50, central_gravity=0.01, spring_length=120, spring_strength=0.08)
    else:
        net.barnes_hut()

    # JSON limpio y válido (pyvis lo parsea con json.loads)
    net.set_options(f"""
    {{
      "interaction": {{
        "hover": true,
        "navigationButtons": true,
        "multiselect": true,
        "tooltipDelay": 80
      }},
      "nodes": {{
        "borderWidth": 1,
        "font": {{
          "size": {int(font_size)},
          "strokeWidth": 2,
          "strokeColor": "#ffffff"
        }}
      }},
      "edges": {{
        "arrows": {{ "to": {{ "enabled": true, "scaleFactor": 0.6 }} }},
        "smooth": {{ "type": "dynamic" }},
        "font": {{ "size": {int(edge_font_size)}, "align": "middle" }}
      }},
      "physics": {{ "enabled": true }}
    }}
    """)

    degH = dict(H.degree())

    def pretty_label(n: str) -> str:
        # Preferir rdfs:label si existe
        if n in labels:
            return labels[n]
        return short(n)

    def hover_html(n: str) -> str:
        b = bucket_for_node(n, classes, objprops, annprops, individuals)
        tset = sorted({short(t) for t in types.get(n, set())})
        return (
            f"<b>{pretty_label(n)}</b><br>"
            f"<code>{n}</code><br><br>"
            f"<b>Tipo visual:</b> {b}<br>"
            f"<b>rdf:type:</b> {', '.join(tset) if tset else '—'}<br>"
            f"<b>Grado:</b> {degH.get(n, 0)}"
        )

    # Nodos
    for n in H.nodes():
        b = bucket_for_node(n, classes, objprops, annprops, individuals)
        color = bucket_color.get(b, bucket_color["Otro"])
        shape = bucket_shape.get(b, "dot")
        size = max(10, min(60, 10 + degH.get(n, 0) * 1.8))

        label = pretty_label(n) if (show_all or n in label_nodes) else ""

        net.add_node(
            n,
            label=label,
            title=hover_html(n),
            color=color,
            size=size,
            shape=shape,
            group=b
        )

    # Aristas
    for u, v, data in H.edges(data=True):
        pred = data.get("predicate", "")
        # Si venimos de modo FULL, predicate ya es localname; si no, lo calculamos
        if not pred:
            pred = data.get("predicate", "")
        net.add_edge(u, v, title=pred, label=pred)

    html = net.generate_html()
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)

    return H.number_of_nodes(), H.number_of_edges()

# -------------------------
# main
# -------------------------

def main():
    ap = argparse.ArgumentParser(description="TTL -> HTML interactivo (PyVis) mostrando clases/propiedades/individuos")
    ap.add_argument("--ttl", default="data/grafo.ttl", help="Ruta al .ttl")
    ap.add_argument("--html", default="data/grafo_interactivo.html", help="Salida HTML")
    ap.add_argument("--mode", default="full", choices=["full", "semantic"], help="full=todo, semantic=solo relaciones clave")
    ap.add_argument("--physics", default="barnesHut", choices=["barnesHut", "repulsion", "forceatlas2"], help="Layout")
    ap.add_argument("--max-nodes", type=int, default=1200, help="Límite de nodos en HTML (performance)")
    ap.add_argument("--top-labels", type=int, default=60, help="Top nodos a etiquetar si el grafo es grande")
    ap.add_argument("--show-all-labels-if-leq", type=int, default=300, help="Si nodos <= N, etiqueta todo")
    ap.add_argument("--font-size", type=int, default=10, help="Tamaño de etiquetas de nodos")
    ap.add_argument("--edge-font-size", type=int, default=8, help="Tamaño de etiquetas de aristas")
    ap.add_argument("--largest-component", action="store_true", help="Dibuja solo la mayor componente")
    ap.add_argument("--include-literals", action="store_true", help="Incluye literales como nodos (ensucia, úsalo con cuidado)")
    args = ap.parse_args()

    allowed_pred_localnames = {
        # relaciones “de dominio” (las tuyas)
        "documentaA",
        "capturadoEnSegmento",
        "tieneRecursoMedial",
        "realizaDanza",
        "seCelebraEn", "SeCelebraEn",
        "ocurreDurante",
        "estaEnLugar",
        "perteneceAComparsa",
        "usaObjetoRitual",
        "representaEntidad",
        "narradoPor",
        "relacionadoCon",
        "muestraPersonaje",
        "registradoPor",
        "ubicadoEn", "UbicadoEn",
        # estructura ontológica (si quieres verlas también en semantic)
        "type",          # rdf:type -> "type" como localname
        "subClassOf",    # rdfs:subClassOf
    }

    G, meta = load_graph_for_visualization(
        args.ttl,
        mode=args.mode,
        allowed_pred_localnames=allowed_pred_localnames,
        include_literals=args.include_literals
    )

    print(f"✅ TTL: {args.ttl}")
    print(f"✅ Nodos:  {G.number_of_nodes()}")
    print(f"✅ Aristas:{G.number_of_edges()}")
    print(f"✅ Modo:   {args.mode}")

    n_nodes, n_edges = nx_to_pyvis_html(
        G, meta, args.html,
        physics=args.physics,
        max_nodes=args.max_nodes,
        top_labels=args.top_labels,
        show_all_labels_if_leq=args.show_all_labels_if_leq,
        font_size=args.font_size,
        edge_font_size=args.edge_font_size,
        largest_component=args.largest_component
    )

    print(f"🧠 HTML interactivo creado: {args.html}")
    print(f"   Renderizado con {n_nodes} nodos y {n_edges} aristas")
    print("   Abre el HTML con doble click (Chrome/Firefox).")

if __name__ == "__main__":
    main()
