# Pull Request Checklist (OBLIGATORIO)

## 🔐 Seguridad y Calidad
- [ ] No hay logs con información sensible (RFC, CURP, tokens, headers completos, payloads crudos).
- [ ] No hay secretos hardcodeados (API keys, passwords, tokens, certificados).
- [ ] Los secretos se obtienen vía variables de entorno o secret manager.
- [ ] No hay `except Exception: pass` ni errores silenciosos.
- [ ] Los errores se propagan o se manejan explícitamente.

## 🧠 Calidad de Código
- [ ] No se usan nombres de variables genéricos (`data`, `temp`, `aux`) sin contexto explícito.
- [ ] Se sigue la convención de nomenclatura `snake_case` según el estándar del repositorio.
- [ ] Las funciones tienen un solo propósito y no exceden 50 líneas.

## 🧪 QA / Tooling
- [ ] SonarQube: 0 issues críticas/bloqueantes y menos de 10 issues totales en QA.
- [ ] No existen conflictos de merge con la rama destino.
- [ ] No existen conflictos de merge con la rama destino.