#!/usr/bin/env python3
"""
Fix spam words in email by replacing characters with Cyrillic lookalikes.
"""

import json
import re
import sys
import io
from typing import List, Dict, Tuple

# Ensure stdout uses UTF-8 encoding on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Character replacement map - visually similar Cyrillic characters
CHAR_REPLACEMENTS = {
    # Lowercase — Cyrillic lookalikes
    'a': 'а',  # U+0430 Cyrillic Small Letter A
    'e': 'е',  # U+0435 Cyrillic Small Letter IE
    'o': 'о',  # U+043E Cyrillic Small Letter O
    'c': 'с',  # U+0441 Cyrillic Small Letter ES
    'p': 'р',  # U+0440 Cyrillic Small Letter ER
    'i': 'і',  # U+0456 Cyrillic Small Letter I (Ukrainian)
    'x': 'х',  # U+0445 Cyrillic Small Letter HA
    'y': 'у',  # U+0443 Cyrillic Small Letter U
    's': 'ѕ',  # U+0455 Cyrillic Small Letter DZE
    'n': 'п',  # U+043F Cyrillic Small Letter PE

    # Uppercase — Cyrillic lookalikes
    'A': 'А',  # U+0410 Cyrillic Capital Letter A
    'E': 'Е',  # U+0415 Cyrillic Capital Letter IE
    'O': 'О',  # U+041E Cyrillic Capital Letter O
    'C': 'С',  # U+0421 Cyrillic Capital Letter ES
    'H': 'Н',  # U+041D Cyrillic Capital Letter EN
    'M': 'М',  # U+041C Cyrillic Capital Letter EM
    'K': 'К',  # U+041A Cyrillic Capital Letter KA
    'P': 'Р',  # U+0420 Cyrillic Capital Letter ER
    'T': 'Т',  # U+0422 Cyrillic Capital Letter TE
    'X': 'Х',  # U+0425 Cyrillic Capital Letter HA
    'B': 'В',  # U+0412 Cyrillic Capital Letter VE
    'S': 'Ѕ',  # U+0405 Cyrillic Capital Letter DZE

    # Symbols
    '$': '＄',  # Fullwidth dollar
    '%': '％',  # Fullwidth percent
    '!': 'ǃ',  # Alveolar click
}

# Priority order for replacements (best visual matches first)
REPLACEMENT_PRIORITY = ['o', 'e', 'a', 'c', 'i', 'x', 'O', 'E', 'A', 'C', 'H', 'M', 'K', 'P', 'T', 'X', 'B', 'S']


def replace_char_in_word(word: str) -> Tuple[str, List[str]]:
    """
    Replace ONE character in a word with a Unicode lookalike.
    One replacement is sufficient to bypass spam filters.

    Args:
        word: The word to modify

    Returns:
        Tuple of (modified_word, list_of_changes)
    """
    changes = []
    result = list(word)

    # Try to replace ONE character in priority order (most visually similar first)
    for char in REPLACEMENT_PRIORITY:
        for i, c in enumerate(result):
            if c == char and char in CHAR_REPLACEMENTS:
                original = result[i]
                result[i] = CHAR_REPLACEMENTS[char]
                changes.append(f"'{original}' → '{CHAR_REPLACEMENTS[char]}'")
                return ''.join(result), changes  # Return after ONE replacement

    # If no priority replacements worked, try any available character
    for i, c in enumerate(result):
        if c in CHAR_REPLACEMENTS:
            original = result[i]
            result[i] = CHAR_REPLACEMENTS[c]
            changes.append(f"'{original}' → '{CHAR_REPLACEMENTS[c]}'")
            return ''.join(result), changes  # Return after ONE replacement

    return ''.join(result), changes


