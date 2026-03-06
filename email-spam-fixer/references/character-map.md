# Unicode Character Replacement Map

This document contains the exact Unicode characters used to replace letters in spam words.

## Primary Replacements

| Original | Replacement | Unicode Name | Code Point |
|----------|-------------|--------------|------------|
| `a` | `α` | Greek Small Letter Alpha | U+03B1 |
| `e` | `ė` | Latin Small Letter E with Dot Above | U+0117 |
| `i` | `𝔦` | Mathematical Fraktur Small I | U+1D526 |
| `o` | `ο` | Greek Small Letter Omicron | U+03BF |
| `u` | `ù` | Latin Small Letter U with Grave | U+00F9 |
| `c` | `ċ` | Latin Small Letter C with Dot Above | U+010B |
| `l` | `І` | Cyrillic Capital Letter Byelorussian-Ukrainian I | U+0406 |
| `n` | `ո` | Armenian Small Letter Vo | U+0578 |
| `s` | `ѕ` | Cyrillic Small Letter Dze | U+0455 |
| `t` | `τ` | Greek Small Letter Tau | U+03C4 |

## Symbol Replacements

| Original | Replacement | Unicode Name | Code Point |
|----------|-------------|--------------|------------|
| `$` | `＄` | Fullwidth Dollar Sign | U+FF04 |
| `%` | `％` | Fullwidth Percent Sign | U+FF05 |
| `0` | `ο` | Greek Small Letter Omicron | U+03BF |
| `!` | `ǃ` | Latin Letter Alveolar Click | U+01C3 |

## Uppercase Replacements

| Original | Replacement | Unicode Name | Code Point |
|----------|-------------|--------------|------------|
| `A` | `Α` | Greek Capital Letter Alpha | U+0391 |
| `E` | `Ε` | Greek Capital Letter Epsilon | U+0395 |
| `I` | `Ι` | Greek Capital Letter Iota | U+0399 |
| `O` | `Ο` | Greek Capital Letter Omicron | U+039F |
| `S` | `Ѕ` | Cyrillic Capital Letter Dze | U+0405 |
| `T` | `Τ` | Greek Capital Letter Tau | U+03A4 |

## Copy-Paste Reference

For quick copy-paste, here are the replacement characters:

```
Lowercase:
a → α
e → ė
i → 𝔦
o → ο
u → ù
c → ċ
l → І
n → ո
s → ѕ
t → τ

Uppercase:
A → Α
E → Ε
I → Ι
O → Ο
S → Ѕ
T → Τ

Symbols:
$ → ＄
% → ％
0 → ο
! → ǃ
```

## Usage Notes

1. **Selective Replacement**: Don't replace all instances of a character. Replace just enough to break the spam word pattern.

2. **Prioritize**: Start with vowels (a, e, i, o) as they appear in most words and are least noticeable when replaced.

3. **Visual Similarity**: All replacements are chosen to be visually identical or nearly identical in most fonts.

4. **Email Client Compatibility**: These characters render correctly in all major email clients (Gmail, Outlook, Apple Mail, etc.)
