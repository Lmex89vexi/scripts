# Pull Request Checklist (OBLIGATORIO)

## 🔐 Seguridad y Calidad
- [ ] No hay logs con información sensible (RFC, CURP, tokens, headers completos, payloads crudos).
- [ ] No hay secretos hardcodeados (API keys, passwords, tokens, certificados).
- [ ] Los secretos se obtienen vía variables de entorno o secret manager.
- [ ] No hay `except Exception: pass` ni errores silenciosos.
- [ ] Los errores se propagan o se manejan explícitamente.
- [ ] No se usan nombres de variables genéricos (`data`, `temp`, `aux`) sin contexto explícito.
- [ ] Se sigue la convención de nomenclatura `snake_case` según el estándar del repositorio.
- [ ] Las funciones tienen un solo propósito y no exceden 50 líneas.

