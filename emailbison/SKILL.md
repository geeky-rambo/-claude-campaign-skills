---
name: emailbison
description: Reference skill for working with the EmailBison MCP. Contains all rules for sequences, campaigns, variables, pagination, and defaults. Use when creating or managing EmailBison campaigns, sequences, sender accounts, leads, or any EmailBison MCP operation.
---

# EmailBison MCP — Rules & Reference

## Connection

- **MCP:** `emailbison` (HTTP, connected to `https://mcp.emailbison.com/mcp`)
- **Instance URL:** `https://send.oneaway.io`
- **Auth:** Configured via MCP headers — no manual API key needed in tool calls

---

## Confirmed API Endpoint Reference

Base URL for all call_api calls: `https://send.oneaway.io/api`

Do NOT use search_api_spec for these operations — endpoints are confirmed here.

### Workspace Management

Use `get_account_details` (named tool) to verify the current workspace.
If the current workspace is wrong, ask the user to manually switch via the EmailBison dashboard,
then confirm before continuing.

Sub-workspace switching via API is not supported on the HTTP MCP — the `/workspaces/v1.1`
endpoints do not exist on this server. Do NOT attempt `call_api` for workspace switching.

### Custom Variables

| Operation | Method | Endpoint |
|---|---|---|
| List variables | GET | `/api/custom-variables` |
| Create variable | POST | `/api/custom-variables` |

### Campaign Operations

| Operation | Method | Endpoint | Body |
|---|---|---|---|
| List campaigns | GET | `/api/campaigns` | — |
| Create campaign | POST | `/api/campaigns` | `{"name":"...","type":"outbound"}` |
| Get campaign | GET | `/api/campaigns/{id}` | — |
| Update campaign | PATCH | `/api/campaigns/{id}/update` | settings object |
| Pause | POST | `/api/campaigns/{id}/pause` | — |
| Resume | PATCH | `/api/campaigns/{id}/resume` | — |
| List attached senders | GET | `/api/campaigns/{id}/sender-emails` | — |
| Attach senders | POST | `/api/campaigns/{id}/attach-sender-emails` | `{"sender_email_ids":[...]}` |
| Create schedule | POST | `/api/campaigns/{id}/schedule` | schedule object |
| Get schedule | GET | `/api/campaigns/{id}/schedule` | — |

**Create schedule body must include `"save_as_template": false` or the API returns 422.**

Full default body:
```json
{
  "monday": true, "tuesday": true, "wednesday": true,
  "thursday": true, "friday": true,
  "saturday": false, "sunday": false,
  "start_time": "08:00", "end_time": "17:00",
  "timezone": "America/New_York",
  "save_as_template": false
}
```

### Sequence Steps

| Operation | Method | Endpoint |
|---|---|---|
| Get steps | GET | `/api/campaigns/v1.1/{campaign_id}/sequence-steps` |
| Create steps | POST | `/api/campaigns/v1.1/{campaign_id}/sequence-steps` |
| Delete step | DELETE | `/api/campaigns/sequence-steps/{step_id}` |

**Warning — PUT step update is unreliable:** PUT `/api/campaigns/v1.1/sequence-steps/{step_id}`
frequently returns 422. If sequence step bodies or subjects need fixing after campaign creation,
advise the user to edit manually in the EmailBison dashboard. Do not attempt automated PUT
updates for post-creation repairs.

**Confirmed POST body for sequence step creation:**
```json
{
  "title": "Campaign Step Title",
  "sequence_steps": [
    {
      "order": 1,
      "email_subject": "your subject here",
      "email_body": "<p>HTML body here</p>",
      "wait_in_days": 1,
      "thread_reply": false,
      "variant": false
    }
  ]
}
```
- `title`: top-level string, any descriptive label
- `sequence_steps`: array (send all steps in one call)
- `order`: 1-indexed position in sequence
- `variant`: false for normal steps, true for A/B variants

### A/B Variant Steps

