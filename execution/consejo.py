#!/usr/bin/env python3
"""
consejo.py — Debate multi-agente con dashboard en tiempo real.

Uso:
    python execution/consejo.py "¿Cuál es la mejor estrategia para X?"
    python execution/consejo.py          # pide la pregunta interactivamente
"""

import json
import os
import sys
import webbrowser
from typing import Optional

import anthropic
from dotenv import load_dotenv

load_dotenv()

# ── Modelos ────────────────────────────────────────────────────────────────────
SONNET = "claude-sonnet-4-6"
OPUS = "claude-opus-4-7"

# ── Control de rondas ──────────────────────────────────────────────────────────
MIN_ROUNDS = 3
MAX_ROUNDS = 6

# ── Roles ──────────────────────────────────────────────────────────────────────
ROLES = [
    {
        "name": "Pragmático",
        "emoji": "⚙️",
        "color": "#3b82f6",
        "tagline": "Viabilidad · Recursos · Restricciones",
        "system": (
            "Eres el agente Pragmático en un consejo de deliberación estratégica. "
            "Tu perspectiva: viabilidad real, recursos disponibles, limitaciones prácticas. "
            "\n\nREGLA DE INTERACCIÓN (obligatoria): antes de exponer tu punto, reacciona "
            "explícitamente a la intervención más reciente del debate. Cita o parafrasea "
            "al agente por su nombre y di si estás de acuerdo, en desacuerdo o lo matizan. "
            "El debate debe progresar — no repitas lo ya dicho, construye sobre ello. "
            "\n\nTermina tu respuesta con exactamente una de estas líneas:\n"
            "[CONSENSO: SÍ] — el grupo tiene acuerdo suficiente para actuar.\n"
            "[CONSENSO: NO] — el debate debe continuar."
        ),
    },
    {
        "name": "Crítico",
        "emoji": "🔍",
        "color": "#ef4444",
        "tagline": "Riesgos · Errores · Puntos ciegos",
        "system": (
            "Eres el agente Crítico en un consejo de deliberación estratégica. "
            "Tu perspectiva: riesgos, errores de lógica, supuestos incorrectos, puntos ciegos. "
            "\n\nREGLA DE INTERACCIÓN (obligatoria): antes de exponer tu punto, identifica "
            "el argumento más débil o el riesgo más grave aún no señalado en el debate. "
            "Nombra al agente que lo dijo y explica exactamente qué puede fallar. "
            "No seas negativo por serlo — señala lo que hay que corregir para mejorar. "
            "\n\nTermina tu respuesta con exactamente una de estas líneas:\n"
            "[CONSENSO: SÍ] — el grupo tiene acuerdo suficiente para actuar.\n"
            "[CONSENSO: NO] — el debate debe continuar."
        ),
    },
    {
        "name": "Visionario",
        "emoji": "🔭",
        "color": "#10b981",
        "tagline": "Impacto · Largo plazo · Oportunidades",
        "system": (
            "Eres el agente Visionario en un consejo de deliberación estratégica. "
            "Tu perspectiva: impacto estratégico a largo plazo, oportunidades que se abren. "
            "\n\nREGLA DE INTERACCIÓN (obligatoria): antes de exponer tu visión, conecta "
            "explícitamente con el punto más prometedor que otro agente haya señalado. "
            "Nómbralo, amplíalo y eleva su alcance. El debate debe converger hacia algo mayor. "
            "\n\nTermina tu respuesta con exactamente una de estas líneas:\n"
            "[CONSENSO: SÍ] — el grupo tiene acuerdo suficiente para actuar.\n"
            "[CONSENSO: NO] — el debate debe continuar."
        ),
    },
    {
        "name": "Implementador",
        "emoji": "🛠️",
        "color": "#f59e0b",
        "tagline": "Pasos · Secuencia · Entregables",
        "system": (
            "Eres el agente Implementador en un consejo de deliberación estratégica. "
            "Tu perspectiva: traducir ideas en pasos concretos, quién hace qué y cuándo. "
            "\n\nREGLA DE INTERACCIÓN (obligatoria): antes de proponer pasos, sintetiza "
            "brevemente el acuerdo emergente del debate (nombra a los agentes y sus aportes) "
            "y luego concreta el plan. Tu turno debe acercar al grupo a una decisión accionable. "
            "\n\nTermina tu respuesta con exactamente una de estas líneas:\n"
            "[CONSENSO: SÍ] — el grupo tiene acuerdo suficiente para actuar.\n"
            "[CONSENSO: NO] — el debate debe continuar."
        ),
    },
]


