# Pydantic temporal-validator example

A working template for the 3-invariant temporal validator. Adapt to the local pipeline schema.

```python
import os
from datetime import date, datetime
from pydantic import BaseModel, model_validator

PIPELINE_TODAY = date.fromisoformat(
    os.environ.get("PIPELINE_TODAY", date.today().isoformat())
)


class Incident(BaseModel):
    incident_id: str
    event_date: date | None             # when the incident happened (may be null)
    disclosure_date: date                # when the incident was publicly reported (required)
    ingested_at: datetime                # when the pipeline first saw the record
    source_url: str

    @model_validator(mode="after")
    def temporal_invariants(self):
        # Invariant 1: reject future-dated events
        if self.event_date and self.event_date > PIPELINE_TODAY:
            raise ValueError(
                f"event_date {self.event_date} is in the future "
                f"(pipeline today: {PIPELINE_TODAY})"
            )

        # Invariant 1 (continued): disclosure also cannot be future
        if self.disclosure_date > PIPELINE_TODAY:
            raise ValueError(
                f"disclosure_date {self.disclosure_date} is in the future "
                f"(pipeline today: {PIPELINE_TODAY})"
            )

        # Invariant 3: event_date <= disclosure_date when both present
        if self.event_date and self.event_date > self.disclosure_date:
            raise ValueError(
                f"event_date {self.event_date} is after disclosure_date "
                f"{self.disclosure_date} — possible year-fallback bug"
            )

        return self
```

## Year extraction with min-year-fallback (Invariant 2)

When extracting a year from free text:

```python
import re
from datetime import date

YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")

def extract_event_year(
    article_text: str,
    disclosure_date: date,
    min_plausible_year: int = 1970,
) -> int | None:
    """
    Extract the most likely event year from article text.

    Heuristic: among all year mentions, return the MIN that is:
      - >= min_plausible_year
      - <= disclosure_year (events cannot be disclosed before they happen)

    If no candidate qualifies, return None and let the row go to manual review.
    """
    candidates = [
        int(m.group()) for m in YEAR_RE.finditer(article_text)
        if min_plausible_year <= int(m.group()) <= disclosure_date.year
    ]
    return min(candidates) if candidates else None
```

The asymmetric heuristic — MIN year that is `<= disclosure_year` — is the key fix versus the broken MAX-year heuristic. Pair with Invariant 1 + 3 in the validator for defense in depth.

## CI determinism

In the pipeline config:

```yaml
# .github/workflows/ingest.yml
env:
  PIPELINE_TODAY: ${{ github.event.head_commit.timestamp || '2026-05-23' }}
```

Or for local runs:

```bash
PIPELINE_TODAY=2026-05-23 uv run python -m pipeline.ingest
```

The point: every call to validation uses the SAME `today` boundary. Calling `date.today()` inside the validator is the bug pattern.
