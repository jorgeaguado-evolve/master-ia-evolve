#!/usr/bin/env python3
"""
investigacion.py — Investigación multi-agente paralela con síntesis Opus.

Uso:
    python execution/investigacion.py \\
        --tema "Canales de YouTube sobre IA en España" \\
        --objetivo "Mejorar mis guiones" \\
        --pasos "Identifica los 3 mejores videos" "Analiza la estructura del guion" \\
        --n 4

    python execution/investigacion.py  # pide inputs interactivamente
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Optional

import anthropic
from dotenv import load_dotenv

load_dotenv()

# ── Modelos ────────────────────────────────────────────────────────────────────
SONNET = "claude-sonnet-4-6"
OPUS   = "claude-opus-4-7"

# ── Perspectivas predefinidas ──────────────────────────────────────────────────
PERSPECTIVAS = [
    {
        "nombre": "Analista",
        "emoji": "📊",
        "color": "#3b82f6",
        "tagline": "Datos · Patrones · Evidencia",
        "enfoque": (
            "Tu perspectiva es la de los datos y la evidencia empírica. "
            "Buscas patrones verificables, métricas concretas y hechos que se puedan demostrar. "
            "Desconfías de las afirmaciones sin respaldo cuantitativo o sin fuentes."
        ),
    },
    {
        "nombre": "Escéptico",
        "emoji": "🔍",
        "color": "#ef4444",
        "tagline": "Límites · Contraejemplos · Rigor",
        "enfoque": (
            "Tu perspectiva es la del rigor crítico. "
            "Buscas contraejemplos, señalas los límites del conocimiento disponible "
            "y cuestionas supuestos que se dan por sentados. "
            "Tu valor es señalar lo que falta o lo que puede estar mal."
        ),
    },
    {
        "nombre": "Creativo",
        "emoji": "💡",
        "color": "#10b981",
        "tagline": "Conexiones · Analogías · Ideas nuevas",
        "enfoque": (
            "Tu perspectiva busca conexiones no obvias, analogías de otros dominios "
            "e ideas que rompen el marco convencional. "
            "Priorizas la originalidad y las asociaciones inesperadas sobre la seguridad."
        ),
    },
    {
        "nombre": "Pragmático",
        "emoji": "⚙️",
        "color": "#f59e0b",
        "tagline": "Aplicación · Restricciones · Siguiente paso",
        "enfoque": (
            "Tu perspectiva es la aplicabilidad real: ¿qué funciona en la práctica? "
            "¿Qué restricciones existen? ¿Cuál es el siguiente paso accionable? "
            "Traducir ideas en acciones concretas es tu prioridad."
        ),
    },
    {
        "nombre": "Historiador",
        "emoji": "📚",
        "color": "#8b5cf6",
        "tagline": "Contexto · Evolución · Precedentes",
        "enfoque": (
            "Tu perspectiva es histórica y contextual: ¿de dónde viene esto? "
            "¿Cómo ha evolucionado? ¿Qué precedentes existen? "
            "El contexto temporal y los antecedentes son clave para ti."
        ),
    },
    {
        "nombre": "Estratega",
        "emoji": "🎯",
        "color": "#06b6d4",
        "tagline": "Ventajas · Oportunidades · Largo plazo",
        "enfoque": (
            "Tu perspectiva es estratégica: ventajas competitivas, posicionamiento, "
            "oportunidades y amenazas a largo plazo. "
            "Piensas en términos de sistemas, incentivos y consecuencias de segundo orden."
        ),
    },
    {
        "nombre": "Divulgador",
        "emoji": "📣",
        "color": "#f97316",
        "tagline": "Claridad · Accesibilidad · Narrativa",
        "enfoque": (
            "Tu perspectiva busca la explicación más clara y accesible posible. "
            "¿Cómo se lo contarías a alguien que no sabe nada del tema? "
            "La narrativa central y la comunicación efectiva son tu foco."
        ),
    },
    {
        "nombre": "Técnico",
        "emoji": "🔧",
        "color": "#64748b",
        "tagline": "Mecanismos · Implementación · Precisión",
        "enfoque": (
            "Tu perspectiva es la de los mecanismos exactos: ¿cómo funciona por dentro? "
            "¿Cuáles son los detalles de implementación que más importan? "
            "La precisión técnica y el rigor en los detalles son tu prioridad."
        ),
    },
]


# ── Prompts ────────────────────────────────────────────────────────────────────

def build_system_prompt(perspectiva: dict, tema: str, objetivo: str, n_pasos: int, uniforme: bool) -> str:
    if uniforme:
        return (
            f"Eres un investigador objetivo y riguroso.\n\n"
            f"TEMA: '{tema}'\n"
            f"OBJETIVO DE LA INVESTIGACIÓN: '{objetivo}'\n\n"
            f"Ejecutarás {n_pasos} paso(s) secuenciales. En cada paso recibirás la instrucción "
            f"y el contexto acumulado de tus pasos anteriores. "
            f"Responde únicamente con el resultado del paso pedido. Sé exhaustivo y específico."
        )
    return (
        f"Eres el investigador '{perspectiva['nombre']}' ({perspectiva['emoji']}).\n\n"
        f"TU PERSPECTIVA: {perspectiva['enfoque']}\n\n"
        f"TEMA A INVESTIGAR: '{tema}'\n"
        f"OBJETIVO DE LA INVESTIGACIÓN: '{objetivo}'\n\n"
        f"Ejecutarás {n_pasos} paso(s) secuenciales desde tu perspectiva característica. "
        f"En cada paso recibirás la instrucción y el contexto acumulado de tus pasos anteriores. "
        f"Responde únicamente con el resultado del paso pedido. "
        f"Mantén tu perspectiva en todo momento. "
        f"No sabes que otros investigadores trabajan en paralelo sobre el mismo tema."
    )


def build_step_message(tema: str, paso_num: int, instruccion: str, pasos_anteriores: list) -> str:
    context = ""
    if pasos_anteriores:
        context = "\n\nTUS PASOS ANTERIORES:\n"
        for p in pasos_anteriores:
            context += f"\n--- Paso {p['num']}: {p['instruccion']} ---\n{p['output']}\n"

    return (
        f"TEMA: {tema}\n"
        f"{context}\n"
        f"PASO ACTUAL ({paso_num}): {instruccion}\n\n"
        f"Ejecuta este paso. Responde solo con el resultado de este paso."
    )


# ── Agente individual (async) ──────────────────────────────────────────────────

async def run_agent(
    client: anthropic.AsyncAnthropic,
    agent_id: int,
    perspectiva: dict,
    tema: str,
    objetivo: str,
    pasos: list,
    uniforme: bool,
) -> dict:
    system = build_system_prompt(perspectiva, tema, objetivo, len(pasos), uniforme)
    pasos_anteriores = []
    steps_done = []

    for i, instruccion in enumerate(pasos, 1):
        user_msg = build_step_message(tema, i, instruccion, pasos_anteriores)
        resp = await client.messages.create(
            model=SONNET,
            max_tokens=2000,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        output = resp.content[0].text.strip()
        step = {"num": i, "instruccion": instruccion, "output": output}
        steps_done.append(step)
        pasos_anteriores.append(step)
        print(f"  [{perspectiva['nombre']}] paso {i}/{len(pasos)} completado", flush=True)

    full_output = "\n\n".join(
        f"**Paso {s['num']}: {s['instruccion']}**\n{s['output']}"
        for s in steps_done
    )

    return {
        "agent_id": agent_id,
        "perspectiva": perspectiva["nombre"],
        "emoji": perspectiva["emoji"],
        "steps": steps_done,
        "full_output": full_output,
    }


# ── Orquestador async ──────────────────────────────────────────────────────────

async def run_all(
    client: anthropic.AsyncAnthropic,
    tema: str,
    objetivo: str,
    pasos: list,
    n: int,
    uniforme: bool,
) -> list:
    if uniforme:
        perspectivas = [
            {"nombre": f"Investigador {i+1}", "emoji": "🔎", "enfoque": "objetivo y riguroso"}
            for i in range(n)
        ]
    else:
        perspectivas = PERSPECTIVAS[:n]

    tasks = [
        run_agent(client, i, perspectivas[i], tema, objetivo, pasos, uniforme)
        for i in range(n)
    ]
    return await asyncio.gather(*tasks, return_exceptions=True)


# ── Sintetizador Opus (sync) ───────────────────────────────────────────────────

def sintetizar(
    client: anthropic.Anthropic,
    tema: str,
    objetivo: str,
    pasos: list,
    resultados: list,
) -> str:
    bloques = ""
    for r in resultados:
        if isinstance(r, Exception):
            continue
        sep = "=" * 50
        bloques += f"\n\n{sep}\nINVESTIGADOR: {r['emoji']} {r['perspectiva']}\n{sep}\n{r['full_output']}"

    pasos_str = "\n".join(f"  {i+1}. {p}" for i, p in enumerate(pasos))

    resp = client.messages.create(
        model=OPUS,
        max_tokens=3000,
        system=(
            "Eres un sintetizador experto. Tu función es consolidar investigaciones "
            "paralelas e independientes en una síntesis rigurosa y accionable. "
            "Cada investigador trabajó de forma aislada sobre el mismo tema. "
            "Tu síntesis debe revelar lo que el conjunto sabe que ninguno sabía por separado."
        ),
        messages=[{"role": "user", "content": (
            f"TEMA: {tema}\n"
            f"OBJETIVO DE LA INVESTIGACIÓN: {objetivo}\n"
            f"PASOS EJECUTADOS POR CADA INVESTIGADOR:\n{pasos_str}\n\n"
            f"INVESTIGACIONES INDEPENDIENTES:{bloques}\n\n"
            f"Sintetiza. Estructura tu respuesta EXACTAMENTE así:\n\n"
            f"## Hallazgos Clave\n"
            f"(Los 5-7 hallazgos más importantes. Indica qué investigador/es los señalaron.)\n\n"
            f"## Patrones Transversales\n"
            f"(Qué vieron la mayoría o todos los investigadores de forma independiente.)\n\n"
            f"## Tensiones y Contradicciones\n"
            f"(Dónde llegaron a conclusiones distintas y qué revela esa diferencia.)\n\n"
            f"## Perspectivas Únicas\n"
            f"(Qué aportó cada perspectiva que las otras no vieron.)\n\n"
            f"## Conclusión Sintetizada\n"
            f"(2-3 párrafos: qué sabe el equipo ahora que no sabía antes.)\n\n"
            f"## Líneas Abiertas\n"
            f"(Qué quedó sin resolver. Qué investigar a continuación.)"
        )}],
    )
    return resp.content[0].text.strip()


# ── Guardar outputs ────────────────────────────────────────────────────────────

def guardar_outputs(
    tema: str,
    objetivo: str,
    pasos: list,
    n: int,
    uniforme: bool,
    resultados: list,
    sintesis: str,
    timestamp: str,
) -> tuple[str, str]:
    tmp = os.path.join(os.path.dirname(__file__), "..", ".tmp")
    os.makedirs(tmp, exist_ok=True)

    doc_path = os.path.join(tmp, f"investigacion_{timestamp}.md")
    json_path = os.path.join(tmp, f"investigacion_{timestamp}.json")

    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(f"# Investigación: {tema}\n\n")
        f.write(f"**Fecha**: {timestamp[:8][:4]}-{timestamp[4:6]}-{timestamp[6:8]} | ")
        f.write(f"**Agentes**: {n} | **Pasos**: {len(pasos)}\n\n")
        f.write(f"**Objetivo**: {objetivo}\n\n")
        f.write("---\n\n## Hallazgos por Investigador\n\n")

        for r in resultados:
            if isinstance(r, Exception):
                f.write(f"### [Error]\n\n{str(r)}\n\n")
                continue
            f.write(f"### {r['emoji']} {r['perspectiva']}\n\n")
            f.write(r["full_output"])
            f.write("\n\n")

        f.write("---\n\n## Síntesis (Opus)\n\n")
        f.write(sintesis)
        f.write("\n")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "tema": tema,
                "objetivo": objetivo,
                "pasos": pasos,
                "n_agentes": n,
                "uniforme": uniforme,
                "timestamp": timestamp,
                "investigadores": [
                    r if not isinstance(r, Exception) else {"error": str(r)}
                    for r in resultados
                ],
                "sintesis": sintesis,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    return os.path.abspath(doc_path), os.path.abspath(json_path)


# ── Orquestador principal ──────────────────────────────────────────────────────

def run_investigacion(
    tema: str,
    objetivo: str,
    pasos: list,
    n: int = 4,
    uniforme: bool = False,
) -> None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY no encontrada en .env")
        sys.exit(1)

    if not pasos:
        print("ERROR: se requiere al menos un paso.")
        sys.exit(1)

    if not (1 <= n <= 8):
        print("ERROR: n debe estar entre 1 y 8.")
        sys.exit(1)

    client_async = anthropic.AsyncAnthropic(api_key=api_key)
    client_sync  = anthropic.Anthropic(api_key=api_key)

    if not uniforme:
        perspectivas_asignadas = [p["nombre"] for p in PERSPECTIVAS[:n]]
    else:
        perspectivas_asignadas = [f"Investigador {i+1}" for i in range(n)]

    n_llamadas = n * len(pasos) + 1
    print(f"\nTema: {tema}")
    print(f"Objetivo: {objetivo}")
    print(f"Investigadores: {', '.join(perspectivas_asignadas)}")
    print(f"Pasos por investigador: {len(pasos)}")
    print(f"Llamadas API estimadas: {n_llamadas} ({n * len(pasos)} Sonnet + 1 Opus)\n")

    print("Lanzando investigadores en paralelo...")
    resultados = asyncio.run(
        run_all(client_async, tema, objetivo, pasos, n, uniforme)
    )

    errores = [r for r in resultados if isinstance(r, Exception)]
    if errores:
        print(f"\nATENCIÓN: {len(errores)} investigador(es) fallaron.")

    print("\nSintetizando con Opus...")
    sintesis = sintetizar(client_sync, tema, objetivo, pasos, resultados)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    doc_path, json_path = guardar_outputs(
        tema, objetivo, pasos, n, uniforme, resultados, sintesis, timestamp
    )

    print("\n" + "─" * 60)
    print(sintesis)
    print("─" * 60)
    print(f"\n[Documento: .tmp/investigacion_{timestamp}.md]")
    print(f"[JSON:      .tmp/investigacion_{timestamp}.json]")


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Investigación multi-agente paralela con síntesis Opus.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--tema", help="Qué se investiga")
    parser.add_argument("--objetivo", help="Para qué sirve la investigación")
    parser.add_argument("--pasos", nargs="+", help="Pasos que ejecuta cada investigador")
    parser.add_argument("--n", type=int, default=4, dest="n_agentes",
                        help="Número de investigadores (1-8, default: 4)")
    parser.add_argument("--uniforme", action="store_true",
                        help="Todos los investigadores con perspectiva neutra")

    args = parser.parse_args()

    tema     = args.tema
    objetivo = args.objetivo
    pasos    = args.pasos

    if not tema:
        print("Tema de investigación:")
        tema = input("> ").strip()

    if not objetivo:
        print("Objetivo de la investigación:")
        objetivo = input("> ").strip()

    if not pasos:
        print("Pasos (uno por línea, línea vacía para terminar):")
        pasos = []
        while True:
            p = input(f"  Paso {len(pasos)+1}: ").strip()
            if not p:
                break
            pasos.append(p)

    if not tema or not objetivo or not pasos:
        print("ERROR: tema, objetivo y al menos un paso son obligatorios.")
        sys.exit(1)

    run_investigacion(
        tema=tema,
        objetivo=objetivo,
        pasos=pasos,
        n=args.n_agentes,
        uniforme=args.uniforme,
    )