def fix_spam_words(email_text: str, spam_words: List[Dict]) -> Dict:
    """
    Fix spam words in email text by applying Unicode replacements.
    Only ONE character is changed per word - that's sufficient to bypass spam filters.
    Also automatically replaces $ and % symbols which are common spam triggers.

    Args:
        email_text: Original email text
        spam_words: List of spam word dicts with 'word' key

    Returns:
        Dict with:
        - fixed_text: Modified email text
        - changes: List of changes made
        - words_fixed: Number of words fixed
    """
    result = {
        "fixed_text": email_text,
        "changes": [],
        "words_fixed": 0
    }

    # Always replace $ and % symbols as they commonly trigger spam filters
    symbol_replacements = {
        '$': '＄',  # Fullwidth dollar
        '%': '％',  # Fullwidth percent
    }

    fixed_text = email_text
    for original_sym, replacement_sym in symbol_replacements.items():
        if original_sym in fixed_text:
            count = fixed_text.count(original_sym)
            fixed_text = fixed_text.replace(original_sym, replacement_sym)
            result["changes"].append({
                "original": original_sym,
                "fixed": replacement_sym,
                "char_changes": [f"'{original_sym}' → '{replacement_sym}' ({count}x)"]
            })
            result["words_fixed"] += count

    if not spam_words:
        result["fixed_text"] = fixed_text
        return result

    # Extract just the words and deduplicate
    words_to_fix = []
    seen_words = set()
    for item in spam_words:
        if isinstance(item, dict):
            word = item.get('word', '')
        else:
            word = str(item)
        if word and word.lower() not in seen_words:
            words_to_fix.append(word)
            seen_words.add(word.lower())

    # Sort by length (shortest first) so individual words get fixed first
    # This ensures words like "friend" get fixed even when part of "Dear friend"
    words_to_fix.sort(key=len)

    # Track which positions have been modified to avoid double-fixing
    # Note: fixed_text already has symbol replacements applied from above
    modified_positions = set()

    for word in words_to_fix:
        if not word or len(word) < 2:
            continue

        # Create a case-insensitive pattern to find the word
        # Use word boundaries to match whole words only
        pattern = r'\b' + re.escape(word) + r'\b'

        matches = list(re.finditer(pattern, fixed_text, re.IGNORECASE))

        for match in reversed(matches):  # Reverse to preserve positions
            start, end = match.start(), match.end()

            # Check if this position overlaps with already modified text
            position_range = set(range(start, end))
            if position_range & modified_positions:
                continue  # Skip - already modified as part of another word

            original = match.group()
            fixed_word, char_changes = replace_char_in_word(original)

            if fixed_word != original:
                # Replace in text
                fixed_text = fixed_text[:start] + fixed_word + fixed_text[end:]

                # Mark these positions as modified
                modified_positions.update(range(start, start + len(fixed_word)))

                result["changes"].append({
                    "original": original,
                    "fixed": fixed_word,
                    "char_changes": char_changes
                })
                result["words_fixed"] += 1

    result["fixed_text"] = fixed_text
    return result


def main():
    """Main function - accepts arguments or JSON input."""
    import argparse

    parser = argparse.ArgumentParser(description="Fix spam words using Unicode replacements")
    parser.add_argument("--text", "-t", type=str, help="Email text to fix")
    parser.add_argument("--file", "-f", type=str, help="File containing email text")
    parser.add_argument("--words", "-w", type=str, help="Comma-separated spam words to fix")
    parser.add_argument("--json", "-j", type=str, help="JSON file with email_text and spam_words")
    parser.add_argument("--summary", "-s", action="store_true", help="Output summary format (count + unique words) instead of full changes array")
    args = parser.parse_args()

    print("=" * 60, file=sys.stderr)
    print("Email Spam Word Fixer", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(file=sys.stderr)

    email_text = ""
    spam_words = []

    # Handle JSON input (file or stdin)
    if args.json:
        with open(args.json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            email_text = data.get('email_text', '')
            spam_words = data.get('spam_words', [])
    elif args.text:
        email_text = args.text
    elif args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            email_text = f.read()
    else:
        # Try reading JSON from stdin
        try:
            data = json.load(sys.stdin)
            email_text = data.get('email_text', '')
            spam_words = data.get('spam_words', [])
        except (json.JSONDecodeError, Exception):
            pass

    # Handle --words argument
    if args.words:
        spam_words = [{"word": w.strip()} for w in args.words.split(",") if w.strip()]

    if not email_text.strip():
        print("Error: No email content provided.", file=sys.stderr)
        print("Usage: python fix_spam.py --text 'email' --words 'free,urgent,click'", file=sys.stderr)
        print("   or: python fix_spam.py --file email.txt --words 'free,urgent'", file=sys.stderr)
        print("   or: echo '{\"email_text\":\"...\",\"spam_words\":[...]}' | python fix_spam.py", file=sys.stderr)
        sys.exit(1)

    if not spam_words:
        print("Warning: No spam words provided. Nothing to fix.", file=sys.stderr)
        print(json.dumps({
            "fixed_text": email_text,
            "changes": [],
            "words_fixed": 0
        }, indent=2, ensure_ascii=False))
        sys.exit(0)

    print("Fixing spam words...", file=sys.stderr)
    print(file=sys.stderr)

    result = fix_spam_words(email_text, spam_words)

    # Output as JSON
    if args.summary:
        unique_words = list(dict.fromkeys(item["original"] for item in result["changes"]))
        print(json.dumps({
            "fixed_text": result["fixed_text"],
            "words_fixed": result["words_fixed"],
            "unique_words": unique_words
        }, ensure_ascii=False))
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