# ── Lógica de agentes ──────────────────────────────────────────────────────────

def call_agent(client: anthropic.Anthropic, role: dict, transcript: str, question: str) -> str:
    if transcript:
        context = f"DEBATE HASTA AHORA:\n{transcript}"
    else:
        context = "DEBATE HASTA AHORA:\n(Primera intervención — no hay debate previo aún.)"

    user_content = (
        f"PREGUNTA ORIGINAL:\n{question}\n\n"
        f"{context}\n\n"
        f"Tu turno, {role['name']}. Reacciona primero a lo último dicho, "
        f"luego aporta tu perspectiva y avanza el debate hacia una solución. "
        f"Recuerda terminar con [CONSENSO: SÍ] o [CONSENSO: NO]."
    )

    resp = client.messages.create(
        model=SONNET,
        max_tokens=1500,
        system=role["system"],
        messages=[{"role": "user", "content": user_content}],
    )
    return resp.content[0].text.strip()


def has_consensus(response: str) -> bool:
    return "[CONSENSO: SÍ]" in response


def strip_consensus_tag(text: str) -> str:
    return (
        text
        .replace("[CONSENSO: SÍ]", "")
        .replace("[CONSENSO: NO]", "")
        .strip()
    )


def synthesize(client: anthropic.Anthropic, question: str, transcript: str, rounds: int, consensus: bool) -> str:
    status = (
        f"Consenso unánime alcanzado en ronda {rounds}."
        if consensus
        else f"Debate concluido tras {rounds} rondas (sin consenso unánime)."
    )
    system = (
        "Eres un sintetizador experto. Produces la solución final consolidada y accionable. "
        "Estructura tu respuesta EXACTAMENTE así:\n\n"
        "## CONCLUSIÓN PRINCIPAL\n"
        "(2-3 frases directas)\n\n"
        "## IDEAS CLAVE DEL DEBATE\n"
        "(bullets con los aportes más valiosos de cada perspectiva)\n\n"
        "## PLAN DE ACCIÓN\n"
        "(pasos numerados y ordenados)\n\n"
        "## RIESGOS A VIGILAR\n"
        "(bullets, solo si los hay)\n\n"
        "Sé directo. Sin rodeos. Sin repetir el debate completo."
    )
    resp = client.messages.create(
        model=OPUS,
        max_tokens=2000,
        system=system,
        messages=[{"role": "user", "content": (
            f"PREGUNTA: {question}\n\n"
            f"ESTADO: {status}\n\n"
            f"TRANSCRIPCIÓN COMPLETA:\n{transcript}\n\n"
            "Sintetiza y produce la solución final."
        )}],
    )
    return resp.content[0].text.strip()


# ── Dashboard HTML ─────────────────────────────────────────────────────────────

def _esc(text: str) -> str:
    """Escapa HTML básico preservando saltos de línea como <br>."""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("\n", "<br>")
    )


