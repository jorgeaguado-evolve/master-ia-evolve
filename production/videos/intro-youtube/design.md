# Design System — Evolve Intro YouTube

Extraído de https://evolve.es/ — 2026-05-11

## Colores

```css
:root {
  --evolve-dark:       #1a1a1a;   /* fondo principal, texto */
  --evolve-blue:       #0066ff;   /* acento principal, CTAs */
  --evolve-white:      #ffffff;   /* texto sobre oscuro, fondos */
  --evolve-gray-light: #f7f7f7;   /* fondos secundarios */
  --evolve-gray:       #6c757d;   /* texto secundario */
  --evolve-text-muted: rgba(26, 26, 26, 0.6);
}
```

**Paleta para vídeo:**
- Fondo: `#1a1a1a` (dark — máximo contraste para YouTube)
- Texto principal: `#ffffff`
- Acento/highlight: `#0066ff`
- Texto secundario: `rgba(255,255,255,0.6)`

## Tipografía

- **Titulares**: `Plus Jakarta Sans` (Google Fonts, weights 200–800)
- **Cuerpo / UI**: `Inter` (Google Fonts, weights 100–900)
- **Fallback**: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`

**Escala tipográfica (vídeo 1920×1080):**
| Elemento       | Tamaño  | Peso |
|----------------|---------|------|
| Título hero    | 72–96px | 700  |
| Subtítulo      | 36–48px | 500  |
| Caption/body   | 28–32px | 400  |
| Lower third    | 24px    | 600  |

## Estilo visual

- **Tema**: Dark background (`#1a1a1a`) con texto blanco — óptimo para vídeo
- **Estética**: Minimalista, profesional, tech-educativo
- **Sensación**: Limpio, moderno, sin ruido visual
- **3 adjetivos**: Profesional · Accesible · Progresista

## Botones / Badges

- Border radius: `12px` (cards) / `20px` (pills)
- CTA principal: fondo `#0066ff`, texto `#fff`
- CTA secundario: fondo `#1a1a1a`, texto `#fff`
- Padding: `14px 20px`

## Sombras

```css
--shadow-card: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
--shadow-deep: rgba(0,0,0,0.43) 0px 0.6px 0.6px -1.25px,
               rgba(0,0,0,0.38) 0px 2.3px 2.3px -2.5px,
               rgba(0,0,0,0.15) 0px 10px 10px -3.75px;
```

## Animaciones

- Easing estándar: `ease` / `ease-in-out`
- Duración: `0.3s` (micro) / `0.5s` (cards/transiciones)
- Efectos: fade-in, reveal-words, rollover text
- **Para intro YouTube**: entrances con `gsap.from()`, reveal de palabras

## Assets del proyecto

- Logo: descargar de `https://evolve.es/wp-content/themes/evolve/assets/images/logo/logo-evolve.png`
- Fuentes: Google Fonts (Inter + Plus Jakarta Sans)
- Vídeo fuente: `/Users/jvalero/Downloads/Imagenes Editar/video test.mp4`
- Formato output: 1920×1080 MP4

## Google Fonts import

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&family=Plus+Jakarta+Sans:wght@200..800&display=swap" rel="stylesheet">
```
