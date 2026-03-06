#!/usr/bin/env python3
"""
Check email copy for spam using mailmeteor.com spam checker.
Uses Playwright for browser automation.
"""

import json
import sys
import io
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Ensure stdout uses UTF-8 encoding on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def check_spam(email_text: str) -> dict:
    """
    Check email text for spam words using mailmeteor.com.

    Returns:
        dict with keys:
        - score: "poor", "okay", or "great"
        - score_value: numeric score if available
        - spam_words: list of flagged words with categories
        - message: summary message
    """
    result = {
        "score": "unknown",
        "score_value": None,
        "spam_words": [],
        "message": ""
    }

    with sync_playwright() as p:
        # Launch browser using system Chrome
        browser = p.chromium.launch(headless=True, channel="chrome")
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # Navigate to spam checker
            page.goto("https://mailmeteor.com/spam-checker", wait_until="networkidle", timeout=30000)

            # Wait for the page to fully load
            page.wait_for_timeout(2000)

            # Find the text input area - try different selectors
            textarea = None
            selectors = [
                'textarea[placeholder*="email"]',
                'textarea[placeholder*="Email"]',
                'textarea[placeholder*="paste"]',
                'textarea[placeholder*="Paste"]',
                'textarea',
                '[contenteditable="true"]',
                '.editor',
                '#editor'
            ]

            for selector in selectors:
                try:
                    elem = page.wait_for_selector(selector, timeout=3000)
                    if elem:
                        textarea = elem
                        break
                except:
                    continue

            if not textarea:
                # Try to find any input area
                textarea = page.query_selector('textarea') or page.query_selector('[contenteditable="true"]')

            if not textarea:
                result["message"] = "Could not find text input area on page"
                return result

            # Clear and enter the email text
            textarea.click()
            textarea.fill("")
            textarea.fill(email_text)

            # Wait a moment for any auto-analysis
            page.wait_for_timeout(2000)

            # Look for a submit/check button and click if found
            button_selectors = [
                'button:has-text("Check")',
                'button:has-text("Analyze")',
                'button:has-text("Test")',
                'button:has-text("Submit")',
                'button[type="submit"]',
                '.btn-primary',
                'button.primary'
            ]

            for selector in button_selectors:
                try:
                    button = page.query_selector(selector)
                    if button and button.is_visible():
                        button.click()
                        break
                except:
                    continue

            # Wait for results to load
            page.wait_for_timeout(5000)

            # Extract the score - look for common score indicators
            score_text = ""
            score_selectors = [
                '.score',
                '[class*="score"]',
                '[class*="result"]',
                '.rating',
                '[class*="rating"]',
                'h2',
                'h3',
                '.badge'
            ]

            for selector in score_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    for elem in elements:
                        text = elem.inner_text().lower()
                        if any(word in text for word in ['poor', 'bad', 'spam', 'okay', 'good', 'great', 'excellent']):
                            score_text = text
                            break
                    if score_text:
                        break
                except:
                    continue

            # Determine score category
            if 'poor' in score_text or 'bad' in score_text or 'spam' in score_text:
                result["score"] = "poor"
            elif 'great' in score_text or 'excellent' in score_text:
                result["score"] = "great"
            elif 'okay' in score_text or 'good' in score_text:
                result["score"] = "okay"

            # Try to extract numeric score
            import re
            numbers = re.findall(r'(\d+(?:\.\d+)?)\s*(?:/\s*\d+|%)?', score_text)
            if numbers:
                result["score_value"] = float(numbers[0])

            # Extract spam words - look for highlighted or flagged words
            spam_words = []
            spam_selectors = [
                '.spam-word',
                '[class*="spam"]',
                '[class*="warning"]',
                '[class*="highlight"]',
                '.flagged',
                '[class*="flagged"]',
                'mark',
                '.badge-warning',
                '.badge-danger',
                'li:has-text("spam")',
                '[class*="issue"]'
            ]

            for selector in spam_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    for elem in elements:
                        text = elem.inner_text().strip()
                        if text and len(text) < 50:  # Reasonable word/phrase length
                            # Try to get category if available
                            parent = elem.query_selector('xpath=..')
                            category = ""
                            if parent:
                                parent_text = parent.inner_text()
                                for cat in ['urgency', 'shady', 'money', 'overpromise', 'unnatural']:
                                    if cat in parent_text.lower():
                                        category = cat
                                        break

                            spam_words.append({
                                "word": text,
                                "category": category
                            })
                except:
                    continue

            # Filter out website UI noise
            ui_noise = {
                'spam checker', 'spam', 'checker', 'mailmeteor', 'video', 'tutorial',
                'min', 'that', 'look', 'and', 'more', 'your', 'emails', 'with', 'this',
                'shady', 'urgency', 'money', 'overpromise', 'unnatural',  # category labels
                'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
                'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'by', 'at', 'from',
            }

            def is_valid_spam_word(word):
                """Check if a word is a valid spam word (not UI noise)."""
                word_lower = word.lower().strip()
                # Filter out UI noise
                if word_lower in ui_noise:
                    return False
                # Filter out category summary lines (contain emoji or parentheses with numbers)
                if any(c in word for c in '🔞🚨💰🤩💬›'):
                    return False
                if re.match(r'.*\(\d+\).*', word):
                    return False
                # Filter out very short words
                if len(word_lower) < 3:
                    return False
                # Filter out words that are just numbers
                if word_lower.isdigit():
                    return False
                return True

            # Deduplicate and filter
            seen = set()
            unique_words = []
            for item in spam_words:
                word = item["word"]
                if word.lower() not in seen and is_valid_spam_word(word):
                    seen.add(word.lower())
                    unique_words.append(item)

            result["spam_words"] = unique_words

            # Generate summary message
            if result["score"] == "great":
                result["message"] = "Your email looks great! No spam issues detected."
            elif result["score"] == "okay":
                result["message"] = f"Your email is okay but could be improved. Found {len(result['spam_words'])} potential spam words."
            elif result["score"] == "poor":
                result["message"] = f"Your email may trigger spam filters. Found {len(result['spam_words'])} spam words to fix."
            else:
                result["message"] = "Analysis complete. Review the detected spam words."

        except PlaywrightTimeout as e:
            result["message"] = f"Timeout while loading page: {str(e)}"
        except Exception as e:
            result["message"] = f"Error during analysis: {str(e)}"
        finally:
            browser.close()

    return result


def main():
    """Main function - reads email from stdin or prompts for input."""
    import argparse

    parser = argparse.ArgumentParser(description="Check email for spam using mailmeteor.com")
    parser.add_argument("--text", "-t", type=str, help="Email text to check")
    parser.add_argument("--file", "-f", type=str, help="File containing email text")
    args = parser.parse_args()

    print("=" * 60, file=sys.stderr)
    print("Email Spam Checker (powered by mailmeteor.com)", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(file=sys.stderr)

    email_text = ""

    # Priority: --text > --file > stdin
    if args.text:
        email_text = args.text
    elif args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            email_text = f.read()
    else:
        # Try reading from stdin
        email_text = sys.stdin.read()

    if not email_text.strip():
        print("Error: No email content provided.", file=sys.stderr)
        print("Usage: python check_spam.py --text 'email content'", file=sys.stderr)
        print("   or: python check_spam.py --file email.txt", file=sys.stderr)
        print("   or: echo 'email content' | python check_spam.py", file=sys.stderr)
        sys.exit(1)

    print("Analyzing email for spam...", file=sys.stderr)
    print(file=sys.stderr)

    result = check_spam(email_text)

    # Output as JSON for easy parsing
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
