# PII Regex Patterns

Patterns used by Step 6 (PII flagging) to detect columns whose values look like personally identifiable information. Heuristic by design — false positives are acceptable (manual confirmation is cheap); false negatives are not (a missed PII column can leak).

## Email

```python
EMAIL_RE = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
```

A column is PII-email-shaped if ≥ 50% of non-null sampled values match the regex.

## Phone

```python
PHONE_RE = r"^[+]?[\s()-]*\d[\s()-]*\d[\s()-]*\d[\s()-]*\d[\s()-]*\d[\s()-]*\d[\s()-]*\d(?:[\s()-]*\d){0,8}$"
```

Match if value has 7-15 digits with common separators (space, hyphen, parentheses, dot). High false-positive rate on free-form numbers — confirm with column name (`phone`, `tel`, `mobile`, `cell`).

## SSN (US)

```python
SSN_RE = r"^\d{3}-\d{2}-\d{4}$"
SSN_NUMERIC_RE = r"^\d{9}$"
```

The dashed form is high-confidence. The 9-digit form is ambiguous (could be ZIP+4, ID); confirm with column name (`ssn`, `social`, `tax_id`).

## Credit card

```python
CC_RE = r"^\d{13,19}$"  # plus Luhn check
```

Apply Luhn algorithm on candidate matches to reduce false positives. Card numbers in plaintext are almost always a finding regardless.

## Person name (heuristic)

```python
NAME_HINT_RE = r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}$"
```

Two-to-four TitleCase tokens. Very heuristic — confirm with column name (`name`, `first_name`, `last_name`, `full_name`, `given_name`).

## Date of birth

If a column is classified datetime AND name matches `^dob$|date_of_birth|birth_date|birthday`, flag as PII (DOB is often PII / sensitive under HIPAA / GDPR).

## Address

Address detection by regex is unreliable. Defer to column name:

```python
ADDRESS_HINT_NAMES = {
    "address", "street", "street_address", "line1", "line2",
    "city", "state", "zip", "zipcode", "postal_code", "country",
}
```

Flag any object-typed column whose name matches an entry in this set.

## IP address

```python
IPV4_RE = r"^(\d{1,3}\.){3}\d{1,3}$"
IPV6_RE = r"^([0-9a-fA-F]{1,4}:){2,7}[0-9a-fA-F]{0,4}$"
```

IP addresses are PII under GDPR (when linked to an individual) and under many corporate privacy policies. Flag.

## Policy options

| Policy | Behavior |
|---|---|
| `flag` (default) | Note PII shape in the dictionary's `Notes` column. Show raw sample values. |
| `redact` | Replace sample values with `***` (preserve count and length only). |
| `ignore` | Do not check; show raw sample values. (Use only when PII is already known to be absent.) |

## Output integration

In the dictionary's Notes column, PII findings appear as:

```
PII-shape: email (12 of 12 samples match); confirm and redact per policy
```

If multiple patterns match, list each. If `pii_policy: redact`, the dictionary's `Sample values` column shows `***` for the affected column instead of the raw values.
