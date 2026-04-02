---
name: email-spam-fixer
description: Scan email copy for spam words and fix detected words using Cyrillic lookalike characters. Use when checking emails for spam triggers, cleaning email copy for cold email deliverability, or spam-checking spintaxed copy in Bison or Instantly format.
---

# Email Spam Fixer

Scan email copy for spam words using Mailmeteor's live spam checker, then fix detected spam words using Cyrillic lookalike characters.

## Triggers
- fix spam in email
- check email for spam
- spam check
- clean email copy
- bypass spam filter

## Prerequisites
- Python 3.x
- Playwright: `pip install playwright && playwright install chromium`

## Workflow

### Step 1: Get Email Copy
Ask the user to provide their email copy if not already provided.

### Step 2: Detect Spintax Format

Check if input uses spintax. Two formats must be recognized:

**Instantly format:** `{{RANDOM | option1 | option2 | option3}}`
**Bison format:** `{option1 | option2 | option3}` — single brace, pipe-separated

**How to tell Bison spintax from Bison variables:**
- `{FIRST_NAME}` — ALL CAPS, no pipe = variable → skip, do not process as spintax
- `{option one | option two}` — contains `|` = spintax block → process all options

**If Instantly format detected:**
- Parse all variations
- Run spam check on first variation (representative sample)
- Apply fixes to ALL variations
- Reconstruct in original `{{RANDOM | ...}}` format

**If Bison format detected:**
- Identify all `{...}` blocks containing at least one `|`
- Skip blocks matching variable pattern (ALL_CAPS and underscores only, no pipe)
- For each spintax block: split on `|` → extract all options
- Check ALL options from ALL blocks for spam words
- Apply fixes to ALL options in ALL blocks
- Reconstruct in same Bison format: `{fixed_opt1 | fixed_opt2 | fixed_opt3 | fixed_opt4}`

**If no spintax detected:**
- Process as plain text

### Step 3: Check for Spam Words (Primary — Mailmeteor)
Run the Mailmeteor spam checker via Playwright:
```bash
python ~/.claude/skills/email-spam-fixer/scripts/check_spam.py --text "email text"
```

For longer emails, write the text to a temp file and use:
```bash
python ~/.claude/skills/email-spam-fixer/scripts/check_spam.py --file temp_email.txt
```

The script returns JSON with:
- `score`: `"poor"`, `"okay"`, or `"great"`
- `spam_words`: list of flagged words with categories

**Decision logic:**
- If `score` is `"great"` → email is clean. Report score to user and stop.
- If `score` is `"poor"` or `"okay"` → proceed to Step 4.

**If Mailmeteor is unreachable (script errors or times out) — Fallback:**
Scan the email copy against the local word list at `references/spam-words.md` (case-insensitive match). Report to the user that fallback mode is being used and that results may be less complete.

### Step 4: Fix Spam Words
Run the fixer script with the spam words returned by the checker:
```bash
python ~/.claude/skills/email-spam-fixer/scripts/fix_spam.py --text "email text" --words "word1,word2,word3"
```

For longer emails, write the text to a temp file and use:
```bash
python ~/.claude/skills/email-spam-fixer/scripts/fix_spam.py --file temp_email.txt --words "word1,word2,word3"
```

**When called from a campaign pipeline, add `--summary` / `-s`:**
```bash
python ~/.claude/skills/email-spam-fixer/scripts/fix_spam.py --file temp_email.txt --words "word1,word2,word3" --summary
```
Summary output: `{"fixed_text": "...", "words_fixed": N, "unique_words": ["word1", ...]}` — much smaller than the full changes array. Use full output (no flag) only for manual review sessions.

The script will:
- Replace ONE character per spam word with a Cyrillic lookalike
- Automatically replace `$` and `%` symbols (common spam triggers)
- Return JSON with the cleaned text and a change log (or summary if `--summary` is set)

### Step 5: Output
Provide the user with:
- The Mailmeteor score (or note that fallback mode was used)
- The cleaned email copy (in SAME FORMAT as input — preserve spintax if present)
- Summary of spam words detected and which characters were swapped

## Spintax Format Handling

**Input format:**
```
{{RANDOM | We just helped the latest client get 241k new users | We just helped our newest client bring in 241k new users | We just helped a recent client gain 241k new users}}
```

**Output format (MUST match input):**
```
{{RANDOM | We just helped the latest client gеt 241k nеw users | We just helped our newest client bring in 241k nеw users | We just helped a recent client gain 241k nеw users}}
```

Key rules:
1. If input has `{{RANDOM |`, output MUST have `{{RANDOM |`
2. Preserve the exact number of variations
3. Use ` | ` (space-pipe-space) as separator
4. Apply same spam word fixes to ALL variations

## How It Works

The fixer replaces specific characters in spam words with visually identical Cyrillic characters:
- `a` → `а` (Cyrillic а, U+0430)
- `e` → `е` (Cyrillic е, U+0435)
- `o` → `о` (Cyrillic о, U+043E)
- `c` → `с` (Cyrillic с, U+0441)
- `A` → `А`, `E` → `Е`, `O` → `О`, `H` → `Н`, `M` → `М`, `K` → `К`...
- And more...

These characters look the same to humans but aren't detected by spam filters that scan for exact word matches. Only ONE character per word is replaced — that's enough to bypass filters.

## References
- See `references/spam-words.md` for the fallback spam word database (categorized)
- See `references/character-map.md` for the full character substitution table

## Notes
- Only detected spam words are modified, not the entire email
- The email remains readable to recipients
- Cyrillic characters render correctly in all major email clients
- Mailmeteor is the primary detection method — more accurate than the static word list
- The local word list is used as fallback only if Mailmeteor is unreachable
