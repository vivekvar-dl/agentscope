# 🔍 AgentScope

<div align="center">

<img src="https://via.placeholder.com/200x200/0066cc/ffffff?text=🔍" alt="AgentScope Logo" width="120"/>

### The Missing Debugger for AI Agents

**Track costs • Monitor execution • Debug in real-time**

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/vivekvar-dl/agentscope?style=social)](https://github.com/vivekvar-dl/agentscope/stargazers)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Discord](https://img.shields.io/badge/discord-join%20chat-7289da.svg)](https://discord.gg/agentscope)

[🌐 Website](https://vivekvar-dl.github.io/agentscope/) • [📖 Docs](https://vivekvar-dl.github.io/agentscope/) • [💬 Discord](https://discord.gg/agentscope) • [🐛 Issues](https://github.com/vivekvar-dl/agentscope/issues)

</div>

---

## 🎯 Why AgentScope?

AI agents are **black boxes**. You deploy them and hope for the best:

```
Agent: *thinking...*
       *calling some tools...*
       *burning your API credits...*
       
You: 🤷 What just happened?
```

**AgentScope gives you X-ray vision:**

```python
from agentscope import AgentScope

with AgentScope(agent, verbose=True) as scope:
    result = agent.run("Analyze this data")
    
# Instant insights
print(f"💰 Cost: ${scope.cost:.4f}")
print(f"🔢 Tokens: {scope.tokens}")
print(f"🔧 Tools: {scope.tool_calls}")
print(f"⏱️  Time: {scope.duration_seconds:.2f}s")
```

<div align="center">

**One line to integrate. Full visibility forever.**

[Get Started →](#-quick-start) • [See Examples →](#-examples)

</div>

---

## ⚡ Quick Start

### Install

```bash
pip install git+https://github.com/vivekvar-dl/agentscope.git
```

### Use

```python
from agentscope import AgentScope
from langchain.agents import create_openai_functions_agent

# Your normal agent
agent = create_openai_functions_agent(...)

# Wrap it (that's it!)
with AgentScope(agent) as scope:
    result = agent.invoke({"input": "What's the weather?"})
```

### Output

```
╭─────────────────────────────────────────╮
│  AgentScope Execution Summary           │
├─────────────────────────────────────────┤
│  Status:        ✓ Success               │
│  Duration:      2.3s                    │
│  Cost:          $0.0042                 │
│  Tokens:        847 (prompt) + 124 (completion) │
│  Tools:         2 calls                 │
│    - DuckDuckGoSearchRun: 2x            │
│  Decisions:     3                       │
╰─────────────────────────────────────────╯
```

[Full documentation →](https://vivekvar-dl.github.io/agentscope/)

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎯 One-Line Integration
```python
with AgentScope(agent) as scope:
    result = agent.run(task)
```
Zero configuration. Works immediately.

### 💰 Cost Tracking
Track every dollar spent. Supports GPT-4, Claude, Gemini, and 15+ models with accurate pricing.

### 🔧 Tool Monitoring
See which tools your agent calls, how often, and their success rates.

</td>
<td width="50%">

### ⏱️ Performance Metrics
Execution time, token usage, and decision counts for every run.

### 🎬 Replay & Export
Export traces to JSON. Replay any execution. Compare runs side-by-side.

### 🎨 Beautiful CLI
Color-coded output with Rich library. Pretty tables. Live updates.

</td>
</tr>
</table>

---

## 🚀 Why Developers Love It

<div align="center">
<table>
<tr>
<td align="center" width="33%">
<h3>🪶 Lightweight</h3>
<code>&lt;1%</code> overhead<br/>
Minimal dependencies<br/>
Works offline
</td>
<td align="center" width="33%">
<h3>🔓 Open Source</h3>
Free forever<br/>
MIT licensed<br/>
No account needed
</td>
<td align="center" width="33%">
<h3>🔌 Framework Agnostic</h3>
LangChain ✅<br/>
CrewAI (soon)<br/>
AutoGen (soon)
</td>
</tr>
</table>
</div>

---

## 📖 Examples

### Basic Usage

```python
from agentscope import AgentScope

with AgentScope(agent, project="my-app", verbose=True) as scope:
    result = agent.run("Your task here")
    
scope.print_summary()
scope.export("trace.json")
```

### Cost Optimization

```python
# Before: Expensive GPT-4
with AgentScope(gpt4_agent) as scope:
    result = agent.run(task)
    print(f"GPT-4: ${scope.cost:.4f}")  # $0.42

# After: Try GPT-3.5 for same task
with AgentScope(gpt35_agent) as scope:
    result = agent.run(task)
    print(f"GPT-3.5: ${scope.cost:.4f}")  # $0.03

# 14x cost reduction! 💰
```

### Compare Agents

```python
agents = [agent_v1, agent_v2, agent_v3]
scopes = []

for agent in agents:
    with AgentScope(agent, name=f"v{i+1}") as scope:
        result = agent.run(prompt)
        scopes.append(scope)

# Side-by-side comparison
AgentScope.compare(scopes)
```

[More examples →](examples/)

---

## 📊 vs Alternatives

<table>
<tr>
<th></th>
<th>AgentScope</th>
<th>LangSmith</th>
<th>DIY Logging</th>
</tr>
<tr>
<td><strong>Open Source</strong></td>
<td>✅ Yes</td>
<td>❌ No</td>
<td>✅ Yes</td>
</tr>
<tr>
<td><strong>Free</strong></td>
<td>✅ Yes</td>
<td>❌ Paid</td>
<td>✅ Yes</td>
</tr>
<tr>
<td><strong>Works Offline</strong></td>
<td>✅ Yes</td>
<td>❌ No</td>
<td>✅ Yes</td>
</tr>
<tr>
<td><strong>Cost Tracking</strong></td>
<td>✅ Built-in</td>
<td>✅ Yes</td>
<td>❌ Manual</td>
</tr>
<tr>
<td><strong>Beautiful Output</strong></td>
<td>✅ Yes</td>
<td>✅ Yes</td>
<td>❌ No</td>
</tr>
<tr>
<td><strong>Setup Time</strong></td>
<td>✅ 1 minute</td>
<td>⚠️ 10 minutes</td>
<td>❌ Hours</td>
</tr>
</table>

---

## 🗺️ Roadmap

<table>
<tr>
<td width="33%">

### ✅ v0.1.0 (Current)
- [x] LangChain support
- [x] Cost tracking
- [x] CLI output
- [x] Export traces
- [x] 15+ model pricing

</td>
<td width="33%">

### 🔄 v0.2.0 (Next)
- [ ] Web dashboard
- [ ] Cost optimization AI
- [ ] CrewAI support
- [ ] Comparison tool
- [ ] Better docs

</td>
<td width="33%">

### 📋 v0.3.0 (Future)
- [ ] AutoGen support
- [ ] Cloud sync (optional)
- [ ] Team features
- [ ] A/B testing
- [ ] Benchmark suite

</td>
</tr>
</table>

[View full roadmap →](https://github.com/vivekvar-dl/agentscope/issues)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         Your Application                    │
└──────────────────┬──────────────────────────┘
                   │
         ┌─────────▼──────────┐
         │    AgentScope      │ (Transparent wrapper)
         │                    │
         └─────────┬──────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼────┐  ┌──────▼──────┐  ┌───▼────┐
│ Tracer │  │   Metrics   │  │Storage │
│        │  │  Collector  │  │        │
└────────┘  └─────────────┘  └────────┘
```

**Design principles:**
- 🪶 <1% performance overhead
- 🔌 Non-invasive (zero code changes)
- 🔒 Secure (data stays local)
- 🧩 Extensible (plugin system)

---

## 🤝 Contributing

We love contributions! See [CONTRIBUTING.md](CONTRIBUTING.md)

**Ways to contribute:**
- 🐛 [Report bugs](https://github.com/vivekvar-dl/agentscope/issues/new?template=bug_report.md)
- ✨ [Request features](https://github.com/vivekvar-dl/agentscope/issues/new?template=feature_request.md)
- 📖 [Improve docs](https://github.com/vivekvar-dl/agentscope/blob/main/CONTRIBUTING.md#documentation)
- 🔧 [Add adapters](https://github.com/vivekvar-dl/agentscope/blob/main/CONTRIBUTING.md#adding-adapters)
- ⭐ [Star the repo](https://github.com/vivekvar-dl/agentscope/stargazers)

**Good first issues:** [labeled here](https://github.com/vivekvar-dl/agentscope/labels/good%20first%20issue)

---

## 💬 Community

<div align="center">

[![Discord](https://img.shields.io/badge/Discord-Join%20Chat-7289da?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/agentscope)
[![Twitter](https://img.shields.io/badge/Twitter-Follow-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/agentscope)
[![GitHub](https://img.shields.io/badge/GitHub-Discussions-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/vivekvar-dl/agentscope/discussions)

**Join 100+ developers building better AI agents**

</div>

- **Discord:** Real-time chat, support, and community
- **Discussions:** Q&A, feature requests, show & tell
- **Twitter:** Updates, tips, and agent debugging stories

---

## 📊 Stats

<div align="center">

![GitHub Stats](https://img.shields.io/github/stars/vivekvar-dl/agentscope?style=social)
![GitHub Forks](https://img.shields.io/github/forks/vivekvar-dl/agentscope?style=social)
![GitHub Watchers](https://img.shields.io/github/watchers/vivekvar-dl/agentscope?style=social)

![Contributors](https://img.shields.io/github/contributors/vivekvar-dl/agentscope)
![Last Commit](https://img.shields.io/github/last-commit/vivekvar-dl/agentscope)
![Issues](https://img.shields.io/github/issues/vivekvar-dl/agentscope)
![Pull Requests](https://img.shields.io/github/issues-pr/vivekvar-dl/agentscope)

</div>

---

## 🙏 Acknowledgments

Built with:
- [LangChain](https://github.com/langchain-ai/langchain) - Agent framework
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output
- [FastAPI](https://github.com/tiangolo/fastapi) - Dashboard backend (coming soon)

Inspired by:
- [Weights & Biases](https://wandb.ai/) - ML experiment tracking
- [OpenTelemetry](https://opentelemetry.io/) - Observability standard
- The amazing agent developer community 💙

---

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

Copyright © 2026 [Vivek](https://github.com/vivekvar-dl)

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=vivekvar-dl/agentscope&type=Date)](https://star-history.com/#vivekvar-dl/agentscope&Date)

---

<div align="center">

### Built with ❤️ by developers who debug agents daily

**If AgentScope saved you hours of debugging, give us a ⭐!**

[⭐ Star on GitHub](https://github.com/vivekvar-dl/agentscope) • [🌐 Visit Website](https://vivekvar-dl.github.io/agentscope/) • [💬 Join Discord](https://discord.gg/agentscope)

</div>
