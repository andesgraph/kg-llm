# Flujo completo: Protégé Desktop (PC) → GitHub → Raspberry Pi (kg-llm)

El principio es simple:

- La **Raspberry nunca edita** el grafo, solo recibe cambios.
- El **PC con Protégé Desktop** es tu “editor oficial” de la ontología.

---

## 🔵 1. Instalar y usar Protégé Desktop en tu PC

1. Descarga Protégé Desktop desde:  
   https://protege.stanford.edu/software.php

2. Abre tu ontología en Protégé:

    File → Open  
    Selecciona el archivo: `kg-llm/data/grafo.ttl`

3. Edita lo que necesites:

   - Clases  
   - Propiedades  
   - Individuos  
   - Axiomas y restricciones  
   - Jerarquías

4. Guarda los cambios:

    File → Save

Ese `grafo.ttl` actualizado será el que sincronices con GitHub.

---

## 🟣 2. Subir el TTL editado a GitHub (desde tu PC)

En tu PC donde editaste con Protégé:

    cd kg-llm
    git add data/grafo.ttl
    git commit -m "Ontología actualizada desde Protégé Desktop"
    git push

Con esto, el repositorio remoto ya tiene la nueva versión de la ontología.

---

## 🟢 3. Actualizar la Raspberry Pi (donde vive kg-llm)

La Raspberry **no edita** el grafo, solo baja la última versión.

En la Raspberry Pi:

    cd kg-llm
    git pull

Ahora `data/grafo.ttl` está actualizado también en la Raspberry.

---

## 🟡 4. Regenerar los índices en la Raspberry

Cada vez que cambias la ontología, debes regenerar:

- `data/index_entities.json`
- `index/entity_vectors.npz`

En la Raspberry:

    python scripts/extract_entities.py
    python scripts/build_index.py

Después de esto, puedes hacer consultas con el grafo actualizado, por ejemplo:

    python scripts/answer.py "¿Quiénes son los personajes de Qoyllur Rit'i?"

---

## 🟤 5. (Opcional) Script para automatizar la actualización en Raspberry

Puedes crear un script llamado `update_kg.sh` que haga todo junto.

Contenido sugerido:

    #!/bin/bash
    cd /home/pi/kg-llm
    git pull
    source llm-env/bin/activate
    python scripts/extract_entities.py
    python scripts/build_index.py
    echo "✓ KG actualizado"

Luego le das permisos de ejecución:

    chmod +x update_kg.sh

Y cuando quieras actualizar todo:

    ./update_kg.sh

---

## 🔥 Resumen ultra claro

- **En tu PC con Protégé Desktop:**  
  Editas la ontología → Guardas (`File → Save`) → `git add` → `git commit` → `git push`

- **En la Raspberry Pi:**  
  `git pull` → regeneras índices (`extract_entities.py` y `build_index.py`) → usas `kg-llm` normalmente.
  

# Guía básica: cómo usar Protégé Desktop (operaciones esenciales) + sincronización con GitHub y Raspberry

Esta guía resume lo que necesitas para **editar tu ontología en Protégé Desktop** y luego **sincronizar los cambios** con tu repositorio en **GitHub** y con la **Raspberry Pi** donde vive `kg-llm`.

---

## 1. Abrir y navegar tu ontología en Protégé Desktop

1. Abre Protégé Desktop.  
2. Ve a: **File → Open**.  
3. Selecciona el archivo: `kg-llm/data/grafo.ttl`.  

En el panel izquierdo verás:

- **Classes**: clases y jerarquías conceptuales.  
- **Object Properties**: relaciones entre entidades.  
- **Data Properties**: atributos literales (strings, fechas, números).  
- **Individuals**: instancias concretas (ej. `Ukuku`).  
- **Annotation Properties**: etiquetas y comentarios (labels, notes, etc.).

Desde ahí puedes explorar toda la estructura del grafo.

---

## 2. Crear una clase nueva

1. Ve al panel **Classes**.  
2. Selecciona la clase padre (por ejemplo, `Danza`).  
3. Clic derecho → **Create subclass**.  
4. Escribe el nombre de la nueva clase, por ejemplo: `IndividuoDeDanza`.  

