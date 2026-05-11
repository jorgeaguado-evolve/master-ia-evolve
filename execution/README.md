# Execution

Scripts Python deterministas. Cada script hace una sola cosa y la hace bien.

## Reglas

- Credenciales y API keys se leen de `.env` (nunca hardcodear).
- Antes de crear un script nuevo, verificar que no exista uno equivalente.
- Cada script debe ser invocable de forma aislada: `python execution/<script>.py [args]`.
- Salida intermedia → `.tmp/`. Entregables finales → cloud.
