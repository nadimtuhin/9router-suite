# 9router-suite

Autonomous daily patch management, free-tier LLM discovery, and cross-agent skills distribution for [9Router](https://github.com/decolua/9router).

---

## Why

9Router moves fast. Upstream contributors open dozens of PRs addressing critical edge cases on providers like Antigravity, Claude, Codex, and OpenCode:
- Token accounting bugs (double-counting cached prompt tokens)
- Claude CAIS protobuf thinking signatures getting rejected
- Tool schema validation mismatches (integers serialized as strings)
- Missing context window selection causing premature agent compactions
- Silent process kills affecting neighboring Next.js apps

Waiting for upstream releases means living with broken provider loops in daily coding sessions. Re-applying PRs by hand or maintaining a diverged Git branch causes constant rebase conflicts.

`9router-suite` automates the entire lifecycle:
1. **Automated Bug Fix Discovery**: Discovers open bug fix PRs on `decolua/9router`, ranking core coding agents first (Antigravity, Claude, Codex, OpenCode).
2. **Sandbox Evaluation**: Evaluates candidate patches against clean `origin/master` in an isolated Git worktree before touching your live setup.
3. **Clean Build & Rollback**: Compiles the patched Next.js CLI bundle, deploys locally, and auto-rolls back if build or smoke tests fail.
4. **Free Combo Sync**: Dynamically extracts available free tier models from OpenCode and Cline into aggregated failover combos (`opencode-free`, `cline-free`, `free`).
5. **Cross-Agent Skills Distribution**: Installs and symlinks 9Router capability skills across Claude Code, Codex CLI, OpenCode, Pi, and Hermes Agent.

---

## Architecture

```
                       ┌────────────────────────────┐
                       │   decolua/9router (repo)   │
                       └─────────────┬──────────────┘
                                     │
                                     ▼
                      [9router-patcher (sandbox)]
                        - Evaluates open bug PRs
                        - Auto-prunes merged diffs
                        - Compiles Next.js bundle
                        - Executes smoke tests
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
[9router-sync-free]         [9router Daemon]           [9router-sync-skills]
- OpenCode free models      - :20128 Gateway           - Claude (~/.claude)
- Cline free models         - Patched runtime          - Codex (~/.codex)
- Failover combos           - Health & telemetry       - OpenCode (~/.opencode)
                                                       - Pi (~/.pi)
                                                       - Hermes (~/.hermes)
```

---

## Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 20+ (with npm)
- `gh` CLI (authenticated with GitHub)
- Git

### Quick Install

```bash
git clone https://github.com/nadimtuhin/9router-suite.git
cd 9router-suite
export PATH="$PWD/bin:$PATH"
```

To install binaries into your local path:
```bash
ln -sf "$PWD/bin/9router-suite" ~/.local/bin/9router-suite
ln -sf "$PWD/bin/9router-patcher" ~/.local/bin/9router-patcher
ln -sf "$PWD/bin/9router-sync-free" ~/.local/bin/9router-sync-free
ln -sf "$PWD/bin/9router-sync-skills" ~/.local/bin/9router-sync-skills
```

---

## CLI Tools

### 1. `9router-suite`
Master runner that coordinates the full pipeline:
```bash
9router-suite
```

### 2. `9router-patcher`
Discovers and applies open upstream bug fixes directly:
```bash
# Full discovery, sandbox build, install and smoke test
9router-patcher --repo-dir ~/opensource/9router

# Only discover and stage patches without building
9router-patcher --no-build
```

### 3. `9router-sync-free`
Discovers and configures free LLM tiers into 9Router combos:
```bash
9router-sync-free --db ~/.9router/db/data.sqlite
```

### 4. `9router-sync-skills`
Propagates 9Router capability skills across agent environments:
```bash
9router-sync-skills
```

---

## Automated Scheduling

Run daily via cron:

```cron
30 3 * * * /Users/username/.local/bin/9router-suite >> ~/.local/logs/9router-suite.log 2>&1
```

Or configure via launchd (`~/Library/LaunchAgents/com.9router.suite.plist`).

---

## Contributing

Pull requests and issues welcome! If you find a new upstream edge case or provider quirk, feel free to contribute an audit rule or sync adapter.

1. Fork the repository
2. Create your feature branch (`git checkout -b feat/new-adapter`)
3. Commit your changes (`git commit -m 'feat: add adapter'`)
4. Push to the branch (`git push origin feat/new-adapter`)
5. Open a Pull Request

---

## License

MIT License. See [LICENSE](LICENSE) for details.
