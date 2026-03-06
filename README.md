# Claude Campaign Skills

Claude Code skills for running cold email campaigns end-to-end. Paste copy → live EmailBison campaign in one session.

## Skill Map

```
campaign-creator
├── spintax-creator   (generates spintax variations per sentence)
├── email-spam-fixer  (Mailmeteor check + Unicode fix, Python scripts)
└── emailbison        (EmailBison MCP rules & API reference)
```

## Prerequisites

- [Claude Code CLI](https://claude.ai/code)
- Python 3.x + Playwright:
  ```bash
  pip install playwright && playwright install chromium
  ```
- **EmailBison MCP** — install from [emailbison.com](https://emailbison.com) (teammates must add this themselves; API key is personal)

## Installation

```bash
git clone https://github.com/geeky-rambo/claude-campaign-skills.git

# Copy the four skill folders into your Claude skills directory
cp -r claude-campaign-skills/campaign-creator ~/.claude/skills/
cp -r claude-campaign-skills/emailbison ~/.claude/skills/
cp -r claude-campaign-skills/email-spam-fixer ~/.claude/skills/
cp -r claude-campaign-skills/spintax-creator ~/.claude/skills/

# Set up sender cache
cp ~/.claude/skills/emailbison/sender-cache.template.md ~/.claude/skills/emailbison/sender-cache.md
```

## Skills

| Skill | Invoke with | What it does |
|---|---|---|
| `campaign-creator` | `/campaign-creator` | Full pipeline: spam check → fix → spintax → push to EmailBison |
| `emailbison` | `/emailbison` | API rules & reference for EmailBison MCP calls |
| `email-spam-fixer` | `/email-spam-fixer` | Detect spam words (Mailmeteor) + fix with Unicode lookalikes |
| `spintax-creator` | `/spintax-creator` | Generate 3 spintax variations per sentence |

## Sensitive Files

`emailbison/sender-cache.md` is gitignored and will never be committed. After your first campaign run, Claude will populate it with your workspace's sender IDs automatically. Subsequent campaigns skip the API pagination entirely — saving ~18,000 tokens per run.

## File Structure

```
.
├── README.md
├── .gitignore
├── campaign-creator/
│   └── SKILL.md              # Main pipeline orchestrator
├── emailbison/
│   ├── SKILL.md              # EmailBison MCP rules & confirmed endpoints
│   ├── sender-cache.template.md  # Copy → sender-cache.md and populate
│   └── sender-cache.md       # Your local sender IDs (gitignored)
├── email-spam-fixer/
│   ├── SKILL.md              # Spam detection & fix workflow
│   ├── scripts/
│   │   ├── check_spam.py     # Mailmeteor checker via Playwright
│   │   ├── fix_spam.py       # Unicode lookalike replacer
│   │   └── spintax_handler.py
│   └── references/
│       ├── spam-words.md     # Fallback spam word database
│       └── character-map.md  # Unicode substitution table
└── spintax-creator/
    └── skill.md              # Spintax variation generator
```
