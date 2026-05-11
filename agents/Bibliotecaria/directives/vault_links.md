# Vault: Optimización de conexiones y wikilinks

## Objetivo

Detectar conexiones potenciales entre páginas que no están enlazadas, corregir wikilinks rotos y enriquecer la red de conocimiento del vault sin alterar el contenido de las páginas.

## Cuándo activar

- Jorge pide "optimiza los enlaces del vault" o "mejora las conexiones entre notas"
- Después de un INGEST masivo (varias fuentes procesadas de golpe)
- Como parte del mantenimiento semanal junto con LINT
- Amalia detecta durante QUERY que páginas relacionadas no se referencian entre sí

## Principio de operación

Amalia no altera el texto de las páginas. Solo añade wikilinks donde un concepto ya mencionado tiene página propia pero no está enlazado.

---

## Pasos

### Fase 1: Detección de enlaces rotos

```bash
# Extraer todos los wikilinks del vault
grep -r "\[\[" [VAULT]/wiki/ --include="*.md" -h | grep -o '\[\[[^\]]*\]\]' | sort | uniq
# Para cada wikilink: verificar que el archivo destino existe
```

Generar lista de wikilinks rotos con el archivo que los contiene.

### Fase 2: Detección de menciones sin enlazar

1. Cargar `wiki/index.md` para obtener la lista de títulos/nombres de páginas existentes
2. Para cada página del wiki, buscar si su nombre (o alias principales) aparece en texto libre de otras páginas sin estar entre `[[ ]]`:
   ```bash
   grep -r "nombre-pagina" [VAULT]/wiki/ --include="*.md" -l
   # Excluir la propia página
   ```
3. Construir tabla de oportunidades: `término mencionado → aparece en → página que tiene wikilink pendiente`

### Fase 3: Detección de páginas relacionadas sin enlace mutuo

Usando el índice y los tags del frontmatter:
- Identificar páginas con tags comunes que no se referencian entre sí
- Identificar páginas del mismo tipo (ej: dos `concepto-` con tags solapados) sin `[[wikilink]]` mutuo

### Fase 4: Informe de oportunidades

Presentar antes de modificar nada:

```
## Informe de conexiones — [FECHA]

### Enlaces rotos
| Archivo | Wikilink roto | Acción propuesta |
|---------|---------------|------------------|
| ...     | [[X]]         | Renombrar / eliminar / corregir |

### Menciones sin enlazar (top 10 por frecuencia)
| Término | Páginas donde aparece sin enlazar | Acción |
|---------|-----------------------------------|--------|
| ...     | pag-1, pag-2                      | Añadir [[X]] |

### Pares de páginas relacionadas sin enlace mutuo
| Página A | Página B | Tags en común |
|----------|----------|---------------|
| ...      | ...      | agentes, LLMs |

¿Ejecuto las correcciones aprobadas?
```

### Fase 5: Ejecución (solo con OK de Jorge)

Para cada corrección aprobada:

1. **Enlace roto — destino existe con otro nombre**: actualizar `[[nombre-viejo]]` → `[[nombre-correcto]]`
2. **Enlace roto — destino no existe**: eliminar el wikilink del texto (dejar el texto plano) o crear página stub si Jorge lo indica
3. **Mención sin enlazar**: reemplazar primera ocurrencia del término en cada página con `[[nombre-página]]`
   - Solo la primera mención por página (Obsidian convention)
   - Solo si el término coincide exactamente con el nombre de página o su alias
4. **Páginas relacionadas**: añadir sección `## Relacionado` al final de cada página si no existe, con los wikilinks correspondientes

### Fase 6: Registro

Añadir entrada en `wiki/log.md`:
```
## [FECHA] links | Optimización de conexiones
- Enlaces rotos corregidos: N
- Menciones enlazadas: N  
- Pares relacionados conectados: N
- Issues pendientes: [lista si hay]
```

---

## Edge cases

- **Término ambiguo** (misma palabra, dos páginas distintas): no enlazar automáticamente, señalar como ambigüedad
- **Página con alias en frontmatter**: considerar los alias como nombres válidos para detección de menciones
- **Wikilink con sección** (`[[página#sección]]`): verificar que tanto la página como la sección existen
- **Mención en bloque de código o cita**: no enlazar (el texto dentro de ` ``` ` o `>` es referencia, no mención propia)
- **Más de 50 correcciones en un pase**: dividir en bloques de 20, presentar y ejecutar por bloques con confirmación entre cada uno
