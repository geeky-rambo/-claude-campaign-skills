# Cyrillic Character Replacement Map

This document contains the exact Cyrillic characters used to replace letters in spam words.

## Lowercase Replacements

| Original | Replacement | Unicode Name | Code Point |
|----------|-------------|--------------|------------|
| `a` | `а` | Cyrillic Small Letter A | U+0430 |
| `e` | `е` | Cyrillic Small Letter IE | U+0435 |
| `o` | `о` | Cyrillic Small Letter O | U+043E |
| `c` | `с` | Cyrillic Small Letter ES | U+0441 |
| `p` | `р` | Cyrillic Small Letter ER | U+0440 |
| `i` | `і` | Cyrillic Small Letter I (Ukrainian) | U+0456 |
| `x` | `х` | Cyrillic Small Letter HA | U+0445 |
| `y` | `у` | Cyrillic Small Letter U | U+0443 |
| `s` | `ѕ` | Cyrillic Small Letter DZE | U+0455 |
| `n` | `п` | Cyrillic Small Letter PE | U+043F |

## Uppercase Replacements

| Original | Replacement | Unicode Name | Code Point |
|----------|-------------|--------------|------------|
| `A` | `А` | Cyrillic Capital Letter A | U+0410 |
| `E` | `Е` | Cyrillic Capital Letter IE | U+0415 |
| `O` | `О` | Cyrillic Capital Letter O | U+041E |
| `C` | `С` | Cyrillic Capital Letter ES | U+0421 |
| `H` | `Н` | Cyrillic Capital Letter EN | U+041D |
| `M` | `М` | Cyrillic Capital Letter EM | U+041C |
| `K` | `К` | Cyrillic Capital Letter KA | U+041A |
| `P` | `Р` | Cyrillic Capital Letter ER | U+0420 |
| `T` | `Т` | Cyrillic Capital Letter TE | U+0422 |
| `X` | `Х` | Cyrillic Capital Letter HA | U+0425 |
| `B` | `В` | Cyrillic Capital Letter VE | U+0412 |
| `S` | `Ѕ` | Cyrillic Capital Letter DZE | U+0405 |

## Symbol Replacements

| Original | Replacement | Unicode Name | Code Point |
|----------|-------------|--------------|------------|
| `$` | `＄` | Fullwidth Dollar Sign | U+FF04 |
| `%` | `％` | Fullwidth Percent Sign | U+FF05 |
| `!` | `ǃ` | Latin Letter Alveolar Click | U+01C3 |

## Copy-Paste Reference

For quick copy-paste, here are the replacement characters:

```
Lowercase:
a → а
e → е
o → о
c → с
p → р
i → і
x → х
y → у
s → ѕ
n → п

Uppercase:
A → А
E → Е
O → О
C → С
H → Н
M → М
K → К
P → Р
T → Т
X → Х
B → В
S → Ѕ

Symbols:
$ → ＄
% → ％
! → ǃ
```

## Usage Notes

1. **Selective Replacement**: Don't replace all instances of a character. Replace just enough to break the spam word pattern.

2. **Priority**: Start with vowels (o, e, a) as they appear in most words and are least noticeable when replaced.

3. **Visual Similarity**: All Cyrillic replacements are visually identical or nearly identical to their Latin counterparts in most fonts.

4. **Email Client Compatibility**: Cyrillic characters render correctly in all major email clients (Gmail, Outlook, Apple Mail, etc.)
