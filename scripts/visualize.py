#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
from rdflib import Graph
import networkx as nx

def load_ttl_to_nx(ttl_path: str) -> nx.MultiDiGraph:
    rdf = Graph()
    rdf.parse(ttl_path, format="turtle")

    G = nx.MultiDiGraph()
    for s, p, o in rdf:
        G.add_node(str(s))
        G.add_node(str(o))
        G.add_edge(str(s), str(o), predicate=str(p))
    return G

def short(uri: str) -> str:
    if "#" in uri:
        return uri.split("#")[-1]
    return uri.rsplit("/", 1)[-1]

def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)

def main():
    ap = argparse.ArgumentParser(description="TTL → NetworkX (stats + PNG simple)")
    ap.add_argument("--ttl", default="data/grafo.ttl", help="Ruta al .ttl")
    ap.add_argument("--png", default="data/grafo_nx.png", help="Salida PNG")
    ap.add_argument("--top", type=int, default=15, help="Top N nodos por grado")
    ap.add_argument("--no-png", action="store_true", help="No generar imagen")
    args = ap.parse_args()

    print("📁 Working directory:", os.getcwd())

    # Si pasas rutas relativas, esto ayuda a detectar el problema
    if not os.path.exists(args.ttl):
        print(f"❌ No encuentro el TTL en: {args.ttl}")
        print("👉 Prueba con ruta absoluta, por ejemplo:")
        print(r'   --ttl "C:\Users\jvera\Documents\kg-llm\data\grafo.ttl"')
        return

    G = load_ttl_to_nx(args.ttl)

    print(f"✅ TTL cargado: {args.ttl}")
    print(f"✅ Nodos:   {G.number_of_nodes()}")
    print(f"✅ Aristas: {G.number_of_edges()}")

    comps = list(nx.weakly_connected_components(G))
    print(f"✅ Componentes (weak): {len(comps)}")
    if comps:
        print(f"✅ Mayor componente: {max(len(c) for c in comps)} nodos")

    deg = dict(G.degree())
    top = sorted(deg.items(), key=lambda x: x[1], reverse=True)[:args.top]
    print("\nTop nodos por grado:")
    for uri, d in top:
        print(f"{d:>4}  {short(uri)}")

    if args.no_png:
        return

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("⚠️  Falta matplotlib. Instala con: pip install matplotlib")
        return

    largest_comp = max(nx.weakly_connected_components(G), key=len)
    H = G.subgraph(largest_comp).copy()
    print(f"🧩 Dibujando mayor componente: {H.number_of_nodes()} nodos")

    pos = nx.kamada_kawai_layout(H)

    plt.figure(figsize=(14, 14))
    nx.draw_networkx_nodes(H, pos, node_size=20, alpha=0.7)
    nx.draw_networkx_edges(H, pos, width=0.3, alpha=0.3)

    labels = {n: short(n) for n, _ in top if n in H}
    nx.draw_networkx_labels(H, pos, labels=labels, font_size=9)

    plt.axis("off")
    plt.tight_layout()

    # ✅ crear carpeta destino si no existe
    ensure_parent_dir(args.png)

    plt.savefig(args.png, dpi=200)
    print(f"🖼️  PNG guardado en: {args.png}")

if __name__ == "__main__":
    main()