To create an A/B variant of a sequence step (additional version tested against the parent):

Add to the step object in the POST `/api/campaigns/v1.1/{id}/sequence-steps` body:
- `"variant": true` — marks this as an A/B variant, not a new sequential step
- `"variant_from_step": N` — 1-indexed order number of the parent step to A/B test

Example — adding a variant of step 1:
```json
{
  "email_subject": "Different angle subject",
  "email_body": "<p>Alternative copy...</p>",
  "wait_in_days": 1,
  "thread_reply": false,
  "variant": true,
  "variant_from_step": 1
}
```

**API inconsistency:** POST uses `variant_from_step` (step order number, 1-indexed).
The PUT endpoint (if ever used) uses `variant_from_step_id` (step database ID). These are
different values — do not confuse them.

### Sender Emails (Global List)

```
call_api GET /api/sender-emails
```

---

## Sequence Rules — READ BEFORE CREATING SEQUENCES

### `wait_in_days` = delay AFTER that step (before the next step)

- `wait_in_days` on Step 1 = how many days to wait AFTER Step 1 before sending Step 2
- `wait_in_days` on Step 2 = how many days to wait AFTER Step 2 before sending Step 3
- `wait_in_days` on the last step is irrelevant (no next step follows)

### Example: "3 days between step 1→2, 5 days between step 2→3"
- Step 1: `wait_in_days: 3`
- Step 2: `wait_in_days: 5`
- Step 3: `wait_in_days: 1` ← irrelevant, last step

**NEVER set Step 1 `wait_in_days` to 1 thinking it means "send on day 1" — it means "wait 1 day before step 2".**

---

### `email_subject_variables` — Do NOT duplicate variables already in the subject

If the subject already contains `{FIRST_NAME}`, do NOT also pass `email_subject_variables: ["{FIRST_NAME}"]`.

The API appends variables from that array to the subject, causing double `{FIRST_NAME} {FIRST_NAME}`.

**Only use `email_subject_variables` if the variable is NOT already present in the subject text.**

---

### API Hard Constraints (confirmed from live campaigns)

| Constraint | Rule |
|---|---|
| `wait_in_days` minimum | **1** on all steps, including step 1 |
| `email_subject` on thread replies | Required — pass the BARE parent subject string with NO "Re:" prefix. The API prepends "Re:" automatically. If you pass "Re: Business storage", the stored subject will be "Re: Re: Business storage". Pass "Business storage" only. |
| `max_new_leads_per_day` | Must be ≤ `max_emails_per_day` — set both in the same update call |

---

## Campaign Defaults — Apply Unless User Specifies Otherwise

Apply these in the PATCH `/api/campaigns/{id}/update` call:

```json
{
  "plain_text": true,
  "can_unsubscribe": false,
  "open_tracking": false,
  "include_auto_replies_in_stats": false,
  "sequence_prioritization": "followups",
  "max_emails_per_day": 200,
  "max_new_leads_per_day": 50
}
```

**Note:** `can_unsubscribe` and `open_tracking` default to DISABLED (false).
`max_new_leads_per_day` must always be ≤ `max_emails_per_day` — set both in the same call.

---

## Variable Handling

### Built-in Lead Fields — Do NOT create as custom variables

These are populated by EmailBison from the lead record automatically:

| Field | Format |
|---|---|
| First name | `{FIRST_NAME}` |
| Last name | `{LAST_NAME}` |
| Email address | `{EMAIL}` |
| Company name | `{COMPANY}` |
| Job title | `{TITLE}` |
| Sender signature | `{SENDER_EMAIL_SIGNATURE}` |

### Custom Variables — Create if missing

If email copy contains variables like `{PAIN_POINT}`, `{INDUSTRY}`, `{COMPETITOR}`, etc.:

1. Call `list custom variables` first to check what exists
2. If a variable is missing → create it via the settings tool before creating the campaign
3. `422: The name has already been taken` = variable exists → treat as success, continue

