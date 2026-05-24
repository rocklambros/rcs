# Comms templates

Factual-only message structures. No speculation, no premature attribution, no
customer-blame. Each message has the same skeleton: what is known, what is being
investigated, who is doing what, when the next update lands.

## Internal — first notification

```
Subject: [IR-Active] Investigation underway — [triggering-signal-short-name]

What is known:
- At [ISO-time], [triggering-signal] fired on [affected-identity] in [account/project/subscription].
- IR rotation paged at [ISO-time]; on-call: [name + handle].
- Evidence preserved at [storage-path].
- Containment status: [contained / in-progress / awaiting-sign-off].

What is being investigated:
- Whether the source IP / activity is a false positive (known-good source: [list]).
- Blast radius: what the identity could touch + what it actually touched.
- Whether any data classes were accessed.

Who is doing what:
- IR lead: [name]
- Service owner: [name]
- Security advisor: [name]

Next update: [ISO-time] (or sooner if material change).

Do NOT discuss outside the IR channel. Do NOT post to external chat / social.
```

## Internal — containment update

```
Subject: [IR-Active] Containment complete — [triggering-signal-short-name]

Update:
- Affected identity disabled at [ISO-time]. Active sessions revoked.
- Evidence preserved (CloudTrail / Audit / Activity Logs, IAM snapshots, flow logs) at [path]. Hashes recorded.
- Blast radius (preliminary):
  - Could touch: [scope summary]
  - Did touch: [count + classes of resources accessed]
  - Data classes crossed: [PII / PHI / PCI / none observed]

Still being investigated:
- Whether the identity created additional access paths (keys, policies, persistence) — eradication review in progress.
- Whether dependent secrets need rotation.

Next update: [ISO-time].
```

## Internal — eradication / recovery

```
Subject: [IR-Recovery] Eradication complete, recovery in progress

Eradication:
- [count] additional access paths reviewed; [count] reverted, [count] verified-benign.
- Dependent secret rotation: [N rotated, M scheduled].

Recovery:
- Affected resources restored from clean state at [ISO-time].
- Identity re-enabled with reduced scope at [ISO-time] (dual sign-off: [IR lead] + [service owner]).
- TTP monitoring active for [N] days.

Lessons-learned doc owner: [name]. Draft due [ISO-date].
```

## Customer — initial notification (when data class crossed)

```
Subject: Security incident notification — [account / customer-id]

Dear [customer contact],

We are writing to inform you of a security incident affecting [scope] that may have
involved [data class] associated with your account.

What happened:
- On [date], we detected [factual description, no speculation about actor].
- We have completed containment as of [date] and are conducting a detailed
  investigation.

What information may have been affected:
- [factual data-class enumeration; do NOT speculate about specific records until
  the blast-radius assessment is complete]

What we are doing:
- We have preserved logs and are conducting a forensic review.
- We have engaged [legal / DPO / external counsel as applicable].
- We will provide an update no later than [ISO-date].

What you can do:
- [Concrete steps: rotate any shared credentials, enable additional logging,
  contact us via [channel] with questions]

We sincerely regret any inconvenience this may cause. For questions, please contact
[customer-success contact] at [secure channel].

Sincerely,
[Authorizing role — typically CISO or VP Security]
```

## Regulator — when required by jurisdiction

Drafted by counsel / DPO. The IR rotation provides factual content; the legal
team handles jurisdiction-specific notification (GDPR 72h, HIPAA breach
notification, state-level notification laws, sector-specific regulators).

Factual content the IR rotation provides:

- Incident detection timestamp and method
- Scope: data classes, record counts (estimates with bounds, not point estimates)
- Containment timestamp and method
- Affected geographies (driving which regulators apply)
- Status of investigation
- Mitigation steps taken and planned

Do NOT include speculative attribution, internal commentary, or any non-public
information beyond what counsel requires.

## What NOT to write

- "We believe APT-X is behind this." — premature attribution. Wait for forensic confirmation.
- "The partner's compromised systems caused this." — blame-shift. Stick to your-scope facts.
- "There is no risk to customer data." — promise you cannot keep before blast-radius is complete.
- "This was caused by [employee name]'s mistake." — personnel detail. Keep messages to
  process-level facts.
- "We don't know what happened." — even early, you know what fired and what you did.
  Say that.
