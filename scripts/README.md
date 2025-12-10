# Guía de anotación en Protégé para kg-llm

Este documento explica cómo anotar clases, individuos y recursos mediales en Protégé Desktop para que el pipeline de kg-llm pueda extraer buen texto para embeddings y recuperación semántica.

El script `01_extract_entities.py` lee el archivo `grafo.ttl` y, para cada entidad con `rdfs:label`, construye un campo de texto combinando:

- `rdfs:label`
- `:descripcionBreve`
- `:descripcionEtnografica`
- `rdfs:comment` (si existe)

Ese texto pasa luego a `02_build_index.py` para generar embeddings.

---

## 1. Propiedades de texto usadas por el RAG

La ontología define tres propiedades de anotación principales:

- **descripcionBreve** — definición corta (1–2 frases).
- **descripcionEtnografica** — descripción ampliada (3–6 frases).
- **fuenteTexto** — referencia o procedencia del texto.

### Ejemplo en TTL

```ttl
:PersonajeUkuku
    rdfs:label "Personaje Ukuku"@es ;
    :descripcionBreve "Figura enmascarada que representa al Ukuku en festividades andinas."@es ;
    :descripcionEtnografica "Combina rasgos animales y humanos; suele actuar como guardián, mediador y disciplinador..."@es ;
    :fuenteTexto "Notas de campo 2023."@es .
```

El campo `text` concatenará automáticamente estas descripciones.

---

## 2. Cómo anotar en Protégé

### 2.1. Verificar propiedades de anotación

En Protégé Desktop:

1. Abrir **Entities**.
2. Panel izquierdo → **Annotation properties**.
3. Confirmar que existen:
   - `descripcionBreve`
   - `descripcionEtnografica`
   - `fuenteTexto`

Si falta alguna:

- `+ → Create annotation property…`

---

### 2.2. Anotar una clase (ejemplo: `PersonajeUkuku`)

1. Entities → Classes.
2. Seleccionar la clase.
3. Pestaña **Annotations**.
4. Agregar:

**descripcionBreve**  
Figura enmascarada que representa al Ukuku en festividades andinas.

**descripcionEtnografica**  
Combina rasgos animales y humanos; actúa como guardián, mediador y disciplinador. Participa en vigilias nocturnas, procesiones y recorridos de alta montaña.

**fuenteTexto**  
Notas de campo, campaña 2023.

---

### 2.3. Anotar un individuo (ejemplo: `PersonajeUkuku1`)

**descripcionBreve**  
Danzante que interpreta al Ukuku en la comparsa Ukukus 2024.

**descripcionEtnografica**  
Participa en recorridos nocturnos hacia el santuario y ayuda a mantener el orden entre peregrinos.

**fuenteTexto**  
Entrevista realizada en Qoyllur Rit'i 2024.

---

### 2.4. Anotar recursos mediales (Foto, Video, Audio, Documento)

Ejemplo: `Foto_EntradaNaciones_2024`

**descripcionBreve**  
Fotografía de la Entrada de Naciones frente a la iglesia en 2024.

**descripcionEtnografica**  
Registra comparsas formadas frente a la fachada de la iglesia mientras el público observa.

**fuenteTexto**  
Archivo de investigación 2024.

Vincular recurso:

```ttl
:Foto_EntradaNaciones_2024 :documenta :EntradaDeNaciones .
```

---

## 3. Buenas prácticas de redacción

### Para `descripcionBreve`

- Máximo 2 frases.
- Define qué es la entidad.
- Evita tecnicismos.

Ejemplos:

- “Fiesta patronal en Paucartambo dedicada a la Virgen del Carmen.”
- “Figura ritual que representa al Ukuku.”

### Para `descripcionEtnografica`

- 3–6 frases.
- Prosa natural, no listas.
- Describe acciones, actores, significados, contexto.

---

## 4. Conexión con el pipeline kg-llm

### 4.1. Editar en Protégé

- Abrir y modificar `grafo.ttl`.
- Añadir o corregir descripciones.
- Guardar.

### 4.2. Subir cambios a GitHub

```bash
cd kg-llm
git add data/grafo.ttl
git commit -m "Actualización de descripciones etnográficas"
git push
```

### 4.3. Actualizar la Raspberry Pi

```bash
cd /home/pi/Documents/kg-llm
git pull
python3 scripts/01_extract_entities.py
python3 scripts/02_build_index.py
```

### 4.4. Consultar con el LLM local

```bash
python3 scripts/03_query.py "¿Qué papel cumplen los Ukukus al amanecer?"
```

---

## 5. Trabajo colaborativo (Dina + equipo)

Recomendación: mantener una hoja colaborativa con columnas:

- URI  
- Tipo (Clase / Individuo / Foto / Audio / Documento)  
- descripcionBreve  
- descripcionEtnografica  
- fuenteTexto  
- Autor(a)  
- Fecha  

**Flujo recomendado**:

1. Redactar primero en la hoja.
2. Revisar en conjunto.
3. Copiar versiones finales a Protégé.
4. Guardar `grafo.ttl`.
5. Subir a GitHub.
6. Regenerar índices en la Raspberry.

La ontología se convierte así en una **cartografía textual colectiva** que alimenta directamente el sistema RAG local.
