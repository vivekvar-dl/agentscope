# Security Policy

## 🔒 Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in AgentScope, please report it responsibly.

### How to Report

**DO NOT** open a public GitHub issue for security vulnerabilities.

Instead, please email: **security@[youremail].com** (or use GitHub Security Advisories)

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)

We'll respond within 48 hours and work with you to resolve the issue.

## 🛡️ Security Practices

### Data Privacy

- **Local by default:** All data stays on your machine
- **No telemetry:** We don't collect usage data without your consent
- **API keys:** Never logged or transmitted
- **Export files:** You control where data goes

### Dependencies

We regularly update dependencies and scan for vulnerabilities using:
- Dependabot
- GitHub Security Advisories
- Manual audits

### Code Review

All PRs are reviewed before merging. Security-sensitive changes require:
- Multiple reviews
- Test coverage
- Security checklist approval

## 🔍 What We Track

AgentScope only tracks what you explicitly provide:
- Agent execution metrics (local)
- Token counts (calculated locally)
- Cost estimates (calculated locally)
- Tool calls (observed locally)

**We never:**
- Send data to external servers (unless you enable cloud sync)
- Log API keys or credentials
- Track usage without consent
- Phone home

## ✅ Safe Usage

### Best Practices

1. **Sandbox agents:** Run untrusted agents in isolated environments
2. **Limit permissions:** Don't give agents unnecessary file/system access
3. **Review exports:** Check JSON exports before sharing publicly
4. **Update regularly:** Keep AgentScope and dependencies current
5. **Secure API keys:** Use environment variables, not hardcoded keys

### Known Limitations

- AgentScope wraps your agent but doesn't control it
- Agent tools determine what the agent can do
- Enforce boundaries at the tool level, not in AgentScope

## 📦 Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## 🔄 Security Updates

We announce security updates via:
- GitHub Security Advisories
- Release notes
- Discord #announcements channel

Subscribe to releases to stay informed.

## 🙏 Acknowledgments

We appreciate responsible disclosure. Security researchers who report vulnerabilities will be:
- Credited in release notes (if desired)
- Added to SECURITY_HALL_OF_FAME.md
- Thanked publicly (with permission)

---

**Last updated:** March 2026
