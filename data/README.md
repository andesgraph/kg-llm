## Uso de Protégé Web con `grafo.ttl`

Puedes usar **Protégé Web** para visualizar y editar tu grafo RDF antes de pasarlo al pipeline `kg-llm`.

### 1. Abrir Protégé Web

- Entra a: <https://webprotege.stanford.edu>  
- Crea una cuenta o inicia sesión.

### 2. Crear un nuevo proyecto

1. Clic en **Create new project**.  
2. Elige **Blank project**.  
3. Asigna un nombre (por ejemplo, `Festividades-Andinas-KG`).  
4. Clic en **Create**.

### 3. Importar tu archivo `grafo.ttl`

1. En el panel izquierdo, ve a **Settings**.  
2. Abre la sección **Imports**.  
3. Clic en **Add import**.  
4. Selecciona **Upload file**.  
5. Sube tu archivo TTL (el mismo que usas en `data/grafo.ttl`).  
6. Guarda los cambios para que la ontología quede importada en el proyecto.

### 4. Explorar el grafo en Protégé Web

Una vez importado:

- En **Classes** podrás ver las clases principales de tu ontología (por ejemplo, `Festividad`, `Comunidad`, `PersonajeRitual`, `Danza`, etc.).
- En **Object properties** verás las propiedades de relación (por ejemplo, `interpreta`, `representa`, `realizaDanza`).
- En **Data properties** verás atributos literales (fechas, nombres, descripciones, etc.).
- En **Individuals** podrás inspeccionar instancias concretas (por ejemplo, individuos como `Ukuku`, festividades específicas, comunidades, etc.).

### 5. Editar la ontología

En Protégé Web puedes:

- Crear nuevas clases y jerarquías (subclases de `Festividad`, `Comunidad`, etc.).
- Ajustar propiedades (`domain`, `range`, axiomas `subPropertyOf`, restricciones de cardinalidad).
- Añadir o modificar individuos y sus relaciones.
- Verificar consistencia lógica con el reasoner disponible.

Usa estos cambios para refinar tu modelo conceptual antes de extraer entidades para el índice vectorial.

### 6. Exportar nuevamente el TTL para `kg-llm`

Cuando termines de editar:

1. En el proyecto, ve a **Settings**.  
2. Usa la opción **Download** o **Export** (dependiendo de la versión de WebProtégé).  
3. Elige el formato **Turtle (.ttl)**.  
4. Descarga el archivo y guárdalo en tu proyecto local como:

        data/grafo.ttl

5. Vuelve a generar el índice:

        python scripts/extract_entities.py
        python scripts/build_index.py

Con esto, `kg-llm` trabajará con la versión actualizada de tu grafo.

---

## Subir el proyecto a GitHub

    git init
    git add .
    git commit -m "Initial kg-llm pipeline"
    git branch -M main
    git remote add origin https://github.com/andesgraph/kg-llm.git
    git push -u origin main

---

## Licencia

MIT License. Puedes usarlo y modificarlo libremente.

---

## Contribuciones

Pull requests y mejoras son bienvenidas.  
Si deseas reportar errores, usa los Issues del repositorio.