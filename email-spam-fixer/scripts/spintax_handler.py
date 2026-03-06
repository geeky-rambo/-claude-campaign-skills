#!/usr/bin/env python3
"""
Handle spintax format for email spam fixer.
Parses {{RANDOM | opt1 | opt2 | ...}} format, processes each variation, and reconstructs.
"""

import re
import sys
import io

# Ensure stdout uses UTF-8 encoding on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def is_spintax(text: str) -> bool:
    """Check if text contains spintax format."""
    return bool(re.search(r'\{\{RANDOM\s*\|', text, re.IGNORECASE))


def parse_spintax(text: str) -> list:
    """
    Parse spintax format and extract all variations.

    Args:
        text: Text in format {{RANDOM | opt1 | opt2 | opt3}}

    Returns:
        List of variations (strings)
    """
    # Match the spintax pattern
    match = re.search(r'\{\{RANDOM\s*\|(.*?)\}\}', text, re.IGNORECASE | re.DOTALL)

    if not match:
        return [text]

    # Extract the content between {{RANDOM | and }}
    content = match.group(1)

    # Split by | but be careful with multiline content
    variations = []
    current = ""
    depth = 0

    for char in content:
        if char == '{':
            depth += 1
            current += char
        elif char == '}':
            depth -= 1
            current += char
        elif char == '|' and depth == 0:
            variations.append(current.strip())
            current = ""
        else:
            current += char

    # Don't forget the last variation
    if current.strip():
        variations.append(current.strip())

    return variations


def reconstruct_spintax(variations: list) -> str:
    """
    Reconstruct spintax format from list of variations.

    Args:
        variations: List of text variations

    Returns:
        Text in format {{RANDOM | opt1 | opt2 | opt3}}
    """
    if len(variations) == 1:
        return variations[0]

    # Join with | separator
    joined = " | ".join(variations)
    return "{{RANDOM | " + joined + "}}"


def main():
    """Test the spintax handler."""
    import argparse

    parser = argparse.ArgumentParser(description="Parse and reconstruct spintax format")
    parser.add_argument("--text", "-t", type=str, help="Spintax text to parse")
    parser.add_argument("--parse", "-p", action="store_true", help="Parse spintax to variations")
    parser.add_argument("--reconstruct", "-r", action="store_true", help="Reconstruct from variations")
    args = parser.parse_args()

    if args.text:
        if args.parse or not args.reconstruct:
            variations = parse_spintax(args.text)
            print(f"Found {len(variations)} variations:")
            for i, v in enumerate(variations, 1):
                print(f"\n--- Variation {i} ---")
                print(v)
    else:
        # Read from stdin
        text = sys.stdin.read()
        variations = parse_spintax(text)
        print(f"Found {len(variations)} variations:")
        for i, v in enumerate(variations, 1):
            print(f"\n--- Variation {i} ---")
            print(v)


if __name__ == "__main__":
    main()
