---
name: spintax-creator
description: This skill should be used when the user wants to create spintax variations, spin text, generate sentence variations for cold emails, create email copy variations, or generate paraphrases for outreach.
---

# Spintax Creator

This skill generates spintax variations for cold email copy, creating dynamic sentence alternatives that maintain consistent messaging while enabling personalization at scale.

## Purpose

To create exactly 3 variations of any input sentence, formatted for use in cold email tools like Instantly and Bison.

## When to Use

This skill activates automatically when receiving text that needs spintax variations. No commands are required—simply provide the sentence to spin.

## Variation Rules

Follow these rules sequentially when generating variations:

1. **Generate exactly 3 variations** - No more, no fewer
2. **Preserve meaning, context, and intent** - The core message must remain identical
3. **Preserve sentence type** - Questions remain questions, statements remain statements
4. **Preserve question intent** - A "how-to" question must remain "how-to" (not become a feasibility question like "is it possible")
5. **Use 5th-grade level English** - Keep non-technical language simple and accessible
6. **Keep technical jargon intact** - Do not simplify industry-specific terms
7. **First 3 words must match original** - Critical for maintaining consistency
8. **Syntax and tense changes allowed** - Restructure within the above constraints

## Output Format

### Part 1: Per-Line Breakdown

For each spinnable line, produce output in this exact format:

```
Original Sentence-> [original text]

Variations:
[Variation 1]
[Variation 2]
[Variation 3]

For you to copy in Instantly-> {{RANDOM | [original] | [var1] | [var2] | [var3]}}

For you to copy in Bison-> {[original] | [var1] | [var2] | [var3]}
```

- Lines that are too short (1-2 words), purely variable-based (e.g., `{{signature}}`), or greetings like `Hey {{firstName}},` should be kept as-is with no variations.
- Separate each line's block with `---`.

**Format specifications:**
- **Instantly format**: Use `{{RANDOM | ... }}` with double curly braces
- **Bison format**: Use `{ ... }` with single curly braces
- Both formats include the original sentence plus all 3 variations

### Part 2: Full Combined Email

After all individual line breakdowns, output the entire email reassembled with spintax inline — once for Instantly and once for Bison. Lines that had no variations stay as-is. Lines that were spintaxed use their respective format.

```
---

## Full Email - Instantly Format

[Full email with all spintaxed lines using {{RANDOM | ... }} and unchanged lines as-is]

---

## Full Email - Bison Format

[Full email with all spintaxed lines using { ... } and unchanged lines as-is]
```

## Example

**Input:**
> How can AI help automate your customer support workflows?

**Output:**

Original Sentence-> How can AI help automate your customer support workflows?

Variations:
How can AI help make your customer support workflows run on their own?
How can AI help streamline your customer support tasks automatically?
How can AI help reduce manual work in your customer support workflows?

For you to copy in Instantly-> {{RANDOM | How can AI help automate your customer support workflows? | How can AI help make your customer support workflows run on their own? | How can AI help streamline your customer support tasks automatically? | How can AI help reduce manual work in your customer support workflows?}}

For you to copy in Bison-> {How can AI help automate your customer support workflows? | How can AI help make your customer support workflows run on their own? | How can AI help streamline your customer support tasks automatically? | How can AI help reduce manual work in your customer support workflows?}
