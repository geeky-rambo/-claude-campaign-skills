---
name: campaign-creator
description: Prepare campaign copy for EmailBison — spam check, spam fix, spintax, variable mapping, and campaign creation. Works both as pipeline step 5 (reads 04-copywriting.md) or standalone (paste any copy). Use after copywriting is complete or whenever you need to push copy to EmailBison.
---

# Campaign Creator — Push-Button Pipeline

One skill, zero copy-paste. Paste copy → live EmailBison campaign.

> **Before proceeding:** Invoke the `emailbison` skill now to load all MCP rules (sequence constraints, variable handling, pagination, campaign defaults, error handling). Do not skip this — the rules in that skill govern every EmailBison API call made in this workflow.

---

## Mode Detection

### Standalone Mode (PRIMARY)

If user provides a file path or pastes copy directly:
1. If a file path is given, read it with the Read tool (plain `.txt` file)
2. Parse by looking for: "Email 1", "Email 2", "Subject:", "Body:", numbered headers, "---" separators
3. If structure is ambiguous, show what was parsed and ask user to confirm before proceeding
4. Ask: "Which client is this for?" — needed for EmailBison workspace selection

### Pipeline Mode (SECONDARY)

If `04-copywriting.md` exists in current directory:
1. Read `04-copywriting.md` for email sequences
2. Read `03-campaign-strategy.md` for campaign tiers, variables, and routing logic
3. Read `../../00-client-overview-research.md` for client context
4. If `06-performance.md` exists (V2 iteration), read it for what to improve

**Both modes continue to Step 1 below.**

---

## The 10-Step Pipeline

### Step 1 — Parse Emails

Extract from the copy source:
- Campaign name / tier
- Email position in sequence (Email 1, 2, 3, 4)
- Thread structure (see table below)
- Subject line (Emails 1 & 3 only — new threads)
- Body text
- All variables used (`{{first_name}}`, `{{company_name}}`, custom vars, etc.)

**Thread structure:**

| Email | thread_reply | wait_in_days | Subject |
|-------|-------------|-------------|---------|
| 1 | false | 1 | Required (e.g. `your dashboard`) |
| 2 | true | 2–3 | `"[Email 1 subject]"` — bare subject, NO "Re:" prefix (API adds it automatically) |
| 3 | false | 3–4 | Required (e.g. `triαl for {COMPANY}`) |
| 4 | true | 2–3 | `"[Email 3 subject]"` — bare subject, NO "Re:" prefix (API adds it automatically) |

**Labeled email variants (e.g., Email 1a / Email 1b / Email 1c):**
STOP immediately. Before proceeding:
1. List every labeled variant found with its label and first line
2. Ask the user: "I found [N] variants: [list]. Which variant goes in which sequence step?"
3. Wait for the user's answer. Do NOT guess, default, or merge variants.

**If all variants are for Step 1** (e.g. Email 1a, 1b, 1c all open the sequence), offer two choices:
- **A/B/C test (recommended):** All variants go in as Step 1 + A/B/C variants. EmailBison rotates them automatically. Set `variant: true, variant_from_step: 1` on every variant after 1a. Step 2 onward follows all branches.
- **Pick one:** Choose one as the single Step 1, discard the rest (or save for a future campaign).

Wait for the user's choice before continuing.

Each labeled variant is a COMPLETE, INDEPENDENT email.
- Spintax is applied to one email at a time using only its own lines
- Never mix paragraphs or lines from different variants into the same spintax block

**API constraint:** `wait_in_days` minimum is **1**, not 0 — even for the first email.
**API constraint:** `email_subject` is **required on every step** including thread replies —
cannot be empty string. For thread reply steps, pass the BARE parent subject with NO "Re:"
prefix. The API adds "Re:" automatically. Passing "Re: X" results in "Re: Re: X" in storage.

---

### Step 2 — Apply Spintax

Invoke the spintax-creator skill on each email's copy. Do NOT generate your own variations —
the spintax-creator skill enforces quality rules (first-3-words match, meaning preservation,
5th-grade English, exactly 3 new variations per line).

