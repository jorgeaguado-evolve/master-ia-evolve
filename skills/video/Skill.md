---
name: Video
description: Producción de vídeos MP4 para redes sociales con Hyperframes. Activar para crear, editar o renderizar composiciones de vídeo horizontal (1920x1080) o vertical (1080x1920).
---

# Skill: Video

Capacidad de producción audiovisual usando Hyperframes como motor de composición HTML-to-video.

## Cuándo activar
- Jorge pide crear un vídeo para redes sociales
- Hay que editar o mejorar una composición Hyperframes existente
- Se necesita renderizar o exportar un vídeo MP4
- Tareas de animación, captions, transiciones o voiceover

## Qué puede hacer Jeffrey en este dominio
- Crear composiciones HTML animadas con timing preciso
- Generar vídeos en formato horizontal (YouTube, LinkedIn) y vertical (Reels, TikTok)
- Sincronizar captions con audio mediante transcripción Whisper
- Aplicar transiciones profesionales entre escenas (crossfade, wipe, shader)
- Añadir TTS (text-to-speech) para narración
- Eliminar fondos de vídeos con `remove-background`
- Previsualizar en navegador con hot-reload antes de renderizar

## Skills de Hyperframes disponibles
Las siguientes skills están instaladas en `.agents/skills/`:
- `hyperframes` — composición completa
- `hyperframes-cli` — comandos de desarrollo y render
- `hyperframes-media` — TTS, transcripción, background removal
- `hyperframes-registry` — catálogo de bloques preconstruidos
- `gsap`, `animejs`, `lottie`, `three`, `waapi` — librerías de animación
- `tailwind` — estilos en composiciones
- `css-animations` — animaciones CSS puras

## Prerequisitos del sistema
- Node.js >= 22 (instalado: v22.19.0)
- FFmpeg (PENDIENTE DE INSTALAR — necesario para render)

## Activación del perfil de agente
Al activar esta skill, Jeffrey opera en modo `video_agent` (ver [agents/video_agent.md](../../agents/video_agent.md)).

## Proceso estándar
Ver [directives/video.md](../../directives/video.md) para el SOP completo.

## Carpeta de trabajo
`production/videos/` — cada proyecto tiene su propia subcarpeta.
