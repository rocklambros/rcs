# Pre-trust audit verdict table template

| Check | Verdict | Evidence | Notes |
|---|---|---|---|
| 1. License | Pass / Warn / Fail | <file path or commit ref> | |
| 2. Source review | Pass / Warn / Fail | <commits inspected, lines reviewed> | |
| 3. Network egress | Pass / Warn / Fail | <endpoints found in source> | |
| 4. Version pin | Pass / Warn / Fail | <install command> | |
| 5. Secret handling | Pass / Warn / Fail | <how secrets flow through the code> | |
| 6. Tool subset | Pass / Warn / Fail | <tools exposed; least-privilege check> | |

Final verdict: **integrate** / **integrate-with-constraints** / **reject**
