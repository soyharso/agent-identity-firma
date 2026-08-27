# agent-identity-firma

Componente mínimo de identidad de agente sobre Google Cloud: un agente que firma el cierre de una
petición **sin poder firmar como persona**. Nació el 2026-08-27 como sujeto de un experimento
medido sobre el método (`clev-transferencia-metodo`), no como producto.

**Estado: no funciona.** El agente nunca llegó a firmar. `roles/owner` sobre el proyecto no
incluye `iam.serviceAccounts.signJwt`, y el diseño —congelado a propósito, sin corregir— no
contempla a nadie con ese permiso. El detalle, con horas y códigos de error, está en el informe
del experimento, fuera de este repositorio.

## Qué hay aquí

| Archivo | Qué hace | Estado |
|---|---|---|
| `src/firmar_agente.py` | pide a Google que firme un sobre con la clave del service account. | falla con 403. |
| `src/firmar_humano.py` | firma con el `id_token` de la persona. | funciona, pero el sobre sale sin `estado` ni hash: Google no admite claims propios. |
| `src/verificar.py` | comprueba la firma contra las claves públicas y aplica la política de rol. | funciona para el sobre humano. |

## Cómo se corre

```bash
pip install google-auth requests 'pyjwt[crypto]'
python3 src/firmar_humano.py --peticion PET-001 --estado cerrada --texto-archivo libro/curacion.md
python3 src/verificar.py libro/firmas.jsonl
```

Requiere `gcloud` autenticado y el proyecto `ai-transf-lab-0827` (o cambiar la constante en
`src/firmar_agente.py`).

## Lo que se aprendió chocando

- La **Agent Identity API** de Google trata de autorizaciones OAuth de agentes hacia recursos de
  terceros. No emite clave de firma propia al agente.
- El **Agent Registry** sí existe y acepta registrar un agente que no está desplegado: devuelve un
  identificador estable. No tiene campo para atar ese agente a un service account.
- El `id_token` de una persona **no admite claims propios**, así que no puede llevar qué se
  cerró ni el hash de lo cerrado.

Privado. No publicado. Sin datos de personas ni de casos reales.
