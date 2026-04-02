---
name: emailbison
description: Reference skill for working with the EmailBison MCP. Contains all rules for sequences, campaigns, variables, pagination, and defaults. Use when creating or managing EmailBison campaigns, sequences, sender accounts, leads, or any EmailBison MCP operation.
---

# EmailBison MCP — Rules & Reference

## Connection

- **MCP type:** Hosted HTTP MCP endpoint — no local install required
- **Setup:** Follow your EmailBison instance's MCP setup guide at
  `https://[your-instance-url]/integrations/emailbison-mcp`
  Register the MCP endpoint in Claude's MCP settings with your API token.
- **Tool style:** Composite tools — `mcp__emailbison__campaigns`, `mcp__emailbison__sequences`,
  `mcp__emailbison__sender_emails`, `mcp__emailbison__settings`, `mcp__emailbison__workspaces`, etc.
  There is NO standalone `call_api` tool — use the composite tools below.
- **Auth:** Bearer token configured once in MCP settings — no manual key needed in tool calls.
- **API base URL:** Your instance URL + `/api` — set once in MCP config, not repeated in calls.

---

## Confirmed API Endpoint Reference

Do NOT use search_api_spec for these operations — endpoints are confirmed here.

### Workspace Management

Use `mcp__emailbison__settings action=get_account` to verify the current workspace.
If the current workspace is wrong, ask the user to manually switch via the EmailBison dashboard,
then confirm before continuing.

Sub-workspace switching via API is not supported — do NOT attempt programmatic workspace switching.

### Custom Variables

| Operation | MCP Tool + Action |
|---|---|
| List variables | `mcp__emailbison__settings action=list_custom_variables` |
| Create variable | `mcp__emailbison__settings action=create_custom_variable` |

### Campaign Operations

| Operation | MCP Tool + Action |
|---|---|
| List campaigns | `mcp__emailbison__campaigns action=list` |
| Create campaign | `mcp__emailbison__campaigns action=create` — `name`, `type="outbound"` |
| Get campaign | `mcp__emailbison__campaigns action=get` — `campaign_id` |
| Update campaign | `mcp__emailbison__campaigns action=update` — `campaign_id` + settings |
| Pause | `mcp__emailbison__campaigns action=pause` — `campaign_id` |
| Resume | `mcp__emailbison__campaigns action=resume` — `campaign_id` |
| List attached senders | `mcp__emailbison__campaigns action=get_sender_emails` — `campaign_id` |
| Attach senders | `mcp__emailbison__campaigns action=attach_sender_emails` — `campaign_id`, `sender_email_ids` |
| Create schedule | `mcp__emailbison__campaigns action=create_schedule` — `campaign_id` + schedule fields |
| Get schedule | `mcp__emailbison__campaigns action=get_schedule` — `campaign_id` |

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

| Operation | MCP Tool + Action |
|---|---|
| Get steps | `mcp__emailbison__sequences action=get` — `campaign_id` |
| Create steps | `mcp__emailbison__sequences action=create` — `campaign_id`, `title`, `steps` array |
| Delete step | `mcp__emailbison__sequences action=delete_step` — `sequence_step_id` |

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

`mcp__emailbison__sender_emails action=list`

> ⚠️ **Pagination limitation:** The `sender_emails action=list` does NOT support page parameters. Values passed are silently ignored and page 1 (15 results) is always returned. See the Pagination section below for the workaround.

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

### ⚠️ MCP sender_emails pagination limitation

`mcp__emailbison__sender_emails action=list` does **NOT** support page parameters.
The MCP schema exposes no `page` or `per_page` fields for this action — any values passed are silently ignored and page 1 (15 results) is always returned.

**For workspaces with more than 15 senders:**
1. **Use sender-cache.md first** — if the workspace's primary sender IDs are already cached, skip pagination entirely.
2. **If not cached:** use direct HTTP calls (curl or equivalent) with your Bearer token:
   `GET /api/sender-emails?per_page=100&page=N` — loop through all pages, filter client-side.
   Your Bearer token is stored in the MCP process environment — check your MCP config for the value.
3. **After filtering:** append the workspace name and primary sender IDs to `sender-cache.md` so future campaigns skip this step.

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
1. mcp__emailbison__settings action=get_account → verify current workspace matches the client
   If wrong: ask user to switch manually in EmailBison dashboard → wait for confirmation

2. mcp__emailbison__settings action=list_custom_variables → check what custom variables already exist
   422 if near 15 vars: just attempt creation and handle 422s

3. mcp__emailbison__settings action=create_custom_variable {"name": "VAR_NAME"} → create each missing variable
   422 = already exists → treat as success, continue

4. mcp__emailbison__campaigns action=create → name="...", type="outbound", save returned campaign_id

5. mcp__emailbison__campaigns action=update → campaign_id + Campaign Defaults (see above)

6. Read sender-cache.md (same dir as this skill) → if workspace has cached IDs, confirm batch with user, skip API
   If not cached → use direct HTTP GET /api/sender-emails?per_page=100&page=N (loop all pages) → filter client-side
   → append workspace name, ID, and sender IDs to sender-cache.md
   → mcp__emailbison__campaigns action=attach_sender_emails → campaign_id + sender_email_ids

7. mcp__emailbison__campaigns action=create_schedule → campaign_id + schedule body
   Body must include "save_as_template": false (required to avoid 422)
   Default: Mon-Fri, 08:00-17:00 ET

8. mcp__emailbison__sequences action=create → campaign_id + all steps in one call

9. mcp__emailbison__campaigns action=get → campaign_id → verify step count, thread_reply values, subjects present

10. STOP → show summary → wait for "activate"/"go live"
    Then: mcp__emailbison__campaigns action=resume → campaign_id
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
3. If not cached → use direct HTTP GET /api/sender-emails?per_page=100&page=N (loop all pages) → show list → confirm
   → append workspace name, ID, and sender IDs to `sender-cache.md` before continuing
4. mcp__emailbison__campaigns action=attach_sender_emails {"sender_email_ids": [...]}