**Required output format — Bison, always 4 options:**
```
{original sentence | variation 1 | variation 2 | variation 3}
```
The ORIGINAL sentence must appear as option 1. There must be exactly 4 options total (1 original
+ 3 variations). If the spintax-creator output does not include the original as option 1, prepend it.

**Scope — apply spintax to ALL emails in the sequence:**
- Every body paragraph → its own 4-option spintax block
- Subject lines on new-thread emails (1 & 3) → spintaxed
- Thread-reply emails (2 & 4): body paragraphs → spintaxed, subjects → NOT spintaxed

**Do NOT spin these line types:**
- Lines of 3 words or fewer
- Greeting lines that are ONLY a salutation + name variable, e.g. `Hey {FIRST_NAME},` — leave as plain text. These are too short to spin without producing broken variants (e.g. `{FIRST_NAME},` with no greeting word).
- Lines containing only variable tokens, e.g. `{SENDER_EMAIL_SIGNATURE}`
- Specific data points, percentages, numbers from case studies
- P.S. lines that reference a specific company name or metric

**Token optimization:** When invoking the spintax-creator skill, explicitly request only the
"Full Email — Bison Format" section. Ask it to suppress:
- The per-line breakdown (Original → Variations for each line)
- The Instantly `{{RANDOM | ...}}` format section

Only the assembled Bison full-email output is needed for this pipeline.

---

### Step 3 — Spam Check

Run the email-spam-fixer skill on the spintaxed copy. All spam detection rules are defined there.

**Campaign-specific note:** The copy uses Bison spintax format — `{option one | option two}` (single curly braces, pipe-separated). Treat any `{...}` block containing a `|` as spintax and check ALL variants inside it. Blocks without a `|` are variables — skip them.

---

### Step 4 — Fix Spam Words

The email-spam-fixer skill handles all fixes. The fix_spam.py script replaces every occurrence of a flagged word across the full text — so all spintax variants are fixed automatically in one pass.

Invoke fix_spam.py with `--summary` flag. The Spam Fix Summary table in Step 8 uses `words_fixed` count and `unique_words` list from the summary output.

**Post-fix variable token integrity check (required):**
After running fix_spam.py, scan the output for `{{...}}` variable placeholder tokens (the double-brace originals before Step 5 conversion). The spam fixer replaces characters inside ALL text, including token names. If any character inside a variable name was replaced with a Unicode/Cyrillic lookalike — e.g. `{{other_exec_namе}}` where the final `e` is Cyrillic U+0435 — restore it to ASCII before continuing. Corrupted token names break EmailBison variable resolution silently. Only plain-text word occurrences should carry the Cyrillic fix, not the token names.

---

### Step 5 — Convert Variables to EmailBison Format

**EmailBison format: `{VARIABLE}` — single curly braces, ALL CAPS, no pipe.**

**Two different rules depending on variable type:**

**Built-in EmailBison fields → UPPERCASE, exact names below**
These are standard fields EmailBison auto-populates from the lead record.

| Source variable (any casing) | EmailBison format |
|---|---|
| `{{firstName}}` / `{{first_name}}` | `{FIRST_NAME}` |
| `{{companyName}}` / `{{company_name}}` | `{COMPANY}` ← NOT `{COMPANY_NAME}` |
| `{{job_title}}` / `{{jobTitle}}` | `{TITLE}` ← NOT `{JOB TITLE}` |
| `{{sender_signature}}` / `{{signature}}` | `{SENDER_EMAIL_SIGNATURE}` |
| `{{lastName}}` / `{{last_name}}` | `{LAST_NAME}` |
| `{{email}}` | `{EMAIL}` |

**Custom variables → UPPERCASE, SPACES ALLOWED**
Custom variables created per-lead (Clay enrichment, manual entry, etc.) do NOT need underscores. Spaces are valid inside `{}` for custom variable names.
```
{{tech name}}        → {TECH NAME}
{{employee count}}   → {EMPLOYEE COUNT}
{{other exec name}}  → {OTHER EXEC NAME}
{{competitor tool}}  → {COMPETITOR TOOL}
```

**Common built-in EmailBison fields:**
`{FIRST_NAME}`, `{LAST_NAME}`, `{COMPANY}`, `{TITLE}`, `{EMAIL}`, `{SENDER_EMAIL_SIGNATURE}`

