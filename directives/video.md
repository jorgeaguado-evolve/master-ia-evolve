# Directiva: Producción de Vídeo con Hyperframes

## Objetivo
Crear vídeos MP4 para redes sociales (horizontal y vertical) usando Hyperframes como motor de composición. El output final es un archivo MP4 listo para publicar.

## Inputs
- Mensaje o guion del vídeo (obligatorio)
- Formato: horizontal (1920x1080) o vertical (1080x1920)
- Duración objetivo (ej. 15s, 30s, 60s)
- Assets opcionales: vídeos, imágenes, audio, fuentes

## Herramientas
- `npx hyperframes init` — scaffold del proyecto
- `npx hyperframes lint` — validación de estructura
- `npx hyperframes inspect` — revisión visual de layout
- `npx hyperframes preview` — servidor de preview con hot-reload
- `npx hyperframes render` — exportar MP4 final
- Skills: `hyperframes`, `hyperframes-cli`, `hyperframes-media`, `gsap`

## Proceso

### Paso 1: Briefing
Confirmar antes de escribir código:
- Formato y dimensiones (horizontal / vertical)
- Duración total en segundos
- Mensaje principal (qué debe transmitir el vídeo)
- Estilo visual (si no hay design.md: preguntar o usar visual-styles.md)
- Assets disponibles (logo, vídeos, imágenes, música)

### Paso 2: Design system
- Si existe `design.md` en el proyecto: usarlo como fuente de verdad
- Si no existe: crear uno basado en la identidad visual de Evolve (azul corporativo, tipografía limpia, dark background)
- Nunca inventar colores fuera de la paleta definida

### Paso 3: Scaffold
```bash
npx hyperframes init <nombre-proyecto> --non-interactive
```
Proyectos en: `production/videos/<nombre-proyecto>/`

### Paso 4: Composición
Seguir el orden estricto de la skill `hyperframes`:
1. Layout estático primero (hero frame de cada escena)
2. Entrances con `gsap.from()`
3. Transiciones entre escenas (nunca jump cuts)
4. Captions si hay narración o subtítulos
5. Audio sincronizado

### Paso 5: Validación
```bash
npx hyperframes lint           # errores de estructura
npx hyperframes validate       # contraste WCAG
npx hyperframes inspect        # layout visual
```
No avanzar al preview si hay errores de lint.

### Paso 6: Preview
```bash
npx hyperframes preview
```
URL a presentar a Jorge: `http://localhost:3002/#project/<nombre>`
Esperar aprobación antes de renderizar.

### Paso 7: Render
```bash
npx hyperframes render --quality standard --output renders/<nombre>.mp4
```
- `draft` para iteraciones rápidas
- `standard` para revisión
- `high` para entrega final

## Formatos de salida
| Plataforma | Formato | Dimensiones | Duración |
|-----------|---------|-------------|----------|
| Instagram Reels / TikTok | Vertical | 1080x1920 | 15-60s |
| YouTube / LinkedIn | Horizontal | 1920x1080 | 30-180s |
| Instagram Feed | Cuadrado | 1080x1080 | 15-60s |
| Stories | Vertical | 1080x1920 | hasta 15s |

## Edge cases
- **FFmpeg no instalado**: ejecutar `npx hyperframes doctor` y pedir a Jorge que instale FFmpeg antes de renderizar
- **Assets pesados**: procesarlos primero con `npx hyperframes tts` o `remove-background` antes de incluirlos
- **Font no encontrada**: avisar antes de escribir HTML; no sustituir fonts sin permiso
- **Preview lento**: reducir workers o usar `--quality draft`

## Carpeta de producción
```
production/
  videos/
    <nombre-proyecto>/
      index.html          ← composición principal
      design.md           ← identidad visual del vídeo
      assets/             ← media local (vídeos, imágenes, audio)
      fonts/              ← fuentes personalizadas .woff2
      compositions/       ← sub-composiciones
      renders/            ← outputs MP4 finales
```
