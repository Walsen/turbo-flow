# Turbo Flow Quick Setup

This guide explains how to run the bootstrap script for the `turbo-flow` environment.

The bootstrap script will automatically:

1.  Install all required system dependencies (Node.js, Python, Tmux, etc.).
2.  Run the idempotent Taskfile.yml setup tasks.
3.  Configure the environment and launch the tmux workspace.

-----

## ⚙️ Installation

### 1\. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/adventurewavelabs/turbo-flow.git
```

### 2\. Run the Bootstrap Script

Run the bootstrap script from the repo root:

```bash
cd turbo-flow
bash devpods/bootstrap.sh
```

-----

## ✅ After the Script Runs

The installer script finishes by launching you directly into a **TMux session** named `workspace`. Tmux is a terminal multiplexer that allows you to run and manage multiple terminal windows within a single session.

Your `tmux` session is pre-configured with the following windows:

  * **Window 0: `Claude-1`** (Main work window)
  * **Window 1: `Claude-2`** (A second work window)
  * **Window 2: `Claude-Monitor`** (Runs `claude-monitor`)
  * **Window 3: `htop`** (System monitor)

### Basic Tmux Commands

  * **Switch Windows:** Press **`Ctrl+b`**, release, then press the window number (e.g., `0`, `1`, `2`).
  * **Next Window:** Press **`Ctrl+b`**, release, then press `n` (for next).
  * **Detach (Leave Session Running):** Press **`Ctrl+b`**, release, then press `d` (for detach).
  * **Re-attach:** From your normal terminal, type `tmux a -t workspace` to get back into your session.

All your new aliases (like `dsp`, `cf-swarm`, `cfs`, etc.) are now active and ready to use *inside* this `tmux` session.