Flag which variables need custom enrichment (e.g., via Clay export) vs. standard EmailBison lead fields.

Any `{VARIABLE}` used in a subject line must be listed in `email_subject_variables` when creating sequences.

---

### Step 6 — Convert Bodies to HTML

EmailBison `email_body` expects HTML. Convert plain text after Steps 4–5:

- Each paragraph (block separated by blank lines) → `<p>...</p>`
- Blank lines between paragraphs → `<p><br></p>`
- Single line breaks within a paragraph → `<br>`
- No styling, no inline CSS, no classes
- Variables stay inline: `<p>Hi {FIRST_NAME},</p>`
- Spintax stays inline: `<p>{Option A | Option B | Option C}</p>`

**Example:**
```
Plain text:
Hi {{first_name}},

Noticed {{company_name}} is expanding fast.

Worth a quick chat?

HTML output:
<p>Hi {FIRST_NAME},</p><p><br></p><p>Noticed {COMPANY_NAME} is expanding fast.</p><p><br></p><p>Worth a quick chat?</p>
```

---

### Step 7 — Validate Spintax

Before showing the approval gate, validate the final HTML of every email:

1. **Balanced braces:** Count of `{` must equal count of `}`
2. **Spintax completeness:** Every `{...}` block containing `|` must have ≥ 2 non-empty options
3. **Variable format:** Every `{...}` block without `|` must be ALL CAPS — built-in fields use underscores (`{FIRST_NAME}`), custom variables may contain spaces (`{TECH NAME}`, `{EMPLOYEE COUNT}`) — both are valid

**On failure:**
- Show the exact broken token
- Attempt auto-repair (close unclosed braces, fill empty options)
- Re-validate
- If still broken, flag to user and continue — do not silently push broken copy

---

### Step 8 — Approval Gate

**STOP. Do not push to EmailBison until user says "push it", "create the campaign", or "go ahead".**

Display a condensed summary table:

**Spam Fix Summary**
| Email | Flagged Words | Words Fixed | Status |
|-------|--------------|-------------|--------|
| Email 1 Subject | [list] | N | ✓ Clean / Fixed |
| Email 1 Body | [list] | N | ✓ Fixed |
| Email 2 Body | [list] | N | ✓ Fixed |
| ... | | | |

**Sequence Overview**
| Step | thread_reply | wait_in_days | Subject | Body Lines | Spintaxed? |
|------|-------------|--------------|---------|-----------|-----------|
| 1 | false | 1 | [subject preview] | N paragraphs | Yes |
| 2 | true | 2 | [bare subject] | N paragraphs | Yes |
| 3 | false | 3 | [subject preview] | N paragraphs | Yes |
| 4 | true | 2 | [bare subject] | N paragraphs | Yes |

**Variable List**
- Standard: {FIRST_NAME}, {COMPANY}, ...
- Custom (need Clay enrichment): {VAR_NAME}, ...
- Subject variables: [list]

**Spintax Validation:** PASS / FAIL

Type `preview [1–4]` to see full copy for that email. Otherwise, approve to continue.

---

### Step 9 — EmailBison Workspace Setup

After approval:

1. `get_account_details` (named tool) → verify the current workspace is correct for this client
   If wrong: "I'm currently in [X] workspace but this campaign is for [Y]. Please switch
   to the [Y] workspace in the EmailBison dashboard, then confirm here."
   Wait for confirmation before continuing.

2. `call_api GET /api/custom-variables` → list existing variables
   For each missing variable needed (from Step 5 mapping):
   `call_api POST /api/custom-variables {"name": "VAR_NAME"}`
   422 = already exists → treat as success, continue

3. `list_campaigns` (named tool or `call_api GET /api/campaigns`) → check for name conflicts
   If same name exists, append `v2` or ask user for alternate name

**Campaign naming convention:** `[Client Name] - [Brief Description]`
Example: `Access Storage - Q2 Outbound Tier A`

---

### Step 10 — Push Campaign to EmailBison

Use the confirmed endpoints from the emailbison skill. Do NOT guess endpoint paths.

