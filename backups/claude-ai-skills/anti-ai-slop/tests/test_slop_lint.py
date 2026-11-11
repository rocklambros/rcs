"""Tests for slop_lint. Version 1.2.0, owner Rock Lambros.

Run from the skill folder: python3 -m pytest -q tests
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# The tests live in tests/ and the linter in scripts/, per the skill layout in
# the harness-engineering repo. Put scripts/ on the path before the import.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import slop_lint as lint  # noqa: E402


def rules(
    text: str, severity: str, profile: str = "blog", include_quotes: bool = False
) -> set[str]:
    found = lint.lint(text, profile=profile, include_quotes=include_quotes)
    return {f.rule for f in found if f.severity == severity}


@pytest.mark.parametrize(
    ("text", "rule"),
    [
        ("The patch is the disclosure \u2014 and the clock starts.", "H-DASH"),
        ("We shipped it - then we regretted it.", "H-DASH-SUB"),
        ("The patch shipped; the exploit followed.", "H-SEMI"),
        ("We delve into the threat landscape here.", "H-VOCAB"),
        ("This will enhance your security posture.", "H-VOCAB"),
        ("It's not a tool, it's a teammate.", "H-ANTITHESIS"),
        ("This is not just a patch.", "H-ANTITHESIS"),
        ("Not the price. Not the features. The trust.", "H-ANTITHESIS"),
        ("We patched it. However, the exploit still worked.", "H-CONNECTOR"),
        ("Here's the thing about agents.", "H-THROAT"),
        ("Great question about agents.", "H-CHATBOT"),
        ("See the report [INSERT SOURCE] for detail.", "H-FINGERPRINT"),
        ("Experts say the risk is growing.", "H-ATTRIBUTION"),
        ("Several sources indicate the risk is growing.", "H-ATTRIBUTION"),
        ("This could potentially change the market.", "H-HEDGE-STACK"),
        ("That is what keeps CISOs up at night.", "H-DREAD"),
        ("It encrypts data at rest, highlighting its value.", "H-ING-TAIL"),
        ("The breach stands as a reminder.", "H-SIGNIFICANCE"),
        ("Despite these challenges, the team shipped.", "H-CONCESSIVE"),
        ("It's like having a second analyst.", "H-PROMO"),
    ],
)
def test_hard_rules_fire(text: str, rule: str) -> None:
    assert rule in rules(text, lint.HARD)


@pytest.mark.parametrize(
    "text",
    [
        # Terms of art the owner needs. None of these may hard fail.
        "Article 14 requires human oversight of high risk systems.",
        "Rotate the API key and review key management.",
        "The Kerberos realm trusts the forest.",
        "He served as CISO for six years.",
        "Adversarial robustness testing ran for a week.",
        "NIST SP 800-172 lists enhanced security requirements.",
        "The crosswalk shows where CSF aligned with ISO 27001.",
        "The analyst finished unpacking the malware sample.",
        "A cross-functional team owns enablement.",
        "So we moved the control to the gateway.",
        "Retention runs 10\u201320 days.",
    ],
)
def test_terms_of_art_do_not_hard_fail(text: str) -> None:
    assert rules(text, lint.HARD) == set()


def test_quoted_and_code_material_is_skipped_by_default() -> None:
    text = 'He wrote "we delve; we leverage" in the memo.\n\n`a; b`\n\n> delve; tapestry\n'
    assert rules(text, lint.HARD) == set()
    assert "H-SEMI" in rules(text, lint.HARD, include_quotes=True)


def test_open_ask_is_reported_and_never_fails() -> None:
    found = lint.lint("The outage hit [ROCK: which vendor and what month?] hard.")
    assert [f.severity for f in found] == [lint.OPEN_ASK]


def test_list_separator_dash_is_typography() -> None:
    assert rules("- **Term** \u2014 description here\n", lint.HARD) == set()


def test_reversed_antithesis_and_paragraph_closer_are_advisory() -> None:
    text = (
        "The agent tries every path at once, which a human tester never does. "
        "You learn about the gap on the attacker's schedule instead of yours."
    )
    assert "A-ANTITHESIS-REVERSED" in rules(text, lint.ADVISORY)
    assert rules(text, lint.HARD) == set()


def test_fragment_run_is_advisory() -> None:
    text = (
        "Shipping a patch does half the attacker's work today. No source needed. Dead on arrival."
    )
    assert "A-FRAGMENT-RUN" in rules(text, lint.ADVISORY)


def test_technical_profile_passes_technical_terms() -> None:
    text = "The parser is robust against malformed input."
    assert "H-VOCAB" in rules(text, lint.HARD)
    assert rules(text, lint.HARD, profile="technical") == set()


def test_casual_profile_keeps_only_fingerprints() -> None:
    assert rules("We delve; we leverage.", lint.HARD, profile="casual") == set()
    assert "H-CHATBOT" in rules("I hope this helps!", lint.HARD, profile="casual")


def test_exit_codes_and_kill_switch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text("The patch shipped; the exploit followed.", encoding="utf-8")
    clean = tmp_path / "clean.md"
    clean.write_text("The patch shipped and the exploit followed.", encoding="utf-8")
    assert lint.main([str(draft)]) == 1
    assert lint.main([str(clean)]) == 0
    assert lint.main([str(draft), "--advisory-only"]) == 0
    assert lint.main([str(tmp_path / "missing.md")]) == lint.EXIT_USAGE
    monkeypatch.setenv(lint.DISABLE_ENV, "1")
    assert lint.main([str(draft)]) == 0


def test_internal_error_is_not_mistaken_for_a_failing_draft(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text("A clean sentence.", encoding="utf-8")

    def boom(*_args: object, **_kwargs: object) -> list[lint.Finding]:
        raise RuntimeError("simulated")

    monkeypatch.setattr(lint, "lint", boom)
    assert lint.main([str(draft)]) == lint.EXIT_INTERNAL


def test_email_profile_allows_goodwill_marks_and_reaction_runs() -> None:
    text = "Got it. Thanks! Looking forward to it! \U0001f60a"
    assert rules(text, lint.ADVISORY, profile="email") == set()
    assert "A-EXCLAIM" in rules(text, lint.ADVISORY)
    assert "H-SEMI" in rules("It shipped; it broke.", lint.HARD, profile="email")


def test_smooth_draft_is_flagged_against_rocks_cadence() -> None:
    sentence = (
        "The committee reviewed the proposal in detail and decided that the rollout "
        "should wait until the external audit team finishes its review."
    )
    found = lint.lint(" ".join([sentence] * 12))
    smooth = [f.span for f in found if f.rule == "A-SMOOTH"]
    assert any("average sentence" in span for span in smooth)
    assert any("five words or fewer" in span for span in smooth)
    assert "A-LONG-PARAGRAPH" in {f.rule for f in found}


def test_contrast_budget_fires_above_rocks_rate() -> None:
    text = (
        "It is a process, not a product. Buy time rather than tools. Hire people instead of logos."
    )
    assert "A-CONTRAST-BUDGET" in rules(text, lint.ADVISORY)
    assert "A-CONTRAST-BUDGET" not in rules("It is a process, not a product.", lint.ADVISORY)


def test_finds_you_well_opener_is_hard() -> None:
    assert "H-THROAT" in rules("I hope this email finds you well.", lint.HARD, profile="email")


def test_curly_apostrophes_match_the_same_rules() -> None:
    assert "H-THROAT" in rules("Let\u2019s dive in to a couple of case studies.", lint.HARD)
    assert "H-ANTITHESIS" in rules("It\u2019s not a tool, it\u2019s a teammate.", lint.HARD)


def test_formal_profile_accepts_book_register_paragraphs() -> None:
    sentence = (
        "The committee reviewed the proposal in detail and decided that the rollout "
        "should wait until the external audit team finishes its review."
    )
    paragraph = " ".join([sentence] * 6)
    text = f"{paragraph}\n\n{paragraph}"
    assert {"A-SMOOTH", "A-LONG-PARAGRAPH"} <= rules(text, lint.ADVISORY)
    assert not {"A-SMOOTH", "A-LONG-PARAGRAPH"} & rules(text, lint.ADVISORY, profile="formal")
    assert "H-SEMI" in rules("It shipped; it broke.", lint.HARD, profile="formal")


def test_social_profile_allows_two_exclamation_points() -> None:
    text = "Great start for a Monday! Say hi to the team at the conference this week!"
    assert "A-EXCLAIM" not in rules(text, lint.ADVISORY, profile="social")
    assert "A-EXCLAIM" in rules(text, lint.ADVISORY)
    assert "A-EXCLAIM" in rules(text + " Happy Monday!", lint.ADVISORY, profile="social")


def test_fingerprint_rule_ignores_the_word_cites() -> None:
    assert "H-FINGERPRINT" not in rules("Where a seed cites another source, follow it.", lint.HARD)
    assert "H-FINGERPRINT" in rules("as shown citeturn0search1 here", lint.HARD)


def test_unknown_profile_is_rejected() -> None:
    with pytest.raises(ValueError, match="unknown profile"):
        lint.lint("text", profile="nope")


# Closer checks added in slop_lint 1.4.0 (2026-10-09).
FLAGGED_SLACK = (
    # Names replaced with placeholders for the public backup repo. The
    # sentence shapes are the 2026-10-09 register entry's.
    "Heads up: Sam asked me to connect him with Alex for the Field CISO, "
    "Executive Access role in the operating model. His Fortune 500 CISO "
    "network is the EA fit. Wanted you to hear it from me before the intro "
    "goes out. Flag anything I should know first."
)
FIXED_SLACK = (
    "Heads up: Sam asked me to connect him w/ Alex for the Field "
    "CISO EA role in the operating model. Alex was a senior security "
    "advisor at two large vendors and works closely w/ Fortune 500 CISOs, "
    "which is the access the EA role needs. "
    "I'm going to make the intro."
)
BODY = "The renewal moved to March because legal needs the new DPA first. "


def test_flagged_slack_draft_trips_both_closer_rules() -> None:
    assert "H-CLOSER-MOTIVE" in rules(FLAGGED_SLACK, lint.HARD, profile="email")
    assert "A-CLOSER-GATE" in rules(FLAGGED_SLACK, lint.ADVISORY, profile="email")


def test_fixed_slack_draft_is_clean() -> None:
    found = {f.rule for f in lint.lint(FIXED_SLACK, profile="email")}
    assert not {"H-CLOSER-MOTIVE", "A-CLOSER-GATE"} & found


@pytest.mark.parametrize(
    "closer",
    [
        # Rock's measured closers from references/voice-guide.md.
        "Looking forward to it.",
        "Let me know if you need anything.",
        "Happy to hop on a call.",
        "I'll let you two take it from here.",
    ],
)
def test_rocks_own_closers_pass(closer: str) -> None:
    found = {f.rule for f in lint.lint(BODY + closer, profile="email")}
    assert not {"H-CLOSER-MOTIVE", "A-CLOSER-GATE"} & found


@pytest.mark.parametrize(
    "closer",
    [
        "Didn't want this to catch you off guard.",
        "Figured you'd want to know.",
        "Just wanted to loop you in.",
        "Wanted you to hear it from me first.",
    ],
)
def test_motive_closers_fail(closer: str) -> None:
    assert "H-CLOSER-MOTIVE" in rules(BODY + closer, lint.HARD, profile="email")


def test_motive_phrase_carrying_a_fact_passes() -> None:
    text = BODY + ("Wanted to give you a heads up that I'm starting the internal testing today.")
    assert "H-CLOSER-MOTIVE" not in rules(text, lint.HARD, profile="email")


def test_motive_opener_early_in_message_passes() -> None:
    text = (
        "I just wanted you to know I haven't forgotten about the renewal update. "
        "Jordan spoke to their CFO last week. We meet again on Friday."
    )
    assert "H-CLOSER-MOTIVE" not in rules(text, lint.HARD, profile="email")


def test_sign_off_does_not_hide_the_closer() -> None:
    for tail in ("\n\nThanks,\n-Rock", "\nThanks,\n-Rock", "\n\n-Rock"):
        text = BODY + "Wanted you to hear it from me first." + tail
        assert "H-CLOSER-MOTIVE" in rules(text, lint.HARD, profile="email"), tail


def test_quoted_closer_is_ignored_by_default() -> None:
    text = BODY + 'I cut "Wanted you to hear it from me first." from the draft.'
    assert "H-CLOSER-MOTIVE" not in rules(text, lint.HARD, profile="email")


def test_gate_closer_is_advisory_only() -> None:
    text = BODY + "Let me know if you have any concerns before I send it."
    assert "A-CLOSER-GATE" in rules(text, lint.ADVISORY, profile="email")
    assert not rules(text, lint.HARD, profile="email")


def test_casual_profile_skips_closer_checks() -> None:
    assert "H-CLOSER-MOTIVE" not in rules(FLAGGED_SLACK, lint.HARD, profile="casual")


def test_sign_off_only_message_returns_no_closer_findings() -> None:
    assert lint.check_closers("Thanks,\n-Rock") == []


# --- H-PRAISE-LABEL, added 2026-11-04 from the Voice Corrections Register ---


# Spans Rock flagged as praise labels, verbatim from the register entries of
# 2026-10-26 (Helen Oakley comment) and 2026-11-04 (Gadi Evron comment), plus
# phrases his own pastes carried that the /anti-ai-slop pass removed.
@pytest.mark.parametrize(
    "text",
    [
        "Taking ACH from seven hypotheses to thousands is the headline, and it deserves to be.",
        "Don't skip the math, though, because the math is the best part.",
        "Review currentness is the feature I'd show every AppSec team first.",
        "The question at the end of your blog is the one I'm stealing.",
        "I'm stealing this for every agent control review.",
        "Anyone running Claude Code should go kick the tires on this.",
        "This deserves way more eyes than it's getting.",
        "The smartest thing in Gadi Evron's new paper is the field he refused to build.",
        "She's done it with unparalleled clarity.",
        "This is a must-read!",
        "Today we're releasing CxBOM, and I couldn't be prouder of it.",
    ],
)
def test_praise_label_fires(text: str) -> None:
    assert "H-PRAISE-LABEL" in rules(text, lint.HARD, profile="social")


@pytest.mark.parametrize(
    "text",
    [
        # Literal uses that must keep passing.
        "The user deserves to be notified before the agent acts.",
        "Every incident deserves a postmortem.",
        "The best part of the attack chain to break is the help-desk call.",
        "Patching is the best thing you can do this week.",
        "I'm stealing time from the roadmap to fix the pipeline.",
        "The headline number was 3,000 indicators.",
        "Read the paper this weekend.",
    ],
)
def test_praise_label_spares_literal_uses(text: str) -> None:
    assert "H-PRAISE-LABEL" not in rules(text, lint.HARD, profile="social")


def test_praise_label_ignores_quoted_spans_by_default() -> None:
    text = 'Rock cut "is the headline, and it deserves to be." from the draft.'
    assert "H-PRAISE-LABEL" not in rules(text, lint.HARD, profile="social")


def test_shipped_gadi_comment_stays_clean() -> None:
    shipped = (
        "Don't skip the weighting math in this one.\n\n"
        "Every piece of a brain carries a weight, the negative log of how often it "
        "shows up in YOUR traffic.\n\n"
        "Gadi, is Share or disproof next on the build list?\n"
    )
    assert "H-PRAISE-LABEL" not in rules(shipped, lint.HARD, profile="social")


# --- slop_lint 1.6.0: register audit of 2026-11-06 ---------------------------
# Fixtures keep the shape of each register span and drop client and colleague
# names, because the harness-engineering repo that backs this skill up is
# public. Each comment names the register entry the span comes from.


@pytest.mark.parametrize(
    ("text", "rule", "profile"),
    [
        # 2026-11-05 slack
        ("Details and a short follow-up list are on the PR.", "H-POINTER", "email"),
        # 2026-10-06 slack
        ("Two sentences you can use as they stand.", "H-DELIVERABLE-LABEL", "email"),
        # 2026-10-29 slack
        ("If you're good w/ the shape, I'll draft the README.", "H-DELIVERABLE-LABEL", "email"),
        # 2026-10-31 email
        ("Each one comes with a check folks can take home.", "H-DELIVERABLE-LABEL", "email"),
        ("I'll keep my employer and any product pitch out of all three.", "H-DISCLAIMER", "email"),
        ("Thanks for having me back, and I'm glad the tabletop landed.", "H-LANDED", "email"),
        # 2026-10-09 email and 2026-10-24 blog
        ("He's a dear friend, so I'm biased, but I'd back him.", "H-PERF-HEDGE", "email"),
        ("I'm the lead author, so discount my enthusiasm as you see fit.", "H-PERF-HEDGE", "blog"),
        # 2026-10-13 comment and 2026-10-23 post
        ("On your CFO question, put the reviewers in the budget.", "H-TOPIC-CLAUSE", "social"),
        ("On breaking in, I'm not budging.", "H-TOPIC-CLAUSE", "social"),
        # 2026-10-29 slack, 2026-10-22 comment, 2026-10-06 slack
        ("Issue #318 is the last thing I want your read on.", "H-POINTBACK", "email"),
        ("I'd underline one line from the essay that you flagged.", "H-POINTBACK", "social"),
        ("That word is the one I'd drop, because it isn't what I said.", "H-POINTBACK", "email"),
        # 2026-10-16 slack and post
        ("54 days left of the ninety, and they run out December 9.", "H-COUNTDOWN", "email"),
        (
            "Did your board approve an AI vulnerability scanner this year?",
            "H-BOARD-SPEND",
            "social",
        ),
        ("There are two ways this goes.", "H-THROAT", "email"),
        # 2026-10-14 post
        ("It makes you feel better and tells your board nothing.", "H-PAIRED-CONTRAST", "social"),
        # 2026-10-09 post
        (
            "Cap the session, starting here: nothing that reads secrets talks out.",
            "H-THROAT",
            "social",
        ),
        # 2026-11-02 and 2026-10-30 pastes
        ("Interestingly, the filing never uses the word.", "H-CONNECTOR", "blog"),
        ("Crucially, she names the limits.", "H-CONNECTOR", "social"),
        ("She doesn't shy away from the limits of the evidence.", "H-PRAISE-LABEL", "social"),
        ("The vendor unveiled the feature at the conference.", "H-VOCAB", "social"),
        # 2026-10-13 comment
        (
            "Unharvested payroll is exactly the phrase that ends up in the deck.",
            "H-PRAISE-LABEL",
            "social",
        ),
        # 2026-10-09 meme
        ("I respect the honesty.", "H-PRAISE-LABEL", "social"),
        # coffee-peer-voice "Anchor in something real, by name"
        (
            "A recent study found most agents run with standing permissions.",
            "H-VAGUE-SOURCE",
            "social",
        ),
        ("A company I know got hit the same way.", "H-VAGUE-SOURCE", "email"),
    ],
)
def test_register_hard_rules_fire(text: str, rule: str, profile: str) -> None:
    assert rule in rules(text, lint.HARD, profile=profile)


@pytest.mark.parametrize(
    ("text", "profile"),
    [
        # Rock's own lines from the register and the voice guide. None may fail.
        ("On Tuesday I wrote that AI moved the bottleneck to the reviewers.", "social"),
        ("On prem, the customer hosts and processes its own data.", "email"),
        ("On average, the queue cleared in four days.", "blog"),
        ("Every commit landed on October 4 and 5.", "email"),
        ("The user deserves to be notified before the agent acts.", "social"),
        ("A recent study by Partnership on AI tested four agent systems.", "social"),
        ("The board approved the annual budget in March.", "formal"),
        ("Ship it, because what the hell could possibly go wrong???", "social"),
        ("Gadi, is Share or disproof next on the build list?", "social"),
        ("Let me know if you need anything.", "email"),
        ("Happy to hop on a call.", "email"),
        ("A next-generation firewall sits in front of the plant network.", "technical"),
    ],
)
def test_register_literal_uses_pass(text: str, profile: str) -> None:
    assert rules(text, lint.HARD, profile=profile) == set()


@pytest.mark.parametrize(
    ("text", "rule", "profile"),
    [
        ("Defense gives us until December 15 on items 2 and 3.", "A-XREF", "email"),
        ("In ACS, I imagine it would also function as runtime evidence.", "A-HEDGE-STACK", "email"),
        (
            "Helen, I spent the morning in your code, and the tests sold me.",
            "A-FIRSTPERSON-CLAIM",
            "social",
        ),
        ("The part I'm proudest of is the attack table.", "A-FIRSTPERSON-CLAIM", "blog"),
        ("On premises, the customer hosts its own data.", "A-ROCK-TERM", "email"),
        ("Sam, send him the same evidence by Friday.", "A-PEER-IMPERATIVE", "email"),
        ("I'd want to see more before I signed one.", "A-NO-OBJECT", "blog"),
        (
            "Run the first three against it: percent of what, under what condition, "
            "and compared to what.",
            "A-COLON-LIST",
            "blog",
        ),
        (
            "The deterministic enforcement you're calling for is already written down.",
            "A-STAGED-REVEAL",
            "social",
        ),
        (
            "Every time a marketplace gets poisoned, we buy another scanner.",
            "A-GENERALIZATION",
            "social",
        ),
        (
            "That read is dangerous because an agent is worse than a human insider.",
            "A-NOUN-LABEL",
            "social",
        ),
        ("Drop it silently and every rate is wrong.", "A-DO-X-AND-Y", "social"),
        (
            "Your logs blame the orchestrator, because that's whose badge it wore.",
            "A-CLICHE",
            "social",
        ),
    ],
)
def test_register_advisory_rules_fire(text: str, rule: str, profile: str) -> None:
    assert rule in rules(text, lint.ADVISORY, profile=profile)


def test_peer_imperative_skips_interjections() -> None:
    assert "A-PEER-IMPERATIVE" not in rules(
        "Thanks, send it over when ready.", lint.ADVISORY, profile="email"
    )


def test_engagement_bait_closer_is_hard_in_social_only() -> None:
    text = "We shipped the gate this week and it caught two bad tool calls. Thoughts?"
    assert "H-ENGAGEMENT-BAIT" in rules(text, lint.HARD, profile="social")
    assert "H-ENGAGEMENT-BAIT" not in rules(text, lint.HARD, profile="email")
    generic = (
        "We shipped the gate this week and it caught two bad tool calls. "
        "What's the greenest dashboard you ever presented right before something blew up?"
    )
    assert "A-CLOSING-QUESTION" in rules(generic, lint.ADVISORY, profile="social")


def test_three_asks_in_prose_want_a_list() -> None:
    text = (
        "Can you send the scan results? Could you confirm the owner for the bastion? "
        "Would you check whether the keys rotate every 7 days?"
    )
    assert "A-ASKS-UNLISTED" in rules(text, lint.ADVISORY, profile="email")
    listed = (
        "Three asks:\n\n1. Can you send the scan?\n"
        "2. Could you confirm the owner?\n3. Would you check the keys?\n"
    )
    assert "A-ASKS-UNLISTED" not in rules(listed, lint.ADVISORY, profile="email")


def test_acronym_needs_expansion_but_caps_emphasis_passes() -> None:
    assert "A-ACRONYM" in rules(
        "Can your IAM tell which sessions belong to an agent?", lint.ADVISORY, profile="social"
    )
    defined = "Can your identity and access management (IAM) system tell? IAM is the place to look."
    assert "A-ACRONYM" not in rules(defined, lint.ADVISORY, profile="social")
    assert "A-ACRONYM" not in rules(
        "Attribution is HARD and it is the LAST thing you worry about.",
        lint.ADVISORY,
        profile="social",
    )


def test_code_identifiers_flagged_in_social_only() -> None:
    text = "Helen, test_public_content.py fails the build if the docs say certified."
    assert "A-CODE-IN-SOCIAL" in rules(text, lint.ADVISORY, profile="social")
    assert "A-CODE-IN-SOCIAL" not in rules(text, lint.ADVISORY, profile="email")


def test_synonym_cycling_across_one_unit() -> None:
    text = (
        "Counted per attempt, the attacks worked 3.64% of the time. Each of the tries "
        "ran once. Those runs are the same data counted two ways."
    )
    assert "A-SYNONYM-CYCLE" in rules(text, lint.ADVISORY)


# --- slop_lint 1.6.0: SlopShape core-value proxies ---------------------------
# Written for these tests in the shape the paper describes (thesis and flow
# announced up front, legacy-versus-modern frame, institutional voice, a
# closing that restates the opening). Not copied from the paper or a post.
TIDY_AI_POST = (
    "In this post, we'll cover why vendor onboarding stalls, three fixes that "
    "work, and how to measure the difference. Vendor onboarding stalls because "
    "manual review queues slow every request.\n\n"
    "Paper checklists were built for a slower era. Traditional approaches rely on "
    "email threads and spreadsheets, and legacy workflows hide who owns each "
    "step. A modern, integrated workflow gives every request an owner and a clock.\n\n"
    "The first fix is a single intake form. The second fix is automated routing "
    "to the right reviewer. The third fix is a shared status page that every "
    "requester can see without asking anyone for an update.\n\n"
    "Measurement matters as much as the fixes themselves. Track the time from "
    "intake to approval for each request and compare it against the old process "
    "every week so the improvement stays visible to everyone involved.\n\n"
    "In short, vendor onboarding stalls because manual review queues slow every "
    "request, and the three fixes remove the stall."
)


def test_tidy_ai_post_trips_the_shape_rules() -> None:
    found = {f.rule for f in lint.lint(TIDY_AI_POST, profile="blog")}
    assert {"H-SHAPE-ROADMAP", "H-SHAPE-RECAP", "H-SHAPE-ERA"} <= found
    assert {"A-SHAPE-LEGACY", "A-SHAPE-RESTATE", "A-SHAPE-NODATE", "A-SHAPE-NOROUTE"} <= found
    assert "A-SHAPE-MODAL" in found


# Rock's published LinkedIn posts from before AI assistance existed (2019 and
# 2021, public posts, quoted from references/voice-samples.md). They set the
# floor: no 1.6.0 rule may hard fail his own pre-AI writing.
ROCK_2019 = (
    "The URGENT/11 vulnerability announced by Armis last week is probably the "
    "biggest news of the week that nobody knows about. 6 of the 11 enable RCE. "
    "Most owner/operators don't even know VxWorks exists on their networks as "
    "those devices are embedded in systems provided by larger manufacturers, such "
    "as Siemens and Rockwell. Game on, ICS vendors, to get your products patched. "
    "Game on, owner/operators to actually apply the patches."
)
ROCK_2021 = (
    "A lot of people are asking me about the Colonial Pipeline attack. News media "
    "is reporting that the ransomware did not impact OT systems, and that certain "
    "OT systems were taken offline as a precaution. There is a lot of speculation "
    "regarding attribution going around in the media, but I caution you that "
    "attribution is HARD and it's important that we we let the smart people gather "
    "all the facts."
)


@pytest.mark.parametrize("text", [ROCK_2019, ROCK_2021])
def test_rocks_pre_ai_posts_stay_hard_clean(text: str) -> None:
    assert rules(text, lint.HARD, profile="social") == set()
    shape = {f.rule for f in lint.lint(text, profile="social") if f.rule.startswith("A-SHAPE")}
    assert shape == set()


# --- slop_lint 1.6.0: burstiness and paragraph skeletons ---------------------
# 2026-10-29 course answers: every paragraph three to four sentences of 16 to
# 25 words, same skeleton per answer, and A-UNIFORM stayed silent.
UNIFORM_ANSWER = "\n\n".join(
    [
        "A broadcast join ships a full copy of the smaller table to every executor "
        "in the cluster. The large table stays partitioned where it already sits on "
        "disk. Spark avoids the shuffle that a sort merge join would otherwise need "
        "here.",
        "A sort merge join shuffles both tables by the join key before it starts "
        "matching rows. Each executor then sorts its partitions and walks them in "
        "order. The approach scales well when both tables are far too large to "
        "broadcast.",
        "The optimizer picks a broadcast join when the smaller side falls under the "
        "configured threshold. You can raise that threshold when executors have "
        "memory to spare. Raising it too far risks out of memory errors on every "
        "executor.",
        "Skewed keys hurt both strategies in different ways during large production "
        "jobs. A broadcast join tolerates skew on the large side without much "
        "trouble. A sort merge join needs salting or adaptive execution to stay "
        "balanced.",
    ]
)


def test_uniform_course_answers_trip_burstiness_and_skeleton() -> None:
    found = rules(UNIFORM_ANSWER, lint.ADVISORY, profile="formal")
    assert {"A-BURSTINESS", "A-PARA-UNIFORM"} <= found


def test_rocks_varied_cadence_passes_burstiness() -> None:
    text = (
        "I ran a SOC. The queue beat the hell out of headcount every single time. "
        "Analysts will just close what they can't investigate. They are burned out "
        "and fatigued and even w/ an agentic SOC, I haven't seen a fully autonomous "
        "one yet. Nor would I want to. Inventory your agents. This is no different "
        "than inventorying your hardware and software, and we've been doing that for "
        "decades! Go ahead... I'll wait."
    )
    assert "A-BURSTINESS" not in rules(text, lint.ADVISORY, profile="social")


def test_cleft_with_past_tense_verb_is_advisory() -> None:
    # Register 2026-10-23: "What decided this week was dumber."
    assert "A-CLEFT" in rules("What decided this week was dumber.", lint.ADVISORY, profile="social")
    assert "A-CLEFT" not in rules("I asked him what happened.", lint.ADVISORY, profile="social")


# --- slop_lint 1.7.0: agreement template and ranking verdicts, 2026-11-10 ---
# Fire cases are verbatim openers from LinkedIn Comment Brief and X Reply
# Brief options drafted November 7 to 10, 2026. Pass cases are Rock's own
# published reply openers from the same week and his pre-AI voice samples.


@pytest.mark.parametrize(
    "text",
    [
        "Agreed on the hygiene, and your runtime question is the one I'd put first.",
        "Excessive agency is the one I'd move to the top.",
        "Number 7 is the one I'd hand to procurement.",
        "The Mt. Moon fix is the part I'd show a security team.",
        "The fresh-session repro check is the part I'd keep.",
        "The cost gap is the bigger story.",
        "That’s the question I’d ask first.",
    ],
)
def test_rank_pick_fires(text: str) -> None:
    assert "H-RANK-PICK" in rules(text, lint.HARD, profile="social")


@pytest.mark.parametrize(
    "text",
    [
        "The one I'd trust is the signed build.",
        "That word is the one I'd be careful with.",  # H-POINTBACK owns this one
        "Patching is the one control that works when nothing else does.",
        "I'd move excessive agency to the top of the list.",
        "The cost gap is the story Vals measured: $2 to $3 against $17 to $46.",
    ],
)
def test_rank_pick_passes(text: str) -> None:
    assert "H-RANK-PICK" not in rules(text, lint.HARD, profile="social")


@pytest.mark.parametrize(
    "text",
    [
        "Agreed on the hygiene. Permissions say nothing about runtime.",
        "Agreed, and the Astra case is worse.",
        "Agreed that every agent action can't wait for a person.",
        "A (recommended): Agreed, the AI SOC pile-up is real.",
        "Fair point. Agreed, and the patch backs you up.",
    ],
)
def test_agree_ramp_fires(text: str) -> None:
    assert "H-AGREE-RAMP" in rules(text, lint.HARD, profile="social")


@pytest.mark.parametrize(
    "text",
    [
        "Agreed. The managed instructions shaped what the agent asked for.",
        "I agree with Dutch Schwartz wholeheartedly that the next CISO is a business executive first.",
        "100%. The camera now becomes an input channel.",
        "Yes! 100% Yes! Basics still apply.",
        "Yep... just because people think AI is black magic doesn't mean the oldies go away.",
        "The board agreed, and the budget moved.",
    ],
)
def test_agree_ramp_passes(text: str) -> None:
    assert "H-AGREE-RAMP" not in rules(text, lint.HARD, profile="social")


BATCH = (
    "A (recommended): Agreed. The managed instructions shaped what the agent asked for.\n"
    "\n"
    "B: Yep, and the alert still has to sit outside the agent's write scope.\n"
    "\n"
    "C: Which of the 15 would you fund first out of the SOC line?\n"
    "\n"
    "R02: 100%. Recovery runs from the same tool, so the agent can turn it off.\n"
)


def test_second_agreement_opener_in_batch_is_hard() -> None:
    found = [f for f in lint.lint(BATCH, profile="social") if f.rule == "H-AGREE-REPEAT"]
    assert len(found) == 2


def test_one_agreement_opener_in_batch_passes() -> None:
    text = BATCH.split("\n\nR02")[0].replace("B: Yep, and", "B: The")
    assert "H-AGREE-REPEAT" not in rules(text, lint.HARD, profile="social")


def test_agreement_repeat_is_social_only() -> None:
    assert "H-AGREE-REPEAT" not in rules(BATCH, lint.HARD, profile="email")
