#!/usr/bin/env python3
"""
trim.py — Sistema de salud de archivos base de Jeffrey.

Uso:
  python trim.py                  # Analiza y genera reporte + registra uso
  python trim.py --solo-reporte   # Solo genera reporte, sin registrar uso
  python trim.py --registrar-uso ARCHIVO1 ARCHIVO2 ...  # Solo registra uso
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = Path(__file__).parent / "trim_config.json"
REPORT_PATH = BASE_DIR / ".tmp" / "trim_report.md"
USAGE_PATH = BASE_DIR / ".tmp" / "trim_usage.json"


def cargar_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


# ───────────────────────────────────────────────────────────
# 1. Calcular tokens por sección
# ───────────────────────────────────────────────────────────

def calcular_tokens_por_seccion(ruta_relativa: str) -> list[dict]:
    """Divide un archivo por cabeceras ## y estima tokens (~4 chars = 1 token)."""
    path = BASE_DIR / ruta_relativa
    if not path.exists():
        return []

    texto = path.read_text(encoding="utf-8")
    secciones = []
    partes = re.split(r"(?m)^(#{1,3} .+)$", texto)

    seccion_actual = "(preámbulo)"
    buffer = []

    for parte in partes:
        if re.match(r"^#{1,3} .+$", parte):
            if buffer:
                contenido = "\n".join(buffer).strip()
                secciones.append({
                    "archivo": ruta_relativa,
                    "seccion": seccion_actual,
                    "lineas": contenido.count("\n") + 1 if contenido else 0,
                    "chars": len(contenido),
                    "tokens_est": max(1, len(contenido) // 4),
                })
            seccion_actual = parte.strip()
            buffer = []
        else:
            buffer.append(parte)

    if buffer:
        contenido = "\n".join(buffer).strip()
        if contenido:
            secciones.append({
                "archivo": ruta_relativa,
                "seccion": seccion_actual,
                "lineas": contenido.count("\n") + 1,
                "chars": len(contenido),
                "tokens_est": max(1, len(contenido) // 4),
            })

    return secciones


# ───────────────────────────────────────────────────────────
# 2. Aplicar heurísticas
# ───────────────────────────────────────────────────────────

def aplicar_heuristicas(config: dict) -> list[dict]:
    """Detecta candidatos automáticos: edge cases, tablas, ejemplos, duplicados."""
    umbrales = config["umbrales"]
    candidatos = []

    todas_secciones: dict[str, str] = {}  # "archivo::seccion" → contenido

    for ruta in config["archivos_a_analizar"]:
        path = BASE_DIR / ruta
        if not path.exists():
            continue
        texto = path.read_text(encoding="utf-8")
        partes = re.split(r"(?m)^(#{1,3} .+)$", texto)

        seccion_actual = "(preámbulo)"
        buffer = []

        for parte in partes:
            if re.match(r"^#{1,3} .+$", parte):
                if buffer:
                    contenido = "\n".join(buffer).strip()
                    clave = f"{ruta}::{seccion_actual}"
                    todas_secciones[clave] = contenido
                    _evaluar_seccion(ruta, seccion_actual, contenido, umbrales, candidatos)
                seccion_actual = parte.strip()
                buffer = []
            else:
                buffer.append(parte)

        if buffer:
            contenido = "\n".join(buffer).strip()
            if contenido:
                clave = f"{ruta}::{seccion_actual}"
                todas_secciones[clave] = contenido
                _evaluar_seccion(ruta, seccion_actual, contenido, umbrales, candidatos)

    # Detectar secciones duplicadas entre archivos
    _detectar_duplicados(todas_secciones, candidatos)

    return candidatos


def _evaluar_seccion(ruta, seccion, contenido, umbrales, candidatos):
    lineas = contenido.count("\n") + 1 if contenido else 0
    nombre_lower = seccion.lower()

    if "edge case" in nombre_lower and lineas > umbrales["edge_cases_max_lineas"]:
        candidatos.append({
            "archivo": ruta,
            "seccion": seccion,
            "motivo": f"Edge cases con {lineas} líneas (umbral: {umbrales['edge_cases_max_lineas']})",
            "accion": "Extraer a directiva específica del dominio",
        })
        return

    filas_tabla = len(re.findall(r"(?m)^\|.+\|$", contenido))
    if filas_tabla > umbrales["tabla_max_filas"] + 2:  # +2 por cabecera y separador
        candidatos.append({
            "archivo": ruta,
            "seccion": seccion,
            "motivo": f"Tabla con {filas_tabla - 2} filas de contenido (umbral: {umbrales['tabla_max_filas']})",
            "accion": "Extraer a archivo de referencia",
        })
        return

    if ("ejemplo" in nombre_lower or "example" in nombre_lower) and lineas > umbrales["ejemplo_max_lineas"]:
        candidatos.append({
            "archivo": ruta,
            "seccion": seccion,
            "motivo": f"Bloque de ejemplos con {lineas} líneas (umbral: {umbrales['ejemplo_max_lineas']})",
            "accion": "Extraer a apéndice o directiva",
        })


def _detectar_duplicados(secciones: dict[str, str], candidatos: list):
    claves = list(secciones.keys())
    for i in range(len(claves)):
        for j in range(i + 1, len(claves)):
            a, b = claves[i], claves[j]
            ca, cb = secciones[a], secciones[b]
            if len(ca) < 80 or len(cb) < 80:
                continue
            # Similitud simple: palabras comunes / total palabras
            pa = set(ca.lower().split())
            pb = set(cb.lower().split())
            if not pa or not pb:
                continue
            similitud = len(pa & pb) / max(len(pa), len(pb))
            if similitud > 0.75:
                archivo_a = a.split("::")[0]
                archivo_b = b.split("::")[0]
                if archivo_a != archivo_b:
                    candidatos.append({
                        "archivo": archivo_a,
                        "seccion": a.split("::", 1)[1],
                        "motivo": f"Sección muy similar ({int(similitud*100)}%) a '{b.split('::', 1)[1]}' en {archivo_b}",
                        "accion": f"Consolidar en un archivo y referenciar desde el otro",
                    })


# ───────────────────────────────────────────────────────────
# 3. Validar integridad referencial
# ───────────────────────────────────────────────────────────

def validar_integridad_referencial(config: dict) -> list[dict]:
    """Extrae links [texto](ruta) de archivos base y verifica que los destinos existen."""
    rotos = []
    link_re = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    for ruta in config["archivos_a_analizar"]:
        path = BASE_DIR / ruta
        if not path.exists():
            continue
        texto = path.read_text(encoding="utf-8")
        for match in link_re.finditer(texto):
            texto_link, destino = match.group(1), match.group(2)
            if destino.startswith("http://") or destino.startswith("https://"):
                continue
            destino_limpio = destino.split("#")[0]
            if not destino_limpio:
                continue
            destino_path = (BASE_DIR / ruta).parent / destino_limpio
            if not destino_path.exists():
                # También intentar desde BASE_DIR
                destino_path2 = BASE_DIR / destino_limpio
                if not destino_path2.exists():
                    rotos.append({
                        "origen": ruta,
                        "texto": texto_link,
                        "destino": destino,
                    })

    return rotos


# ───────────────────────────────────────────────────────────
# 4. Registrar uso
# ───────────────────────────────────────────────────────────

def registrar_uso(archivos_leidos: list[str]):
    """Añade entrada a .tmp/trim_usage.json con timestamp y archivos leídos."""
    USAGE_PATH.parent.mkdir(parents=True, exist_ok=True)

    datos = []
    if USAGE_PATH.exists():
        try:
            datos = json.loads(USAGE_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            datos = []

    datos.append({
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "archivos_leidos": archivos_leidos,
    })

    USAGE_PATH.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[trim] Uso registrado: {len(archivos_leidos)} archivos en {USAGE_PATH}")


# ───────────────────────────────────────────────────────────
# 5. Generar reporte
# ───────────────────────────────────────────────────────────

def generar_reporte(config: dict, candidatos: list, rotos: list, secciones_por_archivo: list):
    """Escribe .tmp/trim_report.md con candidatos, links rotos y top secciones por tokens."""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    protegidos = set(config["archivos_protegidos"])
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

    lineas = [
        f"# Trim Report — {fecha}",
        "",
        "---",
        "",
    ]

    # Sección: candidatos automáticos
    lineas.append("## Candidatos a extraer")
    lineas.append("")

    protegidos_cands = [c for c in candidatos if c["archivo"] in protegidos]
    libres_cands = [c for c in candidatos if c["archivo"] not in protegidos]

    if libres_cands:
        lineas.append("### Archivos modificables (requieren confirmación)")
        lineas.append("")
        for c in libres_cands:
            lineas.append(f"- **{c['archivo']}** › `{c['seccion']}`")
            lineas.append(f"  - Motivo: {c['motivo']}")
            lineas.append(f"  - Acción: {c['accion']}")
            lineas.append("")
    else:
        lineas.append("_No hay candidatos automáticos en archivos modificables._")
        lineas.append("")

    if protegidos_cands:
        lineas.append("### Archivos protegidos (solo revisión manual por Jorge)")
        lineas.append("")
        for c in protegidos_cands:
            lineas.append(f"- **{c['archivo']}** › `{c['seccion']}`")
            lineas.append(f"  - Motivo: {c['motivo']}")
            lineas.append(f"  - Acción sugerida: {c['accion']}")
            lineas.append("")

    lineas.append("---")
    lineas.append("")

    # Sección: links rotos
    lineas.append("## Links rotos")
    lineas.append("")
    if rotos:
        for r in rotos:
            lineas.append(f"- `{r['origen']}` → [{r['texto']}]({r['destino']}) — **destino no encontrado**")
        lineas.append("")
    else:
        lineas.append("_Todos los links están correctos._")
        lineas.append("")

    lineas.append("---")
    lineas.append("")

    # Sección: top secciones por peso en tokens
    lineas.append("## Top secciones por peso (tokens estimados)")
    lineas.append("")
    todas = sorted(secciones_por_archivo, key=lambda x: x["tokens_est"], reverse=True)[:15]
    if todas:
        lineas.append("| Archivo | Sección | Tokens est. | Líneas |")
        lineas.append("|---------|---------|-------------|--------|")
        for s in todas:
            lineas.append(f"| {s['archivo']} | {s['seccion']} | {s['tokens_est']} | {s['lineas']} |")
        lineas.append("")

    # Resumen de archivos analizados
    lineas.append("---")
    lineas.append("")
    lineas.append("## Resumen de archivos")
    lineas.append("")
    archivos_analizados = {}
    for s in secciones_por_archivo:
        arch = s["archivo"]
        if arch not in archivos_analizados:
            archivos_analizados[arch] = {"tokens": 0, "secciones": 0}
        archivos_analizados[arch]["tokens"] += s["tokens_est"]
        archivos_analizados[arch]["secciones"] += 1

    lineas.append("| Archivo | Tokens est. | Secciones | Protegido |")
    lineas.append("|---------|-------------|-----------|-----------|")
    for arch, datos in sorted(archivos_analizados.items(), key=lambda x: x[1]["tokens"], reverse=True):
        prot = "✓" if arch in protegidos else ""
        lineas.append(f"| {arch} | {datos['tokens']} | {datos['secciones']} | {prot} |")

    REPORT_PATH.write_text("\n".join(lineas), encoding="utf-8")
    print(f"[trim] Reporte generado en {REPORT_PATH}")


# ───────────────────────────────────────────────────────────
# MAIN
# ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Jeffrey trim — salud de archivos base")
    parser.add_argument("--solo-reporte", action="store_true", help="Solo genera reporte, no registra uso")
    parser.add_argument("--registrar-uso", nargs="*", metavar="ARCHIVO", help="Solo registra uso con la lista de archivos")
    args = parser.parse_args()

    config = cargar_config()

    # Modo: solo registrar uso
    if args.registrar_uso is not None:
        registrar_uso(args.registrar_uso)
        return

    # Recopilar todas las secciones
    todas_secciones = []
    for ruta in config["archivos_a_analizar"]:
        todas_secciones.extend(calcular_tokens_por_seccion(ruta))

    # Analizar
    candidatos = aplicar_heuristicas(config)
    rotos = validar_integridad_referencial(config)

    # Generar reporte
    generar_reporte(config, candidatos, rotos, todas_secciones)

    # Registrar uso (salvo --solo-reporte)
    if not args.solo_reporte:
        archivos_leidos = [r for r in config["archivos_a_analizar"] if (BASE_DIR / r).exists()]
        registrar_uso(archivos_leidos)

    # Mostrar resumen en stdout
    n_cands = len(candidatos)
    n_rotos = len(rotos)
    print(f"[trim] Candidatos detectados: {n_cands} | Links rotos: {n_rotos}")
    if n_cands > 0:
        print("[trim] Candidatos:")
        for c in candidatos:
            prot = " [PROTEGIDO]" if c["archivo"] in set(config["archivos_protegidos"]) else ""
            print(f"  - {c['archivo']} › {c['seccion']}{prot}")
            print(f"    {c['motivo']}")
    if n_rotos > 0:
        print("[trim] Links rotos:")
        for r in rotos:
            print(f"  - {r['origen']} → {r['destino']}")


if __name__ == "__main__":
    main()