```
1. [Workspace already confirmed in Step 9 — skip if same workspace as previous campaign]

2. call_api GET /api/custom-variables → confirm variables exist
   call_api POST /api/custom-variables {"name": "VAR_NAME"} for each missing one

3. create_campaign (named tool) — name="[Client] - [Description]", type="outbound"
   → save returned campaign_id

4. call_api PATCH /api/campaigns/{id}/update
   {"plain_text": true, "can_unsubscribe": false, "open_tracking": false,
    "include_auto_replies_in_stats": false, "sequence_prioritization": "followups",
    "max_emails_per_day": 200, "max_new_leads_per_day": 50}

5. Attach sender accounts:
   - Read emailbison/sender-cache.md first. If the current workspace has a cached "primary"
     batch, use those IDs directly and skip all API calls.
   - If not cached: fetch all sender pages via direct HTTP (see emailbison/SKILL.md pagination
     note — the MCP sender_emails list action does NOT support page parameters).
   - When user says "primary only": exclude any sender where ANY tag name contains "Backup"
     (case-insensitive). Tags like "Backup + India", "Backup + USA", "Backup + Emea",
     "Batch 2 (backup)" are all excluded. Remaining senders are primary.
   - After filtering, save the primary IDs to sender-cache.md under the workspace name.
   - mcp__emailbison__campaigns action=attach_sender_emails {"sender_email_ids": [...]}

6. call_api POST /api/campaigns/{id}/schedule
   {"monday":true,"tuesday":true,"wednesday":true,"thursday":true,"friday":true,
    "saturday":false,"sunday":false,"start_time":"08:00","end_time":"17:00",
    "timezone":"America/New_York","save_as_template":false}

7. call_api POST /api/campaigns/v1.1/{id}/sequence-steps
   Steps array — NO "Re:" prefix on thread reply subjects (API adds it):
   Step 1: thread_reply=false, wait_in_days=1, subject=[spintaxed subject], body=[HTML]
   Step 2: thread_reply=true,  wait_in_days=2, subject="[step1 subject bare]", body=[HTML]
   Step 3: thread_reply=false, wait_in_days=3, subject=[spintaxed subject],   body=[HTML]
   Step 4: thread_reply=true,  wait_in_days=2, subject="[step3 subject bare]", body=[HTML]

8. get_campaign (named tool) → verify 4 steps, thread_reply=false/true/false/true,
   subjects present, spintax/variables intact in bodies

9. STOP — show summary, wait for "activate"/"go live"
   Then: call_api PATCH /api/campaigns/{id}/resume
```

---

## Error Handling

| Error | Response |
|---|---|
| Workspace wrong | `get_account_details` → ask user to switch manually in EmailBison dashboard, then confirm |
| fix_spam.py fails | Apply manual Unicode fixes using character-map.md priority order |
| Spintax validation fails | Show broken token, auto-repair attempt, re-validate, then continue |
| Sequence step creation fails | Note which step failed, do NOT delete campaign, offer retry |
| `422: name already taken` on custom variable | Variable already exists — treat as success, continue |
| `422: max_new_leads_per_day must be ≤ max_emails_per_day` | Set both fields in the same update call: `max_emails_per_day=200, max_new_leads_per_day=50` |
| `422: email_subject field is required` on thread reply step | Pass BARE parent subject with NO "Re:" prefix — API adds "Re:" automatically |
| `422: wait_in_days must be at least 1` | Minimum is 1 for all steps including step 1 |
| `422` on schedule creation | Include `"save_as_template": false` in schedule body |
| `Sibling tool call errored` | This cascades when one parallel call fails — re-run the affected calls individually in the next turn |
| Campaign name conflict | Append `v2` or ask user for alternate name |
| User requests changes at approval gate | Re-run from affected step, show new approval gate |

---

## Quick Reference: Bison Spintax vs Variables

| Token | Contains pipe? | Meaning | Example |
|-------|---------------|---------|---------|
| `{opt1 \| opt2 \| opt3}` | YES | Spintax rotation | `{Quick question \| Just curious \| Wondering}` |
| `{FIRST_NAME}` | NO | Variable merge tag | `{COMPANY_NAME}` |

**Never use `{{RANDOM | ...}}` — that is Instantly format and will break in EmailBison.**