def _esc_pre(text: str) -> str:
    """Escapa HTML básico sin convertir saltos (para pre-wrap)."""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def generate_html(
    question: str,
    turns: list,
    synthesis: Optional[str],
    done: bool,
    round_num: int,
    consensus_reached: bool,
    active_agent: Optional[str] = None,
) -> str:
    role_map = {r["name"]: r for r in ROLES}
    progress_pct = min(100, int((round_num / MAX_ROUNDS) * 100))

    if done and consensus_reached:
        status_badge = '<span class="badge badge-ok">✓ Consenso alcanzado</span>'
    elif done:
        status_badge = '<span class="badge badge-warn">⚑ Máx. rondas alcanzado</span>'
    elif active_agent:
        status_badge = f'<span class="badge badge-running">⟳ {active_agent} razonando…</span>'
    else:
        status_badge = f'<span class="badge badge-running">⟳ Ronda {round_num} en curso</span>'

    # ── Tarjetas del debate ────────────────────────────────────────────────────
    cards_html = ""
    for turn in turns:
        r = role_map[turn["name"]]
        body = _esc(strip_consensus_tag(turn["response"]))
        c_icon = "✓ Consenso" if turn["voted_yes"] else "✗ Debate"
        c_cls = "yes" if turn["voted_yes"] else "no"
        cards_html += f"""
    <div class="card" style="border-left:4px solid {r['color']}">
      <div class="card-header">
        <span class="agent-name" style="color:{r['color']}">{r['emoji']} {r['name']}</span>
        <span class="agent-tag">{r['tagline']}</span>
        <span class="round-badge">R{turn['round']}</span>
        <span class="consensus-icon {c_cls}">{c_icon}</span>
      </div>
      <div class="card-body">{body}</div>
    </div>"""

    # ── Tarjeta "pensando" ─────────────────────────────────────────────────────
    thinking_html = ""
    if not done and active_agent and active_agent in role_map:
        r = role_map[active_agent]
        thinking_html = f"""
    <div class="card thinking" style="border-left:4px solid {r['color']}">
      <div class="card-header">
        <span class="agent-name" style="color:{r['color']}">{r['emoji']} {r['name']}</span>
        <span class="agent-tag">{r['tagline']}</span>
        <span class="round-badge">R{round_num}</span>
      </div>
      <div class="card-body dots"><span>●</span><span>●</span><span>●</span></div>
    </div>"""

    # ── Síntesis ───────────────────────────────────────────────────────────────
    synthesis_html = ""
    if synthesis:
        synthesis_html = f"""
  <section class="synthesis">
    <h2>⚡ Síntesis Final <span class="model-tag">Opus</span></h2>
    <div class="synthesis-body">{_esc_pre(synthesis)}</div>
  </section>"""

    # ── Leyenda de agentes ─────────────────────────────────────────────────────
    legend = "".join(
        f'<div class="agent-pill">'
        f'<div class="dot" style="background:{r["color"]}"></div>'
        f'{r["emoji"]} {r["name"]}'
        f'</div>'
        for r in ROLES
    )

    refresh_tag = "" if done else '<meta http-equiv="refresh" content="3">'
    footer_note = "Actualizando cada 3 s…" if not done else "Debate completado."

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  {refresh_tag}
  <title>Consejo Jeffrey</title>
  <style>
    * {{ box-sizing:border-box; margin:0; padding:0; }}
    body {{
      font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
      background:#0d0d1a; color:#e2e8f0;
      min-height:100vh; padding:28px 20px;
    }}
    header {{ max-width:860px; margin:0 auto 28px; }}
    .logo {{ font-size:11px; color:#6366f1; letter-spacing:3px;
             text-transform:uppercase; margin-bottom:14px; }}
    h1 {{ font-size:22px; font-weight:700; color:#f8fafc; margin-bottom:10px; }}
    .question {{
      font-size:15px; color:#94a3b8; line-height:1.65;
      padding:14px 18px; background:#1a1a2e; border-radius:8px;
      margin-bottom:18px; border-left:3px solid #6366f1;
    }}
    .meta {{ display:flex; align-items:center; gap:14px; flex-wrap:wrap; margin-bottom:18px; }}
    .badge {{
      font-size:12px; font-weight:600; padding:5px 12px;
      border-radius:20px; letter-spacing:0.3px; white-space:nowrap;
    }}
    .badge-running {{ background:#1e3a5f; color:#60a5fa; }}
    .badge-ok      {{ background:#064e3b; color:#34d399; }}
    .badge-warn    {{ background:#451a03; color:#fbbf24; }}
    .progress-wrap {{ flex:1; min-width:100px; }}
    .progress-bar  {{ background:#1a1a2e; border-radius:4px; height:5px; }}
    .progress-fill {{
      background:linear-gradient(90deg,#6366f1,#a78bfa);
      border-radius:4px; height:5px;
      width:{progress_pct}%; transition:width .6s ease;
    }}
    .round-info {{ font-size:12px; color:#475569; white-space:nowrap; }}
    .agents-legend {{ display:flex; gap:12px; flex-wrap:wrap; margin-bottom:28px; }}
    .agent-pill {{
      display:flex; align-items:center; gap:7px;
      font-size:12px; color:#94a3b8;
      padding:5px 12px; border-radius:20px; background:#1a1a2e;
    }}
    .dot {{ width:8px; height:8px; border-radius:50%; flex-shrink:0; }}
    .feed {{ max-width:860px; margin:0 auto; display:flex; flex-direction:column; gap:14px; }}
    .card {{
      background:#13132a; border-radius:10px; padding:18px 22px;
      animation:fadeIn .35s ease;
    }}
    @keyframes fadeIn {{ from {{ opacity:0; transform:translateY(8px); }} to {{ opacity:1; transform:translateY(0); }} }}
    .card-header {{
      display:flex; align-items:center; gap:10px;
      flex-wrap:wrap; margin-bottom:12px;
    }}
    .agent-name {{ font-weight:700; font-size:14px; }}
    .agent-tag  {{ font-size:11px; color:#475569; flex:1; }}
    .round-badge {{
      font-size:11px; color:#475569;
      background:#1a1a2e; padding:2px 8px; border-radius:10px;
    }}
    .consensus-icon {{
      font-size:11px; font-weight:600;
      padding:2px 9px; border-radius:10px;
    }}
    .consensus-icon.yes {{ background:#064e3b; color:#34d399; }}
    .consensus-icon.no  {{ background:#4c1d1d; color:#f87171; }}
    .card-body {{ font-size:14px; line-height:1.75; color:#cbd5e1; }}
    .thinking {{ opacity:.55; }}
    .dots span {{
      display:inline-block; animation:pulse 1.4s infinite;
      font-size:18px; margin-right:4px;
    }}
    .dots span:nth-child(2) {{ animation-delay:.2s; }}
    .dots span:nth-child(3) {{ animation-delay:.4s; }}
    @keyframes pulse {{ 0%,80%,100% {{ opacity:.1; }} 40% {{ opacity:1; }} }}
    .synthesis {{
      max-width:860px; margin:28px auto 0;
      background:#13132a;
      border:1px solid #6366f1; border-radius:12px; padding:28px;
      animation:fadeIn .4s ease;
    }}
    .synthesis h2 {{
      font-size:17px; color:#a78bfa; margin-bottom:20px;
      display:flex; align-items:center; gap:10px;
    }}
    .model-tag {{
      font-size:11px; background:#1a1a2e; color:#818cf8;
      padding:2px 9px; border-radius:10px; font-weight:400;
    }}
    .synthesis-body {{
      font-size:14px; line-height:1.8; color:#e2e8f0; white-space:pre-wrap;
    }}
    .footer-note {{
      text-align:center; font-size:11px; color:#2d3748; margin:24px auto;
    }}
  </style>
</head>
<body>
  <header>
    <div class="logo">Jeffrey · Consejo Multi-Agente</div>
    <h1>Debate estratégico</h1>
    <div class="question">{_esc(question)}</div>
    <div class="meta">
      {status_badge}
      <div class="progress-wrap">
        <div class="progress-bar"><div class="progress-fill"></div></div>
      </div>
      <span class="round-info">Ronda {round_num} / {MAX_ROUNDS} · mín. {MIN_ROUNDS}</span>
    </div>
    <div class="agents-legend">{legend}</div>
  </header>

  <div class="feed">
    {cards_html}
    {thinking_html}
  </div>

  {synthesis_html}

  <p class="footer-note">{footer_note}</p>
</body>
</html>"""


def write_dashboard(
    question: str,
    turns: list,
    synthesis: Optional[str],
    done: bool,
    round_num: int,
    consensus_reached: bool,
    active_agent: Optional[str] = None,
) -> str:
    tmp = os.path.join(os.path.dirname(__file__), "..", ".tmp")
    os.makedirs(tmp, exist_ok=True)
    path = os.path.join(tmp, "consejo_live.html")
    html = generate_html(question, turns, synthesis, done, round_num, consensus_reached, active_agent)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return os.path.abspath(path)


# ── Orquestador ────────────────────────────────────────────────────────────────

def run_council(question: str) -> None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY no encontrada en .env")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    turns = []
    round_num = 0
    consensus_reached = False
    transcript = ""

    # Dashboard inicial + abrir navegador
    path = write_dashboard(question, turns, None, False, 0, False)
    webbrowser.open(f"file://{path}")
    print(f"\nDashboard: file://{path}")
    print(f"\nPREGUNTA: {question}\n")

    while round_num < MAX_ROUNDS:
        round_num += 1
        print(f"\n── RONDA {round_num} ──")

        round_votes = []

        for role in ROLES:
            print(f"  [{role['name']}] pensando…", flush=True)

            # Mostrar "pensando" en dashboard
            write_dashboard(question, turns, None, False, round_num, False, active_agent=role["name"])

            response = call_agent(client, role, transcript, question)
            voted_yes = has_consensus(response)
            round_votes.append(voted_yes)

            transcript += (
                f"\n\n{'─' * 44}\n"
                f"{role['name']} — Ronda {round_num}\n"
                f"{'─' * 44}\n"
                f"{response}"
            )
            turns.append({
                "name": role["name"],
                "round": round_num,
                "response": response,
                "voted_yes": voted_yes,
            })

            # Actualizar dashboard con la nueva tarjeta
            write_dashboard(question, turns, None, False, round_num, False, active_agent=None)

            icon = "✓" if voted_yes else "✗"
            print(f"  {icon} {role['name']} completado")

        yes_count = sum(round_votes)
        print(f"  Votos consenso: {yes_count}/{len(ROLES)}")

        if all(round_votes) and round_num >= MIN_ROUNDS:
            print(f"\n✓ Consenso unánime en ronda {round_num}.")
            consensus_reached = True
            break

    if not consensus_reached:
        print(f"\nMáximo de rondas ({MAX_ROUNDS}) alcanzado.")

    print("\nSintetizando con Opus…")
    write_dashboard(question, turns, None, False, round_num, consensus_reached, active_agent="Opus (síntesis)")

    synthesis = synthesize(client, question, transcript, round_num, consensus_reached)
    print("\n" + synthesis)

    # Dashboard final con síntesis
    write_dashboard(question, turns, synthesis, True, round_num, consensus_reached)

    # JSON
    tmp = os.path.join(os.path.dirname(__file__), "..", ".tmp")
    out_path = os.path.join(tmp, "consejo_output.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "question": question,
            "rounds_completed": round_num,
            "consensus_reached": consensus_reached,
            "agents": [r["name"] for r in ROLES],
            "transcript": transcript,
            "synthesis": synthesis,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n[Dashboard final: file://{path}]")
    print(f"[JSON guardado: .tmp/consejo_output.json]")


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        print("Escribe la pregunta para el consejo:")
        question = input("> ").strip()

    if not question:
        print("ERROR: pregunta vacía.")
        sys.exit(1)

    run_council(question)
