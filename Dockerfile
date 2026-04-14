# =============================================================================
# TurboFlow 4.0 — Pre-baked Development Container
#
# Mirrors the 10-step setup from devpods/Taskfile.yml but pre-bakes everything
# into the image so container startup is ~2 min instead of ~10 min.
#
# Base: Ubuntu 24.04 (matches .devcontainer/devcontainer.json)
# Size: ~1–1.2 GB
#
# Usage:
#   docker build -t turbo-flow:4.0 .
#   docker run -it -e ANTHROPIC_API_KEY=sk-... turbo-flow:4.0
#
# Or with docker-compose:
#   docker compose up -d
#   docker compose exec turboflow bash
# =============================================================================

FROM ubuntu:24.04

LABEL maintainer="Adventure Wave Labs"
LABEL version="4.0.0"
LABEL description="TurboFlow 4.0 — Ruflo v3.5 + Beads + Worktrees + Agent Teams"

ARG NODE_MAJOR=20
ARG USERNAME=vscode

# Create non-root user (replaces what the devcontainer base image provided)
RUN groupadd --gid 1000 ${USERNAME} 2>/dev/null || true \
    && useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home ${USERNAME} 2>/dev/null \
       || usermod -l ${USERNAME} -d /home/${USERNAME} -m $(getent passwd 1000 | cut -d: -f1) 2>/dev/null || true \
    && apt-get update && apt-get install -y sudo \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} \
    && rm -rf /var/lib/apt/lists/*

# ─── Environment ─────────────────────────────────────────────────────────────
ENV NPM_CONFIG_PREFIX=/home/${USERNAME}/.npm-global \
    PIP_BREAK_SYSTEM_PACKAGES=1 \
    CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 \
    WORKSPACE=/workspace \
    WORKSPACE_FOLDER=/workspace \
    DEVPOD_WORKSPACE_FOLDER=/workspace \
    AGENTS_DIR=/workspace/agents \
    PATH="/home/${USERNAME}/.npm-global/bin:/home/${USERNAME}/.local/bin:/home/${USERNAME}/.claude/bin:${PATH}"

# Bedrock env vars — set at runtime, not build time.
# To use Bedrock, pass these when running the container:
#   docker run -e CLAUDE_CODE_USE_BEDROCK=1 -e AWS_REGION=us-east-1 ...
# Or use an ECS task role / EC2 instance profile for credentials.

# =============================================================================
# STEP 1: System Prerequisites
# =============================================================================
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        python3 \
        python3-pip \
        git \
        curl \
        jq \
        tmux \
        htop \
        ca-certificates \
        gnupg \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# STEP 2a: Node.js 20
# =============================================================================
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# STEP 6a: Dolt (version-controlled SQL — required by Beads)
# Installed as root before switching user since it goes to /usr/local/bin
# =============================================================================
RUN curl -fsSL https://github.com/dolthub/dolt/releases/latest/download/install.sh | bash \
    || { \
        OS="$(uname -s | tr '[:upper:]' '[:lower:]')" \
        && ARCH="$(uname -m)" \
        && case "$ARCH" in x86_64) ARCH="amd64";; aarch64|arm64) ARCH="arm64";; esac \
        && curl -fsSL "https://github.com/dolthub/dolt/releases/latest/download/dolt-${OS}-${ARCH}.tar.gz" \
           | tar -xz -C /usr/local/bin --strip-components=2; \
    }

# =============================================================================
# Switch to non-root user (matches devcontainer convention)
# =============================================================================
USER ${USERNAME}
WORKDIR /home/${USERNAME}

# npm global directory
RUN mkdir -p /home/${USERNAME}/.npm-global/bin \
             /home/${USERNAME}/.npm-global/lib \
             /home/${USERNAME}/.local/bin

# =============================================================================
# STEP 2b: Claude Code
# =============================================================================
RUN curl -fsSL https://claude.ai/install.sh 2>/dev/null | bash || true
# Fallback to npm if native installer didn't work
RUN command -v claude >/dev/null 2>&1 \
    || npm install -g @anthropic-ai/claude-code 2>/dev/null || true

# =============================================================================
# STEP 2c: Ruflo v3.5
# Bundles: AgentDB v3, RuVector WASM, SONA, 215 MCP tools, 60+ agents,
# skills system, browser automation, observability, gating
# =============================================================================
RUN npx ruflo@latest init --force 2>/dev/null || true

# =============================================================================
# STEP 3: Ruflo Plugins (6) + OpenSpec
# Cap Node heap to 512MB to prevent OOM in constrained builds
# =============================================================================
RUN export NODE_OPTIONS="--max-old-space-size=512" \
    && npx ruflo@latest plugins install -n "@claude-flow/plugin-agentic-qe" 2>/dev/null || true
RUN export NODE_OPTIONS="--max-old-space-size=512" \
    && npx ruflo@latest plugins install -n "@claude-flow/plugin-code-intelligence" 2>/dev/null || true
RUN export NODE_OPTIONS="--max-old-space-size=512" \
    && npx ruflo@latest plugins install -n "@claude-flow/plugin-test-intelligence" 2>/dev/null || true
RUN export NODE_OPTIONS="--max-old-space-size=512" \
    && npx ruflo@latest plugins install -n "@claude-flow/plugin-perf-optimizer" 2>/dev/null || true
RUN export NODE_OPTIONS="--max-old-space-size=512" \
    && npx ruflo@latest plugins install -n "@claude-flow/teammate-plugin" 2>/dev/null || true
RUN export NODE_OPTIONS="--max-old-space-size=512" \
    && npx ruflo@latest plugins install -n "@claude-flow/plugin-gastown-bridge" 2>/dev/null || true
RUN npm install -g @fission-ai/openspec 2>/dev/null || true

# Clean npm cache between heavy phases
RUN npm cache clean --force 2>/dev/null || true

# =============================================================================
# STEP 4: UI UX Pro Max Skill
# =============================================================================
RUN npx -y uipro-cli init --ai claude --offline 2>/dev/null || true

# =============================================================================
# STEP 5: GitNexus (Codebase Knowledge Graph)
# =============================================================================
RUN export NODE_OPTIONS="--max-old-space-size=512" \
    && npm install -g gitnexus 2>/dev/null || true
RUN npm cache clean --force 2>/dev/null || true

# =============================================================================
# STEP 6b: Beads (cross-session memory — requires Dolt)
# =============================================================================
RUN export NODE_OPTIONS="--max-old-space-size=512" \
    && npm install -g @beads/bd 2>/dev/null || true

# Configure Dolt git identity
RUN dolt config --global --add user.name "TurboFlow Agent" 2>/dev/null || true \
    && dolt config --global --add user.email "agent@turboflow.local" 2>/dev/null || true

# =============================================================================
# STEP 8: Statusline Pro + STEP 10: Aliases
# These are generated at runtime by the entrypoint since they reference
# dynamic paths. We copy the devpods scripts which handle this.
# =============================================================================

# Copy devpods (includes Taskfile.yml, bootstrap.sh, devbox.json, scripts, context)
COPY --chown=${USERNAME}:${USERNAME} devpods /workspace/devpods

# Copy CLAUDE.md if present (use a separate build stage to avoid failure)
COPY --chown=${USERNAME}:${USERNAME} CLAUDE.md /workspace/CLAUDE.md

# =============================================================================
# STEP 7: Workspace directories
# =============================================================================
RUN mkdir -p /workspace/src \
             /workspace/tests \
             /workspace/docs \
             /workspace/scripts \
             /workspace/config \
             /workspace/plans \
             /workspace/agents

# =============================================================================
# Entrypoint — runs lightweight post-setup on first start
# =============================================================================
COPY --chown=${USERNAME}:${USERNAME} docker-entrypoint.sh /home/${USERNAME}/docker-entrypoint.sh
RUN chmod +x /home/${USERNAME}/docker-entrypoint.sh

WORKDIR /workspace

EXPOSE 3000 8080

ENTRYPOINT ["/home/vscode/docker-entrypoint.sh"]
CMD ["bash"]
