# 🚀 Turbo Flow Setup for GitHub Codespaces

## ⚡ Quick Setup Methods

### GitHub Codespace Dev Container **

After the codespace boots up, run this command to set up Turbo Flow:

```bash
bash devpods/bootstrap.sh
```
---

## 📁 What Gets Installed

```
your-project/
├── devpods/                    # Setup scripts
├── agents/                     # AI agent library
├── cf-with-context.sh         # Context wrapper
├── CLAUDE.md                  # Claude development rules
├── FEEDCLAUDE.md              # Streamlined instructions
└── [project files]            # Your configured environment
```

---

## 🎯 Available Commands

```bash
cf "any task"              # General AI coordination
cf-swarm "build feature"   # Focused implementation
cf-hive "complex planning" # Multi-agent coordination
claude-monitor             # Usage tracking
```

---

## 🖥️ Tmux Workspace

Connect after setup:
```bash
tmux attach -t workspace
```

**Windows:**
- **0**: Primary Claude workspace
- **1**: Secondary Claude workspace  
- **2**: Claude monitor
- **3**: System monitor (htop)

**Navigation:**
- `Ctrl+b 0-3` - Switch windows
- `Ctrl+b d` - Detach session
- `Ctrl+b ?` - Help

---

## 💡 Quick Test

```bash
# After setup and connecting to tmux:
source ~/.bashrc
cf "Hello! Show me available agents"
```

---

## ⚠️ Troubleshooting

**Can't connect to tmux:**
```bash
tmux list-sessions
# If missing, run:
./devpods/tmux-workspace.sh
tmux attach -t workspace
```

**Commands not found:**
```bash
source ~/.bashrc
```

---

## 🎉 You're Ready!

**Workflow:**
1. **Setup**: Run `bash devpods/bootstrap.sh`
2. **Connect**: `tmux attach -t workspace`  
3. **Build**: `cf-swarm "Help me build my app"`

✅ Complete AI development environment  
✅ Extensive agent library  
✅ Monitoring tools  
✅ 4-window tmux workspace  

**Remember:** Always work inside tmux for the best experience!