Protégé genera automáticamente el axioma:

    IndividuoDeDanza ⊑ Danza

(lo que significa: “IndividuoDeDanza es una subclase de Danza”).

---

## 3. Crear una propiedad de objeto (Object Property)

1. Ve al panel **Object Properties**.  
2. Clic en el botón **+** para crear una nueva propiedad.  
3. Escribe el nombre, por ejemplo: `interpreta`.  
4. En el panel derecho define:

    Domain: IndividuoDeDanza  
    Range: PersonajeRitual  

Esto quiere decir: “un IndividuoDeDanza interpreta un PersonajeRitual”.

---

## 4. Crear o editar un individuo (instancia)

1. Ve al panel **Individuals**.  
2. Clic en **+ Add individual**.  
3. Pon un nombre, por ejemplo: `Ukuku`.  
4. Asigna su tipo/clase: `IndividuoDeDanza`.  
5. En la sección **Object property assertions**, añade relaciones, por ejemplo:

    interpreta → PersonajeRitual_Ukuku  
    realizaDanza → Danza_Ukuku  

Así conectas el individuo con otras entidades del grafo.

---

## 5. Añadir anotaciones (labels, comentarios, metadata)

En cualquier clase, propiedad o individuo, abre la pestaña **Annotations** y añade cosas como:

- `rdfs:label` → nombre legible.  
- `rdfs:comment` → descripción explicativa.  
- `skos:altLabel` → nombres alternativos.

Ejemplo para el individuo `Ukuku`:

    rdfs:label: "Ukuku"  
    rdfs:comment: "Personaje central en la festividad de Qoyllur Rit'i."  

Estas anotaciones luego ayudan en la parte de recuperación semántica (RAG).

---

## 6. Añadir axiomas y restricciones

En la pestaña **Class Description** puedes añadir:

- Restricciones existenciales (someValuesFrom), por ejemplo:

      IndividuoDeDanza ⊑ ∃interpreta.PersonajeRitual

- Subclases adicionales, por ejemplo:

      Ukuku ⊑ PersonajeRitual

- (Con cuidado) clases equivalentes, por ejemplo:

      Festividad ≡ Evento ⊓ TieneComunidad

Solo usa equivalencias cuando estés muy seguro del significado.

---

## 7. Validar la ontología con un razonador

1. Ve a **Reasoner → Start reasoner**.  
2. Elige un razonador (por ejemplo, **HermiT** o **ELK**).  

El razonador te permite:

- Detectar inconsistencias.  
- Ver inferencias automáticas de subclases.  
- Verificar dominios y rangos.  

Si alguna clase aparece en rojo o marcada como incoherente, revisa sus axiomas.

---

## 8. Guardar cambios en Protégé Desktop

Cuando termines de editar:

1. Ve a **File → Save**.  
2. Protégé guarda directamente sobre el archivo:

    kg-llm/data/grafo.ttl  

Ese archivo será el que sincronices con GitHub y luego con la Raspberry.

---

## 9. Sincronizar la ontología con GitHub (en tu PC)

En tu PC (donde tienes el repositorio `kg-llm` y usas Protégé):

3. Para sincronizar con GitHub (en tu PC):

    cd kg-llm  
    git add data/grafo.ttl  
    git commit -m "Ontología actualizada desde Protégé Desktop"  
    git push  

Con esto, el repositorio remoto ya tiene la versión actualizada de `grafo.ttl`.

---

## 10. Actualizar la Raspberry y regenerar índices

4. En la Raspberry, sincronizas con:

    cd kg-llm  
    git pull  

Esto baja la nueva versión de `data/grafo.ttl`.

5. Luego regeneras los índices para que el pipeline use el grafo actualizado:

    python scripts/extract_entities.py  
    python scripts/build_index.py  

Después de eso, puedes usar el grafo actualizado normalmente, por ejemplo:

    python scripts/answer.py "¿Quiénes son los personajes de Qoyllur Rit'i?"

---

## 11. Resumen rápido

- Editas la ontología en Protégé Desktop (PC) → `File → Save`.  
- Sincronizas con GitHub en el PC → `git add`, `git commit`, `git push`.  
- En la Raspberry haces `git pull` → regeneras entidades e índices → consultas actualizadas en `kg-llm`.

