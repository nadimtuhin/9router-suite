# 9router-suite

<p align="center">
  <img src="assets/banner.png" alt="9Router Suite Banner" width="100%" />
</p>

Autonomous daily patch management, free-tier LLM discovery, and cross-agent skills distribution for [9Router](https://github.com/decolua/9router).

---

## The Story

If you run multiple autonomous coding agents (Claude Code, Codex, Pi, OpenCode, Hermes) day in and day out, your LLM router is your most critical piece of infrastructure.

When 9Router works, it is brilliant: one endpoint routing across subscriptions, tiered accounts, and free pools with instant failover. But upstream moves at breakneck speed.

Every single week, critical edge cases break in production:
- **Token double-counting**: Upstream prompt-cache counters get folded twice, blowing through usage tracking.
- **Protocol signature rejections**: Claude introduces CAIS protobuf envelopes for thinking signatures, and foreign signatures from fallback combos leak into conversation turns.
- **Schema mismatches**: Anthropic Draft 2020-12 rejects tool input schemas where integers are serialized as strings (`"1"` instead of `1`).
- **Context window clipping**: Codex models get forced down to 258k ceilings and trigger premature compactions.
- **Rogue process termination**: The CLI daemon blindly kills any process named `next-server`, crashing your other web apps on port 3000.

Contributors write fixes for these issues within hours. But waiting for upstream releases means living with broken agent loops for days.

Manually cherry-picking 30+ pull requests or maintaining a divergent git branch is painful: merge conflicts, duplicate diffs when PRs land, and hours wasted compiling by hand.

`9router-suite` was built to solve this once and for all: an unattended system that discovers open bug fix PRs, tests them in an isolated Git sandbox, compiles the Next.js bundle, verifies health endpoints, and syncs capabilities across all your agent harnesses.

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
