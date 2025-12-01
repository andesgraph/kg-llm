#!/bin/bash
python3 scripts/01_extract_entities.py
python3 scripts/02_build_index.py
python3 scripts/03_query.py
