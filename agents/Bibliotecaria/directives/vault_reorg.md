# Vault: Reorganización estructural

## Objetivo

Detectar desorden en el vault (páginas mal ubicadas, carpetas con demasiado volumen, notas sin clasificar) y proponer un plan de reorganización. Ejecutar solo con aprobación de Jorge.

## Inputs

- Alcance (opcional):
  - `wiki` (default): solo la carpeta `wiki/`
  - `completo`: todo el vault excepto `RAW/`
  - `carpeta:[nombre]`: una carpeta específica

## Principio invariable

Amalia mapea y propone. Jorge aprueba. Solo entonces se ejecuta.
Ningún archivo se mueve, renombra ni elimina sin confirmación explícita.

---

## Pasos

### Fase 1: Diagnóstico (siempre ejecutar)

1. Mapear la estructura completa del alcance con:
   ```bash
   find [RUTA] -type f -name "*.md" | sort
   ```
2. Contar páginas por carpeta y detectar:
   - Carpetas con más de 30 archivos (candidatas a subcarpetas)
   - Archivos directamente en la raíz del vault (deberían estar en subcarpeta)
   - Archivos con nombres genéricos (`sin-titulo.md`, `nota-1.md`, `borrador.md`)
   - Archivos sin extensión `.md` en carpetas de wiki
3. Detectar notas huérfanas (ningún wikilink las apunta):
   ```bash
   # Para cada archivo X, verificar si [[X]] aparece en algún otro archivo
   # Usar grep en el vault completo
   ```
4. Detectar páginas con fecha `creado` o `actualizado` de más de 180 días sin referencias entrantes

### Fase 2: Informe de diagnóstico

Presentar a Jorge con estas secciones antes de ejecutar nada:

```
## Diagnóstico de reorganización — [FECHA]

### Estructura
- Total archivos analizados: N
- Carpetas con >30 archivos: [lista]
- Archivos en raíz del vault: [lista]

### Archivos problemáticos
- Nombres genéricos que requieren renombrado: [lista con propuesta]
- Formato incorrecto: [lista]

### Notas huérfanas (sin referencias entrantes)
- [lista de archivos con ruta]

### Páginas antiguas sin mantenimiento
- [lista con fecha de último actualizado]

### Propuesta de reorganización
[tabla: acción | archivo/carpeta origen | destino propuesto | justificación]

¿Ejecuto los cambios aprobados?
```

### Fase 3: Ejecución (solo con OK de Jorge)

Para cada cambio aprobado:

1. **Renombrado**: `mv [origen] [destino]` + actualizar todos los wikilinks que apuntan al archivo viejo:
   ```bash
   grep -r "[[nombre-viejo]]" [VAULT] --include="*.md" -l
   # Para cada archivo encontrado: reemplazar [[nombre-viejo]] con [[nombre-nuevo]]
   ```
2. **Movimiento de carpeta**: mover archivos + actualizar rutas en index.md
3. **Renombrado de carpeta**: igual que movimiento + actualizar todas las referencias

### Fase 4: Verificación post-ejecución

Después de cada cambio:
- Verificar que los wikilinks actualizados son válidos
- Actualizar `wiki/index.md` si la reorganización afecta al wiki
- Añadir entrada en `wiki/log.md`: `## [FECHA] reorg | [descripción breve]`

---

## Edge cases

- **Archivo referenciado desde una nota de solo lectura** (`Notas/`): no modificar el origen, solo anotar el conflicto
- **Dos archivos con el mismo nombre en carpetas distintas**: señalarlo como conflicto y pedir instrucción explícita
- **Carpeta con estructura deliberada** (Master/, Proyectos/): no proponer cambios internos sin contexto del proyecto
- **Wikilinks ambiguos** (mismo nombre en dos ubicaciones): no resolver unilateralmente, señalar como ambigüedad
