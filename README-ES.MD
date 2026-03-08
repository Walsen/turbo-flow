# 🚀 Turbo Flow v4.0 — La Migración a Ruflo

<div align="center">

![Versión](https://img.shields.io/badge/versión-4.0.0-blue?style=for-the-badge)
![Ruflo](https://img.shields.io/badge/Ruflo-v3.5-purple?style=for-the-badge)
![MCP Tools](https://img.shields.io/badge/MCP_Tools-215+-green?style=for-the-badge)
![Plugins](https://img.shields.io/badge/Plugins-6-critical?style=for-the-badge)
![Licencia](https://img.shields.io/badge/licencia-MIT-orange?style=for-the-badge)

**⚡ Entorno de Desarrollo Agéntico Completo — Ruflo v3.5 + Beads + Worktrees + Agent Teams ⚡**

[Inicio Rápido](#-inicio-rápido) • [Instalación](#-qué-se-instala) • [Plugins](#-plugins-6) • [Comandos](#️-comandos-principales) • [Migración](#-migración-desde-v3x) • [Recursos](#-recursos)

</div>

---

## 🆕 Novedades en v4.0.0

| Métrica | v3.4.1 | v4.0.0 | Cambio |
|---------|--------|--------|--------|
| Pasos de Instalación | 15 | **10** | -5 (consolidados) |
| Paquetes Core | 4 separados | **1 (Ruflo)** | -75% |
| Herramientas MCP | 175+ | **215+** | +23% |
| Agentes | 60+ | **60+** | — |
| Plugins | 15 | **6** | -9 (redundantes eliminados) |
| Memoria entre sesiones | Ninguna | **Beads** | ⭐ Nuevo |
| Aislamiento de agentes | Ninguno | **Git Worktrees** | ⭐ Nuevo |
| Grafo de código | Ninguno | **GitNexus** | ⭐ Nuevo |
| Skill UI/UX | ✓ | **✓** | Mantenida |
| Statusline | ✓ | **✓** | Actualizada a 4.0 |

### Cambios Principales

- ✅ **claude-flow → Ruflo v3.5** — Un solo `npx ruflo@latest init` reemplaza 4 instalaciones separadas
- ✅ **Beads** — Memoria entre sesiones vía JSONL nativo de git
- ✅ **GitNexus** — Grafo de conocimiento del código con servidor MCP y detección de radio de impacto
- ✅ **Git Worktrees nativos** — Aislamiento por agente con namespacing automático de PG Vector
- ✅ **Native Agent Teams** — Equipos de agentes experimentales de Anthropic
- ✅ **6 plugins enfocados** — Eliminados 9 plugins redundantes o de dominio específico
- ✅ **OpenSpec** — Desarrollo dirigido por especificaciones
- ✅ **UI UX Pro Max** — Skill de diseño mantenida
- ✅ **Statusline Pro v4.0** — Actualizada con branding TF 4.0

### Eliminado (redundante con Ruflo v3.5 o fuera de alcance)

- `claude-flow@alpha`, `@ruvector/cli`, `@ruvector/sona`, `@claude-flow/browser` → bundled en Ruflo
- 9 plugins: healthcare-clinical, financial-risk, legal-contracts, cognitive-kernel, hyperbolic-reasoning, quantum-optimizer, neural-coordination, prime-radiant, ruvector-upstream
- Claudish, Agentic Jujutsu, Spec-Kit, agtrace, PAL MCP → bundled o redundante
- HeroUI + Tailwind + TypeScript scaffold → fuera de alcance
- Ars Contexta, OpenClaw Secure Stack → fuera de alcance

---

## 🏗️ Arquitectura

```
╔══════════════════════════════════════════════════════════════════════╗
║                       🚀 TURBO FLOW v4.0                            ║
╠══════════════════════════════════════════════════════════════════════╣
║  🖥️  INTERFAZ                                                        ║
║  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                  ║
║  │ Claude Code  │ │  Open WebUI  │ │  Statusline  │                  ║
║  │     CLI      │ │  (4 instanc) │ │   Pro v4.0   │                  ║
║  └──────────────┘ └──────────────┘ └──────────────┘                  ║
╠══════════════════════════════════════════════════════════════════════╣
║  🎯 ORQUESTACIÓN: Ruflo v3.5                                        ║
║  60+ Agentes │ 215+ Herramientas MCP │ Skills auto-activadas        ║
║  AgentDB v3 │ RuVector WASM │ SONA │ Routing 3 niveles             ║
║  59 MCP Browser Tools │ Observabilidad │ Gating                     ║
╠══════════════════════════════════════════════════════════════════════╣
║  🔌 PLUGINS (6)                                                      ║
║  ┌──────────────────────────────────────────────────────────────┐    ║
║  │ Agentic QE │ Code Intel │ Test Intel │ Perf │ Teammate │ Gas│    ║
║  └──────────────────────────────────────────────────────────────┘    ║
╠══════════════════════════════════════════════════════════════════════╣
║  🧠 INTELIGENCIA DE CÓDIGO: GitNexus                                 ║
║  Grafo de conocimiento │ Radio de impacto │ Servidor MCP            ║
╠══════════════════════════════════════════════════════════════════════╣
║  💾 MEMORIA (Tres Niveles)                                           ║
║  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                ║
║  │    Beads     │ │ Native Tasks │ │   AgentDB    │                  ║
║  │  proyecto/git│ │   sesión     │ │  + RuVector  │                  ║
║  │    JSONL     │ │  ~/.claude/  │ │  WASM accel  │                  ║
║  └──────────────┘ └──────────────┘ └──────────────┘                  ║
╠══════════════════════════════════════════════════════════════════════╣
║  🌳 AISLAMIENTO                                                     ║
║  Git Worktrees por agente │ Schema PG Vector por worktree           ║
║  Auto-indexación GitNexus │ Agent Teams (experimental)              ║
╠══════════════════════════════════════════════════════════════════════╣
║  🎨 SKILLS                                                          ║
║  UI UX Pro Max │ OpenSpec │ 36+ skills auto-activadas de Ruflo      ║
╠══════════════════════════════════════════════════════════════════════╣
║  🏗️  INFRAESTRUCTURA                                                ║
║  DevPod │ Codespaces │ Rackspace Spot                               ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 🏁 Inicio Rápido

### 📦 Instalación de DevPod

<details>
<summary><b>macOS</b></summary>

```bash
brew install loft-sh/devpod/devpod
```
</details>

<details>
<summary><b>Windows</b></summary>

```bash
choco install devpod
```
</details>

<details>
<summary><b>Linux</b></summary>

```bash
curl -L -o devpod "https://github.com/loft-sh/devpod/releases/latest/download/devpod-linux-amd64"
sudo install devpod /usr/local/bin
```
</details>

### 🚀 Lanzar

```bash
# DevPod (recomendado)
devpod up https://github.com/marcuspat/turbo-flow --ide vscode

# Codespaces
# Push a GitHub → Abrir en Codespace → ejecuta automáticamente

# Manual
git clone https://github.com/marcuspat/turbo-flow -b main
cd turbo-flow/v4
chmod +x .devcontainer/setup-turboflow-4.sh
./.devcontainer/setup-turboflow-4.sh
source ~/.bashrc
turbo-status
```

---

## 📦 Qué Se Instala

El script `setup-turboflow-4.sh` instala la pila completa en **10 pasos automatizados**:

### Paso 1: Prerequisitos del Sistema

| Paquete | Propósito |
|:--------|:----------|
| `build-essential` | Compilador C/C++ (gcc, g++, make) |
| `python3` | Runtime de Python |
| `git` | Control de versiones |
| `curl` | Cliente HTTP |
| `jq` | Procesador JSON (requerido para statusline) |
| `Node.js 20+` | Runtime de JavaScript (requerido por Ruflo v3.5) |

### Paso 2: Claude Code + Ruflo v3.5

| Componente | Propósito |
|:-----------|:----------|
| `Claude Code` | CLI de codificación agéntica de Anthropic |
| `Ruflo v3.5` | Motor de orquestación — reemplaza claude-flow@alpha |
| Ruflo MCP | Registrado como servidor MCP en Claude Code |
| Ruflo Doctor | Diagnóstico automático y corrección |

> Ruflo v3.5 incluye: AgentDB v3, RuVector WASM, SONA, 215 herramientas MCP, 60+ agentes, sistema de skills, routing de modelos en 3 niveles, 59 herramientas MCP de navegador, observabilidad, gating

### Paso 3: Plugins de Ruflo (6)

| Plugin | Propósito |
|:-------|:----------|
| **Agentic QE** | 58 agentes QE — TDD, cobertura, escaneo de seguridad, chaos engineering |
| **Code Intelligence** | Análisis de código, detección de patrones, sugerencias de refactoring |
| **Test Intelligence** | Generación de tests, análisis de brechas, detección de tests inestables |
| **Perf Optimizer** | Profiling de rendimiento, detección de cuellos de botella |
| **Teammate Plugin** | Puente entre Native Agent Teams y swarms de Ruflo (21 herramientas MCP) |
| **Gastown Bridge** | Orquestación acelerada por WASM, sincronización con Beads (20 herramientas MCP) |

Además instala **OpenSpec** (`@fission-ai/openspec`) para desarrollo dirigido por especificaciones.

### Paso 4: UI UX Pro Max Skill

| Componente | Propósito |
|:-----------|:----------|
| `uipro-cli` | Skill de diseño — patrones de componentes, accesibilidad, layouts responsivos, tokens de diseño |

### Paso 5: GitNexus (Grafo de Conocimiento del Código)

| Componente | Propósito |
|:-----------|:----------|
| `GitNexus` | Indexa dependencias, cadenas de llamadas, flujos de ejecución |
| GitNexus MCP | Registrado como servidor MCP — detección de radio de impacto |

### Paso 6: Beads (Memoria entre Sesiones)

| Componente | Propósito |
|:-----------|:----------|
| `beads-cli` | Memoria de proyecto en JSONL nativo de git — issues, decisiones, bloqueos |

### Paso 7: Workspace + Agent Teams

| Componente | Propósito |
|:-----------|:----------|
| Directorios | `src/` `tests/` `docs/` `scripts/` `config/` `plans/` |
| Agent Teams | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` habilitado |

### Paso 8: Statusline Pro v4.0

Statusline de 3 líneas con 15 componentes:

```
LÍNEA 1: [Project] nombre | [Model] Sonnet | [Git] branch | [TF] 4.0 | [SID] abc123
LÍNEA 2: [Tokens] 50k/200k | [Ctx] #######--- 65% | [Cache] 42% | [Cost] $1.23 | [Time] 5m
LÍNEA 3: [+150] [-50] | [READY]
```

### Paso 9: Generación de CLAUDE.md

Genera el archivo de contexto del workspace con:
- Protocolo de memoria de 3 niveles (Beads → Native Tasks → AgentDB)
- Reglas de aislamiento (un worktree por agente)
- Reglas de Agent Teams (máx 3 compañeros, profundidad de recursión 2)
- Niveles de routing de modelos (Opus/Sonnet/Haiku)
- Referencia de plugins
- Guardrails de costo ($15/hr)

### Paso 10: Aliases + Entorno + Registro MCP

Más de 50 aliases organizados por familia: `rf-*`, `ruv-*`, `mem-*`, `bd-*`, `wt-*`, `gnx-*`, `aqe-*`, `os-*`, `hooks-*`, `neural-*`, `turbo-status`, `turbo-help`

---

## 🔌 Plugins (6)

| Plugin | Herramientas MCP | Propósito |
|:-------|:-----------------|:----------|
| **Agentic QE** | 16 | 58 agentes QE, TDD, cobertura, seguridad, chaos engineering |
| **Code Intelligence** | — | Análisis de código, patrones, refactoring |
| **Test Intelligence** | — | Generación de tests, brechas, tests inestables |
| **Perf Optimizer** | — | Profiling, cuellos de botella, optimización |
| **Teammate Plugin** | 21 | Puente Agent Teams ↔ Ruflo swarms, routing semántico |
| **Gastown Bridge** | 20 | Orquestación WASM, sincronización Beads, convoys |

### Plugins Eliminados (9)

| Plugin | Razón |
|:-------|:------|
| healthcare-clinical | Dominio específico (HIPAA/FHIR) — no necesario |
| financial-risk | Dominio específico (PCI-DSS/SOX) — no necesario |
| legal-contracts | Dominio específico — no necesario |
| cognitive-kernel | Redundante con sistema neural de Ruflo |
| hyperbolic-reasoning | Redundante con embeddings hiperbólicos de RuVector WASM |
| quantum-optimizer | Redundante con EWC++ y RVFOptimizer de Ruflo |
| neural-coordination | Redundante con coordinación de swarms de Ruflo |
| prime-radiant | Nicho — interpretabilidad matemática |
| ruvector-upstream | Redundante — RuVector bundled en Ruflo v3.5 |

---

## ⌨️ Comandos Principales

<details>
<summary><b>📊 Estado y Ayuda</b></summary>

```bash
turbo-status         # Verificar todos los componentes
turbo-help           # Referencia completa de comandos
rf-doctor            # Verificación de salud de Ruflo
rf-plugins           # Listar plugins instalados
```
</details>

<details>
<summary><b>🎯 Orquestación (Ruflo)</b></summary>

```bash
rf-wizard            # Configuración interactiva
rf-swarm             # Swarm jerárquico (8 agentes máx)
rf-mesh              # Swarm en mesh
rf-ring              # Swarm en anillo
rf-star              # Swarm en estrella
rf-spawn coder       # Crear agente coder
rf-daemon            # Iniciar workers en segundo plano
rf-status            # Estado de Ruflo
```
</details>

<details>
<summary><b>💾 Memoria</b></summary>

```bash
bd-ready             # Estado del proyecto (inicio de sesión)
bd-add               # Registrar issue/decisión/bloqueo
bd-list              # Listar beads
ruv-remember K V     # Almacenar en AgentDB
ruv-recall Q         # Buscar en AgentDB
mem-search Q         # Buscar en memoria de Ruflo
mem-stats            # Estadísticas de memoria
```
</details>

<details>
<summary><b>🌳 Aislamiento</b></summary>

```bash
wt-add agent-1       # Crear worktree para agente
wt-remove agent-1    # Limpiar worktree
wt-list              # Mostrar worktrees activos
wt-clean             # Eliminar worktrees obsoletos
```
</details>

<details>
<summary><b>🧪 Calidad y Testing</b></summary>

```bash
aqe-generate         # Generar tests (plugin Agentic QE)
aqe-gate             # Puerta de calidad
os-init              # Inicializar OpenSpec
os                   # Ejecutar OpenSpec
```
</details>

<details>
<summary><b>🧠 Inteligencia</b></summary>

```bash
hooks-train          # Pretrain profundo en codebase
hooks-route          # Enrutar tarea al agente óptimo
neural-train         # Entrenar patrones neurales
neural-patterns      # Ver patrones aprendidos
gnx-analyze          # Indexar repo en grafo de conocimiento
gnx-serve            # Iniciar servidor web local
gnx-wiki             # Generar wiki desde grafo
```
</details>

---

## 🔄 Migración desde v3.x

1. Los aliases `cf-*` ya no existen → usa `rf-*`
2. Los slash commands (`/sparc`, etc.) ya no existen → Ruflo auto-activa skills
3. Ejecuta `bd init` en tus repos para habilitar memoria Beads
4. Ejecuta `npx gitnexus analyze` en tus repos para construir el grafo
5. El directorio `v3/` preserva todo — nada fue eliminado

| v3.4.1 | v4.0.0 |
|:-------|:-------|
| `cf-init` | `rf-init` |
| `cf-swarm` | `rf-swarm` |
| `cf-doctor` | `rf-doctor` |
| `cf-mcp` | Automático vía `rf-wizard` |
| `mem-search` | `mem-search` (sin cambio) |
| `cfb-open` | Via herramientas MCP del navegador de Ruflo |
| Sin memoria entre sesiones | `bd-ready`, `bd-add` |
| Sin aislamiento | `wt-add`, `wt-remove` |
| Sin grafo de código | `gnx-analyze` |

---

## 📂 Estructura del Repositorio

```
turbo-flow/
├── v3/                          ← archivado (era Claude Flow)
├── v4/                          ← desarrollo activo (era Ruflo)
│   ├── .devcontainer/
│   │   ├── devcontainer.json
│   │   ├── setup-turboflow-4.sh
│   │   └── post-setup-turboflow-4.sh
│   ├── scripts/
│   │   └── generate-claude-md.sh
│   ├── CLAUDE.md
│   └── README.md
├── docs/
│   └── migration-v3-to-v4.md
├── CLAUDE.md                    ← raíz, apunta a v4/
└── README.md
```

---

## 📊 Historial de Versiones

| Versión | Fecha | Cambios |
|:--------|:------|:--------|
| **v4.0.0** | Mar 2026 | **Migración a Ruflo**: Ruflo v3.5, Beads, GitNexus, Worktrees, Agent Teams, 6 plugins, UI UX Pro Max, OpenSpec |
| v3.4.1 | Feb 2025 | Fixes: skill install removido, plugins command, npm fallback |
| v3.4.0 | Feb 2025 | Completo + Plugins: 36 skills, 15 plugins |
| v3.3.0 | Feb 2025 | Instalación completa: 41 skills, memoria, MCP |
| v3.0.0 | Feb 2025 | Versión inicial con Claude Flow V3 |

---

## 🔗 Recursos

| Recurso | Enlace |
|:--------|:-------|
| 🎯 Ruflo | [GitHub: ruvnet/ruflo](https://github.com/ruvnet/ruflo) |
| 🚀 Turbo Flow | [GitHub: marcuspat/turbo-flow](https://github.com/marcuspat/turbo-flow) |
| 📋 OpenSpec | [npm: @fission-ai/openspec](https://npmjs.com/package/@fission-ai/openspec) |
| 🧪 Agentic QE | [npm: agentic-qe](https://npmjs.com/package/agentic-qe) |

---

<div align="center">

**Construido con 💜 para el ecosistema de Claude**

*Ruflo v3.5. 215+ herramientas MCP. 6 plugins. Beads. GitNexus. Worktrees. Un solo comando.*

</div>