**API returns page 1 only (15 results).** If variable count is near or over 15, just attempt creation and handle 422s.

---

## Pagination — Always Paginate

The API paginates all list endpoints (default 15 per page).

**NEVER assume page 1 is all the data.** Always check `meta.last_page` and loop through all pages.

### Best practice
- Use `per_page=100` (max) to minimize round-trips
- Loop: `page=1`, increment until `page >= meta.last_page`
- When filtering by tags: fetch ALL pages first, then filter client-side

### Endpoints that paginate
- Sender emails: `per_page=100&page=N`
- Leads: `per_page=100&page=N`
- Campaigns: `per_page=100&page=N`

---

## Spintax Format

EmailBison uses pipe-separated single-brace spintax:

```
{option one | option two | option three}
```

**Variables nested inside spintax** — wrap the whole block in `{`:
```
{{FIRST_NAME} - Option one text. | {FIRST_NAME} - Option two text. | {FIRST_NAME} - Option three.}
```
The leading `{{` is the outer spintax `{` immediately followed by `{FIRST_NAME}` — confirmed working in live campaigns.

**NEVER use `{{RANDOM | ...}}` — that is Instantly format and will break in EmailBison.**

---

## Standard Campaign Creation Order

```
1. get_account_details (named tool) → verify current workspace matches the client
   If wrong: ask user to switch manually in EmailBison dashboard → wait for confirmation

2. call_api GET /api/custom-variables → check what custom variables already exist
   422 if near 15 vars: just attempt creation and handle 422s

3. call_api POST /api/custom-variables {"name": "VAR_NAME"} → create each missing variable
   422 = already exists → treat as success, continue

4. create_campaign (named tool) → type=outbound, save returned campaign_id

5. call_api PATCH /api/campaigns/{id}/update → apply Campaign Defaults (see above)

6. Read sender-cache.md (same dir as this skill) → if workspace has cached IDs, confirm batch with user, skip API
   If not cached → call_api GET /api/sender-emails?per_page=100 → show list → confirm with user
   → append workspace name, ID, and sender IDs to sender-cache.md → call_api POST /api/campaigns/{id}/attach-sender-emails

7. call_api POST /api/campaigns/{id}/schedule
   Body must include "save_as_template": false (required to avoid 422)
   Default: Mon-Fri, 08:00-17:00 ET

8. call_api POST /api/campaigns/v1.1/{id}/sequence-steps → all steps in one call

9. get_campaign (named tool) → verify step count, thread_reply values, subjects present

10. STOP → show summary → wait for "activate"/"go live"
    Then: call_api PATCH /api/campaigns/{id}/resume
```

---

## Error Handling

| Error | Response |
|---|---|
| `422: name already taken` on custom variable | Variable exists — treat as success, continue |
| `422: max_new_leads_per_day must be ≤ max_emails_per_day` | Set both fields in the same update call |
| `422: email_subject field is required` | Cannot be empty — pass BARE parent subject with no "Re:" prefix; API adds "Re:" automatically |
| `422: wait_in_days must be at least 1` | Minimum is 1 for all steps including step 1 |
| `422` on schedule creation | Include `"save_as_template": false` in schedule body |
| Workspace wrong | Ask user to switch manually in EmailBison dashboard, then confirm |
| Campaign name conflict | Append `v2` or ask user for alternate name |
| Sender attachment not specified | Ask the user which sender accounts to attach |
| Sibling tool call errored | Re-run affected calls individually on next turn |

---

## Sender Cache

Sender IDs for known workspaces are stored in `sender-cache.md` (same directory as this skill).

**Step 6 of every campaign:**
1. Read `sender-cache.md`
2. If the current workspace has cached IDs → confirm batch with user → skip API entirely
3. If not cached → call_api GET /api/sender-emails?per_page=100 → show list → confirm
   → append workspace name, ID, and sender IDs to `sender-cache.md` before continuing
4. call_api POST /api/campaigns/{id}/attach-sender-emails {"sender_email_ids": [...]}
