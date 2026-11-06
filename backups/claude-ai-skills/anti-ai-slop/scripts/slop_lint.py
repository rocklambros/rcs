#!/usr/bin/env python3
"""slop_lint: deterministic check for the mechanical AI writing tells.

Version: 1.6.0
Owner: Rock Lambros
Home: anti-ai-slop/scripts/slop_lint.py
Rules sourced from: anti-ai-slop v1.2, v1.6, v1.8, and v1.9, coffee-peer-voice
v1.7, v1.14, and v1.17, the Voice Corrections Register (H-PRAISE-LABEL,
2026-11-04, and the full register audit of 2026-11-06), the SlopShape paper
(Madler, arXiv:2609.15369v3, release package github.com/pulse-energy-eu/
slopshape at commit fae4c38), and the "Writing Rules: How to Avoid
AI-Generated Patterns" doc reviewed 2026-09-20

What 1.6.0 adds, and where each piece comes from.
    Register rules  Every register pattern that a regex can see and that 1.5.0
                    had no rule for. Each rule's comment names its entry date.
                    Patterns the register records as judgment calls (stance,
                    audience, invented facts, wrong names) stay out, because a
                    regex that tried would fire on Rock's own sentences.
    Shape rules     Proxies for the ten "core values" SlopShape found carry
                    25.6% of a structural classifier's attribution and alone
                    detect AI blog posts at 90.1 macro-F1. The paper measured
                    them with an LLM judge over 13,500 posts. These regexes
                    are approximations of that judge, written for this owner,
                    and they are not validated against the paper's labels
                    (the per-document answers are gated). Each finding's
                    message carries the paper's human-AI gap so the reader
                    can weigh it.
    Cadence rules   A-BURSTINESS (sentence-length coefficient of variation)
                    and A-PARA-UNIFORM, calibrated on Rock's voice samples
                    (sentence-length CV 0.34 to 0.68, pooled 0.59) after the
                    2026-10-29 course-answer entry, where every sentence ran
                    16 to 25 words and A-UNIFORM stayed silent.

Deliberately NOT imported from that doc, because each would hurt the owner:
    human oversight    Term of art. EU AI Act Article 14 carries that title.
    cross-functional,  Working terms in proposals and org design.
    enablement
    meanwhile          Ordinary word. Too many false positives to flag.
    "vary vocabulary"  Contradicts the synonym cycling rule in anti-ai-slop.
    semicolons as the  The owner's standing rule bans semicolons.
    em dash fix

Why this exists. Both skills hold their rules in prompt text, and the model
that wrote a draft is also the only thing checking it. This script is the one
check that does not depend on the model's judgment. It returns quoted spans
with rule ids. It never rewrites text and it never produces a score (see the
third maintainer note in coffee-peer-voice: scores drove an over scrub loop).

Severity model.
    HARD      Binary tells with no honest use in security and governance
              writing. Any HARD finding sets exit code 1.
    ADVISORY  Patterns that need a reader. Never affects the exit code.
    OPEN_ASK  [ROCK: ...] tokens the drafter left for the owner. Listed so
              they are not lost. Never a failure.

Exit codes: 0 no HARD findings, 1 HARD findings present, 2 usage or IO error,
3 internal error. A crash must never look like a failing draft, so callers
treat 2 and 3 as "the check did not run" and fall back to a manual audit.

Requires Python 3.9 or later. macOS developer tools have shipped 3.9, so the
script avoids every 3.10 only construct and the tests run on both.

Kill switch. Set SLOP_LINT_DISABLE=1 to make the script a no-op that exits 0,
or pass --advisory-only to keep the report and force exit 0. Use either when
a rule misfires and you need drafts to flow while the rule gets fixed.

Security. Standard library only. Reads one file or stdin, writes to stdout.
No network, no eval, no file writes. Every quantifier over arbitrary text is
bounded and input is capped at MAX_BYTES, so a hostile draft cannot cause
catastrophic regex backtracking.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections.abc import Callable, Iterator
from dataclasses import asdict, dataclass
from typing import Final

VERSION: Final = "1.6.0"
OWNER: Final = "Rock Lambros"
MAX_BYTES: Final = 2_000_000
DISABLE_ENV: Final = "SLOP_LINT_DISABLE"
EXIT_USAGE: Final = 2
EXIT_INTERNAL: Final = 3

HARD: Final = "HARD"
ADVISORY: Final = "ADVISORY"
OPEN_ASK: Final = "OPEN_ASK"

PROFILES: Final = ("blog", "technical", "social", "email", "formal", "casual")

# A run of this many consecutive short sentences reads as a fragment stack.
# Six words, because coffee-peer-voice allows a lone short imperative
# ("Bring your patch SLA.") and only the run is the tell.
SHORT_SENTENCE_WORDS: Final = 6
SHORT_CLOSER_WORDS: Final = 8
UNIFORM_MIN_SENTENCES: Final = 8
TIER3_DENSITY: Final = 0.03
HASHTAG_LIMIT: Final = 6
CONTEXT_CHARS: Final = 40
# Two of anything is the smallest repeat: two bold bullets, two Tier 2 words
# in a paragraph, two short sentences in a row, two exclamation points.
MIN_REPEAT: Final = 2
TOPIC_LABEL_WORDS: Final = 4
# anti-ai-slop calls 15 to 25 words the uniform band.
UNIFORM_BAND: Final = range(15, 26)

# Calibration from Rock's own typing: 2,971 hand typed emails, 132,592 words,
# measured 2026-09-21. His sentences average 12 words with a median of 10,
# about 27% run five words or fewer, the median paragraph is one sentence,
# and the reversed contrast forms together run about 1.1 per 1,000 words.
# The checks below flag a draft that reads smoother than he writes.
SMOOTH_MEAN_WORDS: Final = 16
SMOOTH_MIN_SENTENCES: Final = 8
SHORT_SHARE_FLOOR: Final = 0.10
SHORT_SHARE_MIN_SENTENCES: Final = 12
REACTION_WORDS: Final = 5
LONG_PARAGRAPH_SENTENCES: Final = 5
CONTRAST_PER_1K: Final = 2.0
# Email and chat carry goodwill exclamation points ("Thanks!", "Looking
# forward to it!") at about 10 per 1,000 words in his short replies, and his
# replies stack reaction sentences ("Got it. Thanks!"), so both thresholds
# loosen in the email profile only.
EMAIL_EXCLAIM_LIMIT: Final = 4
EMAIL_FRAGMENT_RUN: Final = 4
# Rock's 2021 book chapters (24,446 words of his own text) average 18 words
# per sentence and 4 sentences per paragraph, so the formal profile turns the
# smoothness check off and lets a paragraph reach six sentences.
FORMAL_LONG_PARAGRAPH: Final = 7
# Rock's own LinkedIn posts from before December 2022 (60 posts, 3,733 words)
# carry exclamation points at 12 per 1,000 words, and a fifth of them hold
# two or more, so the social profile flags at three instead of two.
SOCIAL_EXCLAIM_LIMIT: Final = 3
# Word and Outlook produce curly quotes. Rules are written with straight
# ones, so mask() maps curly to straight, one character for one character,
# which keeps every offset and line number intact.
CURLY_TO_STRAIGHT: Final = str.maketrans(
    {"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"'}
)

# --- 1.6.0 thresholds -------------------------------------------------------
# Sentence-length coefficient of variation (sd / mean). Rock's voice samples
# run 0.34 to 0.68 (pooled 0.59 over 61 sentences). A draft under 0.30 reads
# metronomic, the way the 2026-10-29 course answers did.
BURSTINESS_CV_FLOOR: Final = 0.30
BURSTINESS_MIN_SENTENCES: Final = 8
# Paragraph skeletons: four or more prose paragraphs whose sentence counts
# differ by at most one and never drop below three, or whose word counts
# barely vary, are the "same skeleton per answer" tell.
PARA_UNIFORM_MIN_PARAGRAPHS: Final = 4
PARA_UNIFORM_MIN_SENTENCES: Final = 3
PARA_UNIFORM_WORD_CV: Final = 0.20
# coffee-peer-voice: "past roughly 400 words the reader skims" (chat and
# mail). Rock's posts run 40 to 80 words, 110 at the 90th percentile, and his
# rants overrun the slot cap on purpose, so the social cap is generous.
EMAIL_WORD_CAP: Final = 400
SOCIAL_WORD_CAP: Final = 300
# Three or more separate asks in a message get a numbered list by default
# (register 2026-10-07, 2026-10-14, 2026-10-31, the third hit).
ASKS_FOR_LIST: Final = 3
# Shape checks need enough text to have a shape.
SHAPE_MIN_WORDS: Final = 150
RESTATE_MIN_PARAGRAPHS: Final = 3
RESTATE_JACCARD: Final = 0.25
RESTATE_MIN_SHARED: Final = 4
# The paper's "tidy, self-announcing" post is the co-occurrence of its
# AI-leaning core values. Three families in one draft is the modal shape.
MODAL_MIN_FAMILIES: Final = 3
# Human-AI gaps from SlopShape Table 6 (core_values_selection.json). Quoted
# in messages so a reader can weigh a proxy hit against the measured effect.
GAP_RESTATED_THESIS: Final = "0.650"
GAP_SUMMARY_STAGE: Final = "0.609"
GAP_NO_ROUTE: Final = "0.592"
GAP_LEGACY_MODERN: Final = "0.497"
GAP_THESIS_FIRST: Final = "0.419"
GAP_MODERN_FRAMING: Final = "0.360"
GAP_INSTITUTIONAL: Final = "0.347"
GAP_HISTORICAL_DATE: Final = "0.283"


@dataclass(frozen=True)
class Finding:
    """One flagged span. `line` is 1-based in the original input."""

    rule: str
    severity: str
    line: int
    span: str
    message: str


@dataclass(frozen=True)
class Rule:
    """A regex rule. `profiles` lists the profiles where the rule is active."""

    rule: str
    severity: str
    pattern: re.Pattern[str]
    message: str
    profiles: tuple[str, ...] = ("blog", "technical", "social", "email", "formal")


def _rx(pattern: str) -> re.Pattern[str]:
    return re.compile(pattern, re.IGNORECASE | re.MULTILINE)


def _words(*stems: str) -> re.Pattern[str]:
    return _rx(r"\b(?:" + "|".join(stems) + r")\b")


# ---------------------------------------------------------------------------
# Vocabulary. A word is HARD only when no literal use exists in security and
# governance writing. Words with a term-of-art sense stay ADVISORY so the fix
# loop never pushes the drafter to rewrite a correct term: Kerberos realm,
# malware unpacking, actionable intelligence, API key, served as CISO,
# adversarial robustness, the underscore character, NIST best practices.
# ---------------------------------------------------------------------------
TIER1_HARD: Final = _words(
    r"delv(?:e|es|ed|ing)",
    r"tapestr(?:y|ies)",
    r"testament",
    r"embark(?:s|ed|ing)?",
    r"utili[sz](?:e|es|ed|ing|ation)",
    r"seamless(?:ly)?",
    r"meticulous(?:ly)?",
    r"game[- ]chang(?:er|ers|ing)",
    r"cutting[- ]edge",
    r"watershed moments?",
    r"nestled",
    r"vibrant",
    r"thriving",
    r"showcas(?:e|es|ed|ing)",
    r"deep[- ]dives?",
    r"div(?:e|es|ing) into",
    r"ever[- ]evolving",
    r"daunting",
    r"holistic(?:ally)?",
    r"impactful",
    r"learnings",
    r"thought leaders?(?:hip)?",
    r"at its core",
    r"synerg(?:y|ies|istic)",
    r"in order to",
    r"due to the fact that",
    r"boast(?:s|ed|ing)?",
    r"commenc(?:e|es|ed|ing)",
    r"ascertain(?:s|ed|ing)?",
    r"endeavou?r(?:s|ed|ing)?",
    r"pivotal",
    r"intrica(?:te|tely|cy|cies)",
    r"landscapes?",
    r"underscor(?:es|ed|ing)",
    r"leverag(?:es|ed|ing)(?! buyout| loan| finance)",
    r"genuinely",
    r"truly",
    # From the 2026-09-20 doc review.
    r"vital",
    r"garner(?:s|ed|ing)?",
    r"reimagin(?:e|es|ed|ing)",
    r"profound(?:ly)?",
    r"groundbreaking",
    r"renowned",
    r"enduring",
    r"interplay",
    r"diverse array",
    r"outside the box",
    r"exemplif(?:y|ies|ied|ying)",
    # `enhanced` is ADVISORY: NIST SP 800-172 is titled Enhanced Security
    # Requirements, so the adjective has a literal use.
    r"enhanc(?:e|es|ing|ements?)",
    r"hustle and bustle",
    r"bridg(?:e|es|ed|ing) the gap",
    r"there(?:'s| is) no denying",
    # Register 2026-10-30: the /anti-ai-slop pass Rock asked for removed
    # "unveiled" from his paste, so it is not his voice. "Released" says it.
    r"unveil(?:s|ed|ing)?",
)

# Pass in the technical profile per the anti-ai-slop context profiles.
# `robustness` is deliberately unmatched: adversarial robustness is a term.
TIER1_TECH_PASS: Final = _words(r"robust(?:ly)?", r"comprehensive(?:ly)?")

TIER1_ADVISORY: Final = _words(
    r"realms?",
    r"paradigms?",
    r"unpack(?:s|ed|ing)?",
    r"actionable",
    r"best practices?",
    r"serv(?:e|es|ed|ing) as",
    r"genuine",
    r"embrac(?:e|es|ed|ing)",
    r"load-bearing",
    r"leverage",
    r"underscore",
    r"journeys?",
    # `key` only before an abstract noun, so key rotation and API keys pass.
    r"key (?:takeaway|insight|factor|role|driver|challenge|component|point"
    r"|aspect|element|finding|difference|priorit(?:y|ies)|reason|benefit"
    r"|lesson|theme|trend|player|stakeholder)s?",
    r"highlight(?:s|ed|ing)",
    # From the 2026-09-20 doc review. Each has a literal sense for this
    # owner: framework crosswalks align with a standard, ISO 27001 clause 5.1
    # requires leadership and commitment, Whisper is a speech model.
    r"enhanced",
    r"align(?:s|ed|ing)? with",
    r"insights?",
    r"touch ?points?",
    r"whisper(?:s|ed|ing)?",
    r"commitment to",
    r"across different",
    r"rich (?:tapestry|history|heritage|tradition|culture|array|variety"
    r"|set of|insights?|understanding)",
    # Register 2026-10-30, 10-31, and 11-02: words the anti-ai-slop pass
    # removed from Rock's own pastes, so the register records them as not
    # his voice. Each has a literal use ("demonstrated the exploit on
    # stage"), which keeps them ADVISORY.
    r"demonstrat(?:e|es|ed|ing)",
    r"emphasi[sz](?:e|es|ed|ing)",
    r"essentially",
    r"honestly",
    r"clearly",
    r"definitively",
    r"explicitly",
    r"conspicuous(?:ly)?",
    # The voice guide: he approves in plain words and rarely writes
    # "awesome" or "excited." The 2026-10-30 paste carried "brilliant."
    r"brilliant",
    r"amazing",
    r"incredible",
    r"fantastic",
    r"awesome",
    # Register 2026-10-31: "we're aligned on the big picture" read as a
    # reviewer signing off on a friend's work.
    r"(?:we're|we are) aligned",
    r"big picture",
)

TIER2: Final = _words(
    r"harness(?:es|ed|ing)?",
    r"navigat(?:e|es|ed|ing)",
    r"foster(?:s|ed|ing)?",
    r"elevat(?:e|es|ed|ing)",
    r"unleash(?:es|ed|ing)?",
    r"streamlin(?:e|es|ed|ing)",
    r"empower(?:s|ed|ing)?",
    r"bolster(?:s|ed|ing)?",
    r"spearhead(?:s|ed|ing)?",
    r"resonat(?:e|es|ed|ing)",
    r"revolutioni[sz](?:e|es|ed|ing)",
    r"facilitat(?:e|es|ed|ing)",
    r"underpin(?:s|ned|ning)?",
    r"nuanced",
    r"crucial",
    r"multifaceted",
    r"ecosystems?",
    r"myriad",
    r"plethora",
    r"encompass(?:es|ed|ing)?",
    r"cataly[sz](?:e|es|ed|ing)",
    r"cultivat(?:e|es|ed|ing)",
    r"illuminat(?:e|es|ed|ing)",
    r"elucidat(?:e|es|ed|ing)",
    r"cornerstones?",
    r"paramount",
    r"poised",
    r"burgeoning",
    r"nascent",
    r"overarching",
    r"transformative",
    r"deeply (?:integrated|committed|rooted|embedded)",
)

TIER3: Final = _words(
    r"significant(?:ly)?",
    r"innovati(?:ve|on|ons)",
    r"effective(?:ly)?",
    r"dynamic",
    r"scalable",
    r"compelling",
    r"unprecedented",
    r"exceptional(?:ly)?",
    r"remarkabl[ey]",
    r"sophisticated",
    r"instrumental",
    r"world-class",
    r"state-of-the-art",
    r"best-in-class",
)

SIGNIFICANCE_ING: Final = (
    "highlighting|underscoring|emphasi[sz]ing|reflecting|symboli[sz]ing"
    "|showcasing|signaling|signalling|illustrating|reinforcing|demonstrating"
)
RESULT_ING: Final = (
    "ensuring|enabling|allowing|making|leading|resulting|driving"
    "|contributing|fostering|encompassing|cultivating|paving"
)

RULES: Final[tuple[Rule, ...]] = (
    Rule(
        "H-DASH",
        HARD,
        # The list separator carve-out from the anti-ai-slop Formatting rules
        # is applied in mask(), so this pattern only sees prose splices.
        re.compile("\u2014" r"|(?<=\w)--(?=\w)|(?<=\s)--(?=\s)"),
        "Em dash. Use a comma, period, colon, or parentheses.",
    ),
    Rule(
        "H-DASH-SUB",
        HARD,
        # An en dash between digits is an ordinary numeric range and passes.
        re.compile("(?<=\\S) [\u2013-] (?=\\S)|(?<=[A-Za-z])\u2013(?=[A-Za-z])"),
        "En dash or spaced hyphen standing in for an em dash.",
    ),
    Rule(
        "H-SEMI",
        HARD,
        re.compile(r";"),
        "Semicolon. Split the sentence or use a comma or colon.",
    ),
    Rule(
        "H-VOCAB",
        HARD,
        TIER1_HARD,
        "Tier 1 word. Delete the clause or state the specific fact.",
    ),
    Rule(
        "H-VOCAB",
        HARD,
        TIER1_TECH_PASS,
        "Tier 1 word outside technical writing. State the specific property.",
        profiles=("blog", "social", "email", "formal"),
    ),
    Rule(
        "H-ANTITHESIS",
        HARD,
        _rx(
            r"\bnot (?:just|only|merely|simply)\b"
            r"|\b(?:is|are|was|were|does|do|did)n't (?:just|only|merely|simply|about)\b"
            r"|\b(?:it|this|that)(?:'s| is| was) not (?:about )?[^.!?\n]{1,60}"
            r"[,.] (?:it|this|that)(?:'s| is| was)\b"
            r"|(?:^|[.!?]\s)Not [^.!?\n]{1,40}[.!?]\s+Not\b"
        ),
        "Leading antithesis. State the positive claim directly.",
    ),
    Rule(
        "H-CONNECTOR",
        HARD,
        re.compile(
            r"(?:^|(?<=[.!?]\s))"
            r"(?:However|Moreover|Furthermore|Additionally|Consequently|Subsequently"
            # Register 2026-11-02: "Interestingly," and "Crucially," came out
            # of Rock's pastes in the passes he asked for. Rock's standing
            # writing rules ban editorializing adverbs (notably, importantly).
            r"|Interestingly|Crucially|Importantly|Notably|Essentially"
            r"|Fundamentally|Undeniably),",
            re.MULTILINE,
        ),
        # Sentence-opening So is deliberately absent. See the fifth maintainer
        # note in coffee-peer-voice: the owner uses it on purpose.
        "Formal connector. Split the sentence or use a plain conjunction.",
    ),
    Rule(
        "H-THROAT",
        HARD,
        _rx(
            r"\bhere's the thing\b|\bhere's what most people miss\b"
            r"|\bit(?:'s| is) worth noting\b"
            r"|\bit(?:'s| is) important to (?:note|remember)\b"
            r"|\bin today's\b|\bin conclusion\b|\bbut it gets worse\b"
            r"|\bthat's where it falls apart\b|\blet me explain\b"
            r"|\blet's (?:dive in|explore|take a look|break (?:this|it) down)\b"
            r"|\bquite frankly\b|\bto be honest\b|\blet's be clear\b"
            r"|\bwhat does this mean for you\b|\bwhy should you care\b"
            r"|\bthe future looks bright\b|\bonly time will tell\b"
            r"|\bas we move forward\b"
            r"|\bi (?:hope|trust) this (?:email|message|note) finds you\b"
            # Emotional flatline and staged reveals (anti-ai-slop catalog,
            # register 2026-10-22 "is already written down" family).
            r"|\bwhat surprised me (?:the )?most\b|\bthe most interesting part\b"
            r"|\bi was fascinated to\b|\binteresting thing here\b"
            r"|\bhere's the (?:kicker|catch|twist|punchline)\b"
            r"|(?:^|(?<=[.!?]\s))(?:the|and the|but the) (?:result|catch|kicker"
            r"|twist|punchline|irony|upshot|verdict)\?"
            # Register 2026-10-16: "There are two ways this goes." announces
            # a turn and stages an options memo for an executive.
            r"|\bthere are (?:two|three|four|a few|a couple of|several|\d{1,2})"
            r" (?:ways|paths|options|scenarios|outcomes|possibilities)"
            r" (?:this|it|things|we) (?:goes|go|can go|could go|plays? out"
            r"|could play out|shakes? out)\b"
            # Register 2026-10-09: "Cap the session, starting here:" is a colon
            # setup announcing the instruction that follows.
            r"|,\s{0,2}starting (?:here|with this|now):"
        ),
        "Throat clearing. Delete it and open on the point.",
    ),
    Rule(
        "H-CHATBOT",
        HARD,
        _rx(
            r"\bgreat question\b|\byou're absolutely right\b|\bcertainly!"
            r"|\bi hope this helps\b|\bfeel free to reach out\b"
            r"|\blet me know if you need anything else\b"
            r"|\bi'd be happy to help\b|\bas of my last (?:update|training)\b"
            r"|\bi don't have access to real-time\b"
            r"|\bin this article, we will\b"
        ),
        "Chatbot artifact. Remove.",
        profiles=PROFILES,
    ),
    Rule(
        "H-FINGERPRINT",
        HARD,
        _rx(
            r"\bcite(?:turn|_)[^\s]{1,40}|contentReference\[oaicite|oai_citation"
            r"|\[attached_file:\d+\]"
            r"|utm_source=(?:chatgpt\.com|copilot\.com|claude\.ai|perplexity\.ai)"
            r"|referrer=grok\.com"
            r"|\[(?:your name|insert [^\]]{1,40}|describe [^\]]{1,40})\]"
            r"|\b20\d\d-XX-XX\b"
        ),
        "AI tool fingerprint. Strip the token or fill in the real content.",
        profiles=PROFILES,
    ),
    Rule(
        "H-ATTRIBUTION",
        HARD,
        _rx(
            r"\b(?:experts|analysts|observers|critics|researchers)"
            r" (?:say|believe|argue|agree|suggest|have cited)\b"
            r"|\b(?:studies|research) (?:shows?|suggests?)\b"
            r"|\bindustry reports (?:suggest|show|indicate)\b"
            r"|\bit is widely (?:regarded|believed|considered)\b"
            r"|\bmany (?:experts|people) (?:say|believe)\b"
            r"|\b(?:several|multiple|numerous) (?:sources|reports|studies)"
            r" (?:indicate|suggest|show)\b"
        ),
        "Vague attribution. Name the source or drop the claim.",
    ),
    Rule(
        "H-HEDGE-STACK",
        HARD,
        # "What could possibly go wrong" is spoken idiom, and Rock's own fix in
        # the register (2026-10-09) carries it, so the idiom passes.
        _rx(
            r"\b(?:could|may|might) (?:potentially|possibly|eventually|ultimately)\b"
            r"(?<!could possibly)(?! go wrong)"
            r"|\b(?:could|may|might) possibly\b(?! go wrong)"
        ),
        "Stacked hedge. Pick one.",
    ),
    Rule(
        "H-WORTH",
        HARD,
        _rx(r"\bworth (?:reading|a look|checking out|your time)\b|\bmust-read\b"),
        "Vague endorsement. Say what it is and who it is for.",
    ),
    Rule(
        "H-DREAD",
        HARD,
        _rx(r"\bkeeps? (?:\w+ ){1,3}up at night\b"),
        "Dread cliche. Name the risk, who carries it, and the cost.",
    ),
    Rule(
        "H-ING-TAIL",
        HARD,
        _rx(r",\s+(?:" + SIGNIFICANCE_ING + r")\b[^.!?\n]{0,80}[.!?]"),
        "Significance participle tail. End the sentence at the fact.",
    ),
    Rule(
        "H-SIGNIFICANCE",
        HARD,
        _rx(
            r"\bstands? as\b|\bis a (?:testament|reminder)\b"
            r"|\bplay(?:s|ed|ing)? an? (?:vital|significant|crucial|pivotal|key"
            r"|central|critical|important|major) role\b"
            r"|\breflect(?:s|ing)? broader\b|\bsetting the stage\b"
            r"|\b(?:marking|shaping) the future\b"
            r"|\brepresents a (?:broader |major |fundamental )?shift\b"
            r"|\bturning point\b|\bfocal point\b|\bindelible mark\b"
            r"|\bcontributing to the evolution\b"
        ),
        "Significance inflation. State what happened and let the reader judge.",
    ),
    Rule(
        "H-PROMO",
        HARD,
        _rx(
            r"\bin the heart of\b|\bnatural beauty\b|\bbreathtaking\b"
            r"|\bmust-see\b|\b(?:it's|it is|that's) like having\b"
        ),
        "Brochure or staged analogy language. Describe the thing plainly.",
    ),
    Rule(
        "H-CONCESSIVE",
        HARD,
        _rx(
            r"\bdespite these (?:challenges|limitations|obstacles|setbacks)\b"
            r"|\bfaces? (?:several|numerous|many|a number of|significant)"
            r" challenges\b"
        ),
        "Challenges template. Put each problem where it belongs in the piece.",
    ),
    # Praise labels that grade someone's work instead of saying what it does.
    # Added 2026-11-04 after the second Voice Corrections Register hit: the
    # 2026-10-26 Helen Oakley comment ("the feature I'd show every AppSec team
    # first," "I'm stealing," "go kick the tires") and the 2026-11-04 Gadi
    # Evron comment ("is the headline, and it deserves to be," "the math is
    # the best part"). Rock called the second one sycophantic. Every pattern
    # is a grade with no fact in it, so the rule is HARD. "deserves to be" on
    # its own stays legal ("the user deserves to be notified"), which is why
    # the bare form only matches at the end of a clause after "and it."
    Rule(
        "H-PRAISE-LABEL",
        HARD,
        _rx(
            r"\b(?:is|was|are|were) the (?:headline|best part|real star"
            r"|star of the show|standout|real story)\b"
            r"|\band (?:it|this|that|they|she|he) deserves? (?:to be|it)\s{0,2}[.!]"
            r"|\bdeserves? (?:to be (?:read|celebrated|required reading|everywhere"
            r"|the headline)|(?:way |a lot |so much |far |much )?more (?:attention"
            r"|eyes|love|credit|readers|buzz|than it(?:'s| is) getting))\b"
            r"|\bthe (?:smartest|best|cleverest|coolest) (?:thing|part|idea|move"
            r"|line) (?:in|about)\b"
            r"|\bthe (?:feature|part|line|idea|one) I(?:'d| would) (?:show|send"
            r"|point|hand) every\b"
            r"|\bI'm (?:stealing|borrowing) (?:this|that|it)\b"
            r"|\b(?:the one|what|the line|the question) I'm (?:stealing|borrowing)\b"
            r"|\bkick the tires\b|\bmust[- ]reads?\b|\bunparalleled\b"
            r"|\bcouldn't be prouder\b"
            # 1.6.0, register 2026-10-13: "Unharvested payroll is exactly the
            # phrase that ends up in the budget deck" praised a commenter's
            # coined jargon. 2026-11-02: "doesn't shy away from" came out of
            # Rock's paste. 2026-10-09: "I respect the honesty" opened a meme
            # in deference to its target.
            r"|\bis exactly the (?:phrase|word|term|line|framing|kind of)\b"
            r"|\b(?:doesn't|does not|didn't|don't) shy away from\b"
            r"|\bI (?:respect|appreciate) the (?:honesty|transparency|candor)\b"
        ),
        "Praise label grading the work. Say what the work does and let that carry the support.",
    ),
    # ----- 1.6.0 register rules (HARD) -------------------------------------
    # Register 2026-11-05: "Details and a short follow-up list are on the PR."
    # A pointer sentence carries no information. Say what is there.
    Rule(
        "H-POINTER",
        HARD,
        _rx(
            r"\b(?:the )?(?:details|specifics|the rest|more detail|the full"
            r" (?:list|details|breakdown|write-?up|story))(?: and [^.!?\n]{1,60})?"
            r" (?:is|are|live|lives|sit|sits) (?:on|in) the (?:PR|pull request"
            r"|issue|doc|thread|ticket|report|deck|repo|link)\b"
        ),
        "Pointer sentence. Name what is on the PR, issue, or doc in this sentence.",
    ),
    # Register 2026-10-06 ("Two sentences you can use as they stand."),
    # 2026-10-29 ("If you're good w/ the shape"), and 2026-10-31 ("a check
    # folks can take home"). A label for the deliverable stands in for it.
    Rule(
        "H-DELIVERABLE-LABEL",
        HARD,
        _rx(
            r"\b(?:one|two|three|a few|a couple of|\d{1,2}) (?:sentences?|lines?)"
            r" you can (?:use|steal|paste|send|lift|drop in)\b"
            r"|\buse as (?:they|it) stands?\b"
            r"|\bhere's (?:a|the|one) (?:line|sentence|framing|phrase) (?:you can"
            r"|to) (?:use|steal|send|lift)\b"
            r"|\bthe (?:sentence|line) I'd use\b"
            r"|\b(?:a|the|one) (?:check|framework|takeaway|playbook|toolkit"
            r"|checklist|lens|model|template) (?:folks|people|you|they|attendees"
            r"|the (?:audience|room)) can (?:take home|take back|use|steal|run"
            r"|apply)\b"
            r"|\b(?:good|ok|okay|fine|happy|comfortable|aligned|on board)"
            r" (?:w/|with) the (?:shape|direction|approach)\b"
            r"|\bthe shape of (?:it|this|the (?:fix|plan|answer|proposal|change))\b"
        ),
        "Deliverable label. Name the thing itself (the two rules, the four calls).",
    ),
    # Register 2026-10-31: "I'll keep Zenity and any product pitch out of all
    # three." A disclaimer nobody asked for plants the worry it removes.
    Rule(
        "H-DISCLAIMER",
        HARD,
        _rx(
            r"\b(?:I'll|I will|I'd|we'll|we will) keep (?:[\w&']{1,30} ){0,3}(?:and )?"
            r"(?:any |all |the )?(?:product|vendor|sales|marketing) pitch(?:es)?"
            r" out\b"
            r"|\b(?:this|it) (?:isn't|is not|won't be|will not be) (?:a|an)"
            r" (?:sales |vendor |product |marketing )?pitch\b"
            r"|\bno (?:sales|vendor|product|marketing) pitch\b"
        ),
        "Volunteered disclaimer. Cut it unless Rock asked for one or the reader raised it.",
    ),
    # Register 2026-10-31: "I'm glad the tabletop landed." "Landed" is a stock
    # figure for went well. "The commit landed" is literal git usage and
    # does not match, because the subject list holds only talk-shaped nouns.
    Rule(
        "H-LANDED",
        HARD,
        _rx(
            r"\b(?:talk|session|tabletop|keynote|workshop|panel|presentation"
            r"|message|point|joke|post|pitch|demo|framing|argument)s?"
            r" (?:really |actually |clearly )?(?:landed|resonated|hit home"
            r"|struck a chord)\b"
        ),
        "Stock figure for went well. Say what happened or thank them and move on.",
    ),
    # Register 2026-10-09 ("He's a dear friend, so I'm biased, but") and
    # 2026-10-24 ("discount my enthusiasm as you see fit," "hype it anyway").
    # coffee-peer-voice has banned performative hedging since 1.6, and the
    # linter had no rule for it.
    Rule(
        "H-PERF-HEDGE",
        HARD,
        _rx(
            r"\bcorrect me if I'm wrong\b|\bmaybe I'm missing something\b"
            r"|\bI'd (?:love|like) to be wrong\b"
            r"|\bI (?:could|might|may) be wrong(?:,| here,?)? but\b"
            r"|\bso I'm (?:biased|partial)\b|\bI'm (?:biased|partial),? but\b"
            r"|\bdiscount (?:my|this|the) (?:enthusiasm|bias|take|opinion)\b"
            r"|\bgrain of salt\b|\bhype it anyway\b"
        ),
        "Performative hedge. State the backing or the uncertainty plainly.",
    ),
    # Register 2026-10-13 ("On your CFO question,") and 2026-10-23 ("On
    # breaking in, I'm not budging."), promoted on Rock's instruction: flag
    # any sentence that opens "On <noun phrase>," even when it continues.
    # Temporal and idiomatic openers stay legal ("On Tuesday I wrote," "On
    # prem, the customer hosts," "On average,"). Case-sensitive on purpose.
    Rule(
        "H-TOPIC-CLAUSE",
        HARD,
        re.compile(
            r"(?:^|(?<=[.!?]\s))On (?!(?:Monday|Tuesday|Wednesday|Thursday"
            r"|Friday|Saturday|Sunday|January|February|March|April|May|June"
            r"|July|August|September|October|November|December|average"
            r"|balance|paper|prem|premises|top|second thought|purpose|stage"
            r"|the other hand|the flip side|the bright side|the record|the call"
            r"|the panel|the podcast|the recording|the demo|the plus side"
            r"|LinkedIn|Slack|GitHub|Twitter|X|day|the day|the first day"
            r"|\d)\b)(?:your |the |my |our |his |her |their |this |that )?"
            r"(?:[\w'/-]{1,25} ){0,4}[\w'/-]{1,25},",
            re.MULTILINE,
        ),
        "Topic-label clause. Answer in the first clause with a plain subject and verb.",
    ),
    # Register 2026-10-29: "Issue #318 is the last thing I want your read on."
    # 2026-10-22: "I'd underline one line from Satya that you flagged."
    # Both point back at a thing before saying anything about it.
    Rule(
        "H-POINTBACK",
        HARD,
        _rx(
            r"\b(?:want|'d like|would like|need) your (?:read|take|eyes|thoughts)"
            r" on[.!]"
            r"|\bthe (?:last|first|one|main|other|big) thing I(?: want|'d like"
            r"| would like| need) your (?:read|take|eyes|thoughts) on\b"
            r"|\bI'd (?:underline|highlight|call out|flag|point to|single out"
            r"|pull out) (?:one|a|the|this|that) (?:line|point|bit|part"
            r"|sentence|passage|quote)\b"
            r"|\bis the (?:one|word|term|label|phrase) I'd (?:drop|cut|change"
            r"|avoid|lose|kill|watch|be (?:most )?careful (?:with|about))\b"
        ),
        "Point-back opener or word verdict. Open on the claim about the thing itself.",
    ),
    # Register 2026-10-16: "54 days left of the ninety." A standing deadline
    # restated as a countdown manufactures urgency from arithmetic.
    Rule(
        "H-COUNTDOWN",
        HARD,
        _rx(
            r"\b\d{1,4} days? (?:left|remain(?:ing)?) (?:of|in) the\b"
            r"|\b\d{1,4} days remain\b"
        ),
        "Countdown. Name the commitment only when something moved against it.",
    ),
    # Register 2026-10-16, Rock's standing rule: boards never approve spend.
    # A board-approved budget is a governance blueprint, so "budget" is
    # deliberately absent from the noun list.
    Rule(
        "H-BOARD-SPEND",
        HARD,
        _rx(
            r"\b(?:the |your |their )?boards? (?:approved|approves|approve"
            r"|signed off on|green-?lit|greenlit|funded|bought|picked)"
            r" (?:a |an |the |your |their )?(?:[\w-]{1,20} ){0,3}(?:purchase"
            r"|tool|spend|spending|scanner|platform|vendor|contract|product"
            r"|solution|license|headcount)s?\b"
        ),
        "Boards never approve spend. Name who approved the purchase.",
    ),
    # Register 2026-10-14: "makes you feel better and tells your board
    # nothing" paired a feeling with an absence and staged the same reveal as
    # "gives comfort, not assurance" without a "not" for H-ANTITHESIS.
    Rule(
        "H-PAIRED-CONTRAST",
        HARD,
        _rx(
            r"\bmakes? (?:you|them|us|people|everyone|the board|teams?) feel"
            r" (?:[\w-]{1,20} ){0,3}and (?:tells|says|proves|shows|does)"
            r" (?:[\w-]{1,20} ){0,3}nothing\b"
            r"|\bgives? (?:you |them |us )?comfort,? not (?:assurance|security"
            r"|proof)\b"
        ),
        "Paired contrast staging a reveal. State the mechanism and its consequence.",
    ),
    # coffee-peer-voice "Anchor in something real, by name": "a recent study"
    # and "a company I know" are how machines talk. The linter had no rule.
    Rule(
        "H-VAGUE-SOURCE",
        HARD,
        re.compile(
            r"\b[Aa] (?:recent|new|major|landmark) (?:study|report|survey|paper"
            r"|analysis)\b(?! (?:from|by|at|in|out of|published by) [A-Z])"
            r"|\b[Aa] company I (?:know|worked with)\b"
        ),
        "Unnamed source. Name the study, the publisher, and the date.",
    ),
    # ----- 1.6.0 shape rules (HARD) ----------------------------------------
    # SlopShape core value STR_FLW_006: AI posts state their thesis and
    # announce their flow before the first section. The paper's example is
    # "In this post, we'll cover why onboarding stalls, three fixes that work,
    # and how to measure the difference." The announcement forms below have
    # no use in Rock's voice, which opens on the news or the claim.
    Rule(
        "H-SHAPE-ROADMAP",
        HARD,
        _rx(
            r"\bin this (?:post|article|piece|guide|issue|newsletter|blog"
            r"(?: post)?|write-?up|thread|essay),? (?:I|we)(?:'ll| will| want to"
            r"|'m going to| are going to| walk| cover| explore| look)\b"
            r"|\bby the end of this (?:post|article|piece|guide|issue|thread"
            r"|essay)\b"
            r"|\bhere's what (?:we'll|you'll|I'll) (?:cover|learn|explore"
            r"|walk through)\b"
        ),
        f"Roadmap announcement (SlopShape thesis-first, gap {GAP_THESIS_FIRST}). "
        "Open on the news or the claim.",
        profiles=("blog", "social", "email", "formal"),
    ),
    # SlopShape core values STR_STG_008 (restated-thesis ending, gap 0.650,
    # the largest in the paper) and STR_STG_001 (summary stage, gap 0.609).
    Rule(
        "H-SHAPE-RECAP",
        HARD,
        re.compile(
            r"(?:^|(?<=[.!?]\s))(?:In summary|To sum (?:it )?up|To summarize"
            r"|To recap|In a nutshell|All in all|In short"
            r"|Key takeaways?|The (?:key |main |big )?takeaways? (?:here )?is"
            r"|The bottom line(?: is)?|Bottom line)\b",
            re.MULTILINE,
        ),
        f"Recap stage (SlopShape summary {GAP_SUMMARY_STAGE}, restated thesis "
        f"{GAP_RESTATED_THESIS}). End on a new point, the next step, or the last fact.",
        profiles=("blog", "social", "email", "formal"),
    ),
    # SlopShape core values STR_FLW_005 (legacy-versus-modern contrast, gap
    # 0.497) and TIM_CUE_011 (modern or next-generation framing, gap 0.360).
    # The paper's example: "Paper checklists were built for a slower era."
    Rule(
        "H-SHAPE-ERA",
        HARD,
        _rx(
            r"\b(?:was|were|is|are) built for (?:a|an|the) (?:slower|simpler"
            r"|different|older|earlier|bygone|pre-[\w-]{1,20}|analog|paper)"
            r" (?:era|age|time|world|decade|century)\b"
            r"|\bfuture[- ](?:proof(?:ed|ing)?|ready)\b"
            r"|\bin (?:an|this|the) (?:era|age) (?:of|where|when)\b"
            r"|\b(?:the|today's) modern (?:enterprise|organi[sz]ation|business"
            r"|workplace|SOC|CISO|security team|world)\b"
        ),
        f"Era framing (SlopShape legacy-vs-modern {GAP_LEGACY_MODERN}, modern "
        f"framing {GAP_MODERN_FRAMING}). Name the date and the specific change.",
    ),
    Rule(
        "A-VOCAB",
        ADVISORY,
        TIER1_ADVISORY,
        "Flagged word with a legitimate literal sense. Keep only if literal.",
    ),
    Rule(
        "A-ANTITHESIS-REVERSED",
        ADVISORY,
        re.compile(r", not (?!only\b|just\b)"),
        "Reversed antithesis (Y, not X). Keep only if the contrast is real.",
    ),
    Rule(
        "A-ING-TAIL",
        ADVISORY,
        _rx(r",\s+(?:" + RESULT_ING + r")\b[^.!?\n]{0,80}[.!?]"),
        "Result participle tail. Give the result its own sentence and verb.",
    ),
    Rule(
        "A-CLEFT",
        ADVISORY,
        _rx(
            r"\bthe reason\b[^.!?\n]{0,60}\bis\b"
            r"|\bwhat (?:matters|counts|changed|broke)\b[^.!?\n]{0,30}\bis\b"
            r"|\bthe thing (?:that|is)\b"
            # Register 2026-10-23: "What decided this week was dumber."
            r"|(?:^|(?<=[.!?]\s))what [a-z]{2,20}ed\b[^.!?\n]{0,40}\b(?:is|was)\b"
        ),
        "Cleft or nominalized subject. Use a plain subject and verb.",
    ),
    Rule(
        "A-CONCESSIVE",
        ADVISORY,
        re.compile(
            r"(?:^|(?<=[.!?]\s))(?:While|Although) [^,.\n]{1,80} "
            r"(?:may|might) (?:seem|appear)\b|\bDespite its\b",
            re.MULTILINE,
        ),
        "Concessive frame. Match the depth of discussion to real weight.",
    ),
    Rule(
        "A-FALSE-RANGE",
        ADVISORY,
        _rx(
            r"\bfrom (?:\w+ ){0,3}(?:small|tiny|large|big|startups?|enterprises?"
            r"|corporations?|fortune 500|smbs?|beginners?|novices?|experts?"
            r"|veterans?)\b[^.!?\n]{0,30}? to (?:\w+ ){0,3}(?:small|tiny|large"
            r"|big|startups?|enterprises?|corporations?|fortune 500|smbs?"
            r"|beginners?|novices?|experts?|veterans?)\b"
        ),
        "False range. Name the specific examples you mean.",
    ),
    Rule(
        "A-HEADER",
        ADVISORY,
        # ADVISORY until the owner rules on it: a newsletter format may use
        # one of these headers on purpose.
        _rx(
            r"^(?:#{1,6}\s*|\*\*)\s*(?:why (?:it|this) matters"
            r"|why this is important|future outlook"
            r"|challenges and [\w ]{1,30})"
        ),
        "Editorial section header. Let the content show its own relevance.",
    ),
    Rule(
        "A-CREDENTIALS",
        ADVISORY,
        _rx(
            r"\bfeatured in\b|\bprofiled in\b|\bindependent coverage\b"
            r"|\bmaintains an active (?:social media )?presence\b"
            r"|\bleading expert\b"
        ),
        "Coverage list used as proof. Fine in a bio. Elsewhere, use the source.",
    ),
    Rule(
        "A-ANALOGY",
        ADVISORY,
        _rx(
            r"\bthink of (?:it|this|them) as\b|\bakin to\b"
            r"|\bmuch like an?\b|\bis like an?\b"
        ),
        "Analogy. Keep it only if the mechanism is unclear without it.",
    ),
    Rule(
        "A-CLICHE",
        ADVISORY,
        # Seed list written by the linter's author, NOT taken from the doc.
        # The doc and the owner's standing rule ban cliches in general, which
        # no regex can enforce, so this list grows from the corrections log.
        _rx(
            r"\bsilver bullets?\b|\bdouble-edged sword\b|\btip of the iceberg\b"
            r"|\blow-hanging fruit\b|\bmov(?:e|es|ed|ing) the needle\b"
            r"|\bperfect storm\b|\bwild west\b|\bnorth star\b"
            r"|\bcat[- ]and[- ]mouse\b|\bcanary in the coal mine\b"
            r"|\belephant in the room\b|\bboil(?:ing)? the ocean\b"
            r"|\bat the end of the day\b|\bsecret sauce\b|\bmagic bullets?\b"
            r"|\bbehind the curve\b|\bleft in the dust\b|\brising tide lifts\b"
            # 1.6.0, from the register: a metaphor that kept working after
            # its setup was cut (2026-10-09 "badge," twice), coined movement
            # verbs (2026-10-04 "took the same hop"), pictures standing in for
            # a rule (2026-10-04 "the attacker's column"), and a place word
            # pointing at a source's metaphor (2026-10-14 "back there").
            r"|\b(?:wore|wears|wearing|whose) (?:[\w'-]{1,20} )?badge\b"
            r"|\b(?:took|takes|take|made) the same hop\b|\bin transit\b"
            r"|\bthe attacker's column\b|\bhits the table\b|\bback there\b"
        ),
        "Business cliche or decorative metaphor. Spoken idiom Rock would say out loud is fine.",
    ),
    # ----- 1.6.0 register rules (ADVISORY) ---------------------------------
    # Register 2026-10-07 ("items 2 and 3") and 2026-11-05 ("which is ask 6
    # again"). Rock writes "No. 6" and "read 7 again!" himself, so this stays
    # ADVISORY: keep a number only when the reader can see what it names.
    Rule(
        "A-XREF",
        ADVISORY,
        _rx(
            r"\b(?:items?|asks?|points?|steps?|options?|bullets?)"
            r" #?\d{1,3}(?: (?:and|or|through|to) #?\d{1,3})?\b"
            r"|\bsee (?:above|below)\b"
            r"|\bas (?:noted|mentioned|discussed|described|covered) (?:above"
            r"|below|earlier)\b"
        ),
        "Cross-reference by label. Name the requirement or the content in this sentence.",
    ),
    # Register 2026-10-31: "I imagine it would also function as" stacked two
    # hedges on a spec fact. H-HEDGE-STACK only covers "could potentially."
    Rule(
        "A-HEDGE-STACK",
        ADVISORY,
        _rx(
            r"\bI (?:imagine|think|suspect|guess|believe|feel like) (?:it|this"
            r"|that|they|we|you) (?:would|might|could|may)\b"
            r"|\b(?:would|might|could|may) (?:likely|probably|perhaps)\b"
            r"|\bperhaps (?:might|could|may)\b"
        ),
        "Two hedges on one claim. Keep one, sized to the evidence.",
    ),
    # Register 2026-10-30 ("the agents I use for my own business"), 2026-10-26
    # ("I spent the morning in your code"), and 2026-10-24 ("The part I'm
    # proudest of"). Three hits of an invented first person fact or feeling.
    # A regex cannot know whether Rock said it, so every hit gets a check.
    Rule(
        "A-FIRSTPERSON-CLAIM",
        ADVISORY,
        _rx(
            r"\bI (?:spent|went through|read|ran|tested|dug (?:into|through)"
            r"|reviewed|looked (?:at|through)|tried|built|walked through"
            r"|cloned|installed|deployed|use|run)\b[^.!?\n]{0,60}"
            r"|\bthe (?:part|thing|piece) I'm (?:most )?proud(?:est)? of\b"
            r"|\bI'm (?:most |so |really |incredibly )?proud(?:est)? of\b"
            r"|\bwhat (?:excites|worries|scares|bothers) me (?:the )?most\b"
            r"|\bI'm (?:so |really )?excited\b"
        ),
        "First person claim or feeling. Keep it only if Rock stated it in this conversation.",
    ),
    # Register 2026-10-14: Rock writes "on prem" (two words, no hyphen).
    Rule(
        "A-ROCK-TERM",
        ADVISORY,
        _rx(r"\bon[- ]premises?\b|\bon-prem\b"),
        "Rock's term is 'on prem'.",
    ),
    # Register 2026-10-14 ("<name>, ... Send him," "<name>, please request ours")
    # and 2026-10-31 ("Could you drop a Guardian box" was fine, "drop a
    # Guardian box" was not). He poses an ask to a peer as a question.
    Rule(
        "A-PEER-IMPERATIVE",
        ADVISORY,
        re.compile(
            r"(?:^|(?<=[.!?]\s))(?!(?:Thanks|Ok|Okay|Yes|No|So|Also|Sure|Great|Hey|Hi"
            r"|Then|Next|Now|First|Second|Third|Finally|Again|Otherwise|Honestly),)"
            r"[A-Z][a-z]{1,15}, (?:please )?(?:send|request"
            r"|pull|run|mark|drop|add|file|update|fix|change|move|submit|make"
            r"|grab|take|ship|merge|delete|remove|rewrite|cut)\b",
            re.MULTILINE,
        ),
        "Imperative to a peer. Pose it as a question to the person who owns the work.",
        profiles=("email",),
    ),
    # Register 2026-10-11 ("I'd want to see more before I signed one") and
    # 2026-10-09 ("so nobody knows"). A want or a gap with no object.
    Rule(
        "A-NO-OBJECT",
        ADVISORY,
        _rx(
            r"\b(?:want|need|like) to (?:see|know|hear) more(?: first)?[.!]"
            r"|\b(?:see|know|need|hear) more before I\b"
            r"|\bnobody knows[.!]"
        ),
        "No object. Name the exact data or fact in the same sentence.",
    ),
    # Register 2026-10-04: "The tell is the colon list itself, in prose or as
    # bullets, and three items is only its most common shape."
    Rule(
        "A-COLON-LIST",
        ADVISORY,
        re.compile(
            r":\s{1,2}(?:[\w'-]{1,20}(?: [\w'-]{1,20}){0,4}, ){1,4}"
            r"(?:[\w'-]{1,20}(?: [\w'-]{1,20}){0,4},? )?(?:and|or)"
            r" [\w'-]{1,20}(?: [\w'-]{1,20}){0,4}[.!?]"
        ),
        "Colon list in prose. Write the items into a sentence with its own verb.",
    ),
    # Register 2026-10-22 ("is already written down") and 2026-10-04 ("The
    # paper had it right the whole time."). A staged reveal or a tidy
    # vindication line in its own sentence.
    Rule(
        "A-STAGED-REVEAL",
        ADVISORY,
        _rx(
            r"\bis already (?:written down|out there|documented|solved|in the"
            r" (?:spec|standard|docs))\b"
            r"|\bhad it right (?:the whole time|all along)\b"
        ),
        "Staged reveal or vindication line. Fold it into the sentence that states the fact.",
    ),
    # Register 2026-10-09: "Every time a marketplace gets poisoned, we buy
    # another scanner." A pattern stated on one case with no purchase under it.
    Rule(
        "A-GENERALIZATION",
        ADVISORY,
        re.compile(
            r"(?:^|(?<=[.!?]\s))(?:Every time|Whenever|Each time) [^,.!?\n]{1,60},"
            r" (?:we|you|they|everyone|the industry|the market|vendors)\b",
            re.MULTILINE,
        ),
        "Generalization. Replace it with the dated event and aim the heat at the mechanism.",
    ),
    # Register 2026-10-22: "That read is dangerous" turned the misreading into
    # a noun label. 2026-10-16: "The cheap one is" labeled an option.
    Rule(
        "A-NOUN-LABEL",
        ADVISORY,
        re.compile(
            r"(?:^|(?<=[.!?]\s))(?:That|This) (?:read|take|framing|reading|lens)"
            r" (?:is|was)\b"
            r"|(?:^|(?<=[.!?]\s))The (?:cheap|easy|hard|fast|slow|safe|risky"
            r"|expensive|first|second|other) (?:one|option|path|route) is\b",
            re.MULTILINE,
        ),
        "Noun label standing in for the thing. Point back with a plain 'That's' or name it.",
    ),
    # coffee-peer-voice 1.6 "Do-X-and-Y-happens": "Drop it silently and every
    # rate is wrong." The prose rule had no linter check.
    Rule(
        "A-DO-X-AND-Y",
        ADVISORY,
        re.compile(
            r"(?:^|(?<=[.!?]\s))(?:Drop|Blind|Skip|Cut|Remove|Break|Kill|Miss"
            r"|Ignore|Turn|Give|Let|Leave|Add|Put|Change|Lose|Starve|Feed|Hand"
            r"|Pull|Flip|Grant|Hide)\b[^.!?,\n]{1,40} and (?:every|your|the"
            r"|nothing|no|it|they|you|that|this|everything)\b[^.!?\n]{1,40}[.!?]",
            re.MULTILINE,
        ),
        "Do-X-and-Y-happens. State the conditional plainly with if or when.",
    ),
    # ----- 1.6.0 shape rules (ADVISORY) ------------------------------------
    # TIM_CUE_011 and STR_FLW_005 forms with a literal use: "next-generation
    # firewall" is a product category, and "no longer" is ordinary English.
    Rule(
        "A-SHAPE-NEXTGEN",
        ADVISORY,
        _rx(
            r"\bnext[- ]gen(?:eration)?\b(?! (?:firewall|antivirus|AV|SIEM"
            r"|endpoint|NGFW)s?\b)"
            r"|\bmodern (?:approach|way|solution|stack|era|world|day)\b"
            r"|\bno longer (?:cuts it|enough|sufficient|an option|optional)\b"
            r"|\btraditional (?:approach|way|model|methods?|tools)\b"
        ),
        f"Modern-versus-legacy framing (SlopShape {GAP_MODERN_FRAMING} and "
        f"{GAP_LEGACY_MODERN}). Name the date and what changed.",
    ),
    Rule(
        "A-EMOJI",
        ADVISORY,
        re.compile("[\U0001f300-\U0001faff\u2600-\u27bf]"),
        "Emoji in professional prose.",
        profiles=("blog", "technical"),
    ),
)

# `- **Term** \u2014 text` and `- [link](url) \u2014 text`: the dash is typography
# there per anti-ai-slop, so mask() blanks it before H-DASH runs.
LIST_SEPARATOR_DASH: Final = re.compile(
    r"^([ \t]*(?:[-*+]|\d+\.) "
    r"(?:\*\*[^*\n]{1,80}\*\*|\[[^\]\n]{1,120}\]\([^)\n]{1,300}\)) )"
    "\u2014",
    re.MULTILINE,
)
OPEN_ASK_RX: Final = re.compile(r"\[ROCK:[^\]\n]{1,200}\]")
HASHTAG_RX: Final = re.compile(r"(?<!\w)#[A-Za-z]\w+")
BOLD_BULLET_RX: Final = re.compile(
    "^[ \\t]*[-*+] \\*\\*[^*\\n]{1,60}(?:[:.]\\*\\*|\\*\\*\\s*[:.\u2014\u2013-])",
    re.MULTILINE,
)
EXCLAIM_RX: Final = re.compile(r"!(?!\[)")
TRIAD_RX: Final = re.compile(r"\b\w+, \w+,? and \w+\b")
CLOSER_ANTITHESIS_RX: Final = _rx(r"\b(?:rather than|instead of)\b")
# Closing lines that narrate why a message was sent ("Wanted you to hear it
# from me before the intro goes out.") or invent a review step ("Flag
# anything I should know first."). Added 2026-10-09 after Rock flagged both
# on a Slack heads up. A search of his rockcyber.com sent mail for seven of
# these phrases that day found his own words only in openers and asks that
# carried a fact ("I just wanted you to know that I haven't forgotten...",
# 2019) and no contentless closer among the hits reviewed. So the check
# reads only the final sentences, and a motive phrase followed by "that"
# passes because the clause carries the news.
CLOSER_SENTENCES: Final = 2
CLOSER_MOTIVE_RX: Final = _rx(
    r"\b(?:wanted|want) you to (?:hear|know|see|be aware)\b"
    r"|\bhear (?:it|this|that|the news) from me\b"
    r"|\b(?:didn't|did not|don't|do not) want (?:you|this|it) to"
    r" (?:be (?:surprised|blindsided|caught off guard)|catch you off guard"
    r"|surprise you|blindside you|come as a surprise"
    r"|hear (?:it|this) from someone else)\b"
    r"|\b(?:figured|thought) you(?:'d| would) want to (?:know|hear|see)\b"
    r"|\b(?:wanted|want) to (?:give you a heads ?up|loop you in"
    r"|keep you in the loop|let you know"
    r"|make sure you (?:knew|know|saw|see|heard|hear))\b"
    r"|\bso you(?:'re| are) not (?:surprised|blindsided|caught off guard)\b"
)
CLOSER_GATE_RX: Final = _rx(
    r"\bflag anything (?:I|we) should (?:know|see|be aware of)\b"
    r"|\banything (?:I|we) should know (?:first|before)\b"
    r"|\b(?:let me know|tell me|ping me|shout) if (?:you have |there are |you see )?"
    r"(?:any )?(?:concerns|objections|issues|red flags) before (?:I|we)\b"
    r"|\bbefore I (?:proceed|move forward)\b"
)
# Quantifiers stay bounded, per the security note in the module docstring.
CLOSER_FACT_RX: Final = re.compile(r"\s{0,3},?\s{0,3}that\b", re.IGNORECASE)
SIGN_OFF_RX: Final = re.compile(
    r"^(?:(?:thanks|thank you|thx|cheers|best|best regards|regards|sincerely"
    r"|talk soon)[,!.]{0,3}(?:\s{1,3}-\s{0,2}[A-Za-z]{1,40})?"
    r"|-\s{0,2}[A-Za-z]{1,40})\.?$",
    re.IGNORECASE,
)
WORD_RX: Final = re.compile("[A-Za-z0-9][A-Za-z0-9'\u2019-]*")

# Periods in these abbreviations do not end a sentence.
ABBREVIATIONS: Final = re.compile(
    r"\b(?:e\.g|i\.e|vs|etc|Mr|Mrs|Ms|Dr|St|No|Inc|Ltd|Corp|U\.S|U\.K)\.$"
)
SENTENCE_SPLIT: Final = re.compile('(?<=[.!?])["\'\u201d\u2019)\\]]*\\s+(?=[A-Z0-9"\u201c(\\[])')


def _blank(match: re.Match[str]) -> str:
    """Replace a match with spaces, keeping newlines so line numbers hold."""
    return re.sub(r"[^\n]", " ", match.group(0))


def mask(text: str, include_quotes: bool) -> str:
    """Blank out material the rules must not judge.

    Code, URLs, and HTML entities are never prose. Quoted material belongs to
    someone else (anti-ai-slop edit mode and its self-reference escape hatch),
    so blockquotes and double-quoted strings are skipped unless
    include_quotes is set. An em dash that separates a bold lead term or a
    link from its description in a list item is typography and is blanked.
    Open asks are blanked so the bracket rule in H-FINGERPRINT cannot fire
    on them.
    """
    masked = LIST_SEPARATOR_DASH.sub(lambda m: m.group(1) + " ", text.translate(CURLY_TO_STRAIGHT))
    masked = re.sub(r"^(```|~~~).*?^\1[^\n]*$", _blank, masked, flags=re.M | re.S)
    masked = re.sub(r"`[^`\n]{1,200}`", _blank, masked)
    masked = re.sub(r"https?://\S+", _blank, masked)
    masked = re.sub(r"&#?\w{1,10};", _blank, masked)
    masked = re.sub(r"^\|[-:| ]+\|[ \t]*$", _blank, masked, flags=re.M)
    masked = OPEN_ASK_RX.sub(_blank, masked)
    if not include_quotes:
        masked = re.sub(r"^[ \t]*>[^\n]*$", _blank, masked, flags=re.M)
        masked = re.sub('"[^"\\n]{1,300}"|\u201c[^\u201d\\n]{1,300}\u201d', _blank, masked)
    return masked


def _line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _context(text: str, start: int, end: int) -> str:
    left = max(0, start - CONTEXT_CHARS)
    right = min(len(text), end + CONTEXT_CHARS)
    return " ".join(text[left:right].split())


def _paragraphs(text: str) -> Iterator[tuple[int, str]]:
    """Yield (start offset, paragraph text) for each prose paragraph."""
    for match in re.finditer(r"(?:[^\n]+\n?)+", text):
        body = match.group(0)
        stripped = body.strip()
        if not stripped or re.match(r"[#|>]|[-*+] |\d+\. ", stripped):
            continue
        yield match.start(), body


def _sentences(paragraph: str) -> list[str]:
    merged: list[str] = []
    for piece in SENTENCE_SPLIT.split(" ".join(paragraph.split())):
        if merged and ABBREVIATIONS.search(merged[-1]):
            merged[-1] = f"{merged[-1]} {piece}"
        elif piece:
            merged.append(piece)
    return merged


def _word_count(sentence: str) -> int:
    return len(WORD_RX.findall(sentence))


def check_rules(original: str, masked: str, profile: str) -> list[Finding]:
    found: list[Finding] = []
    for rule in RULES:
        if profile not in rule.profiles:
            continue
        for hit in rule.pattern.finditer(masked):
            found.append(
                Finding(
                    rule.rule,
                    rule.severity,
                    _line_of(masked, hit.start()),
                    _context(original, hit.start(), hit.end()),
                    rule.message,
                )
            )
    return found


def check_open_asks(original: str) -> list[Finding]:
    return [
        Finding(
            "OPEN-ASK",
            OPEN_ASK,
            _line_of(original, hit.start()),
            hit.group(0),
            "Drafter needs a real detail from the owner before this ships.",
        )
        for hit in OPEN_ASK_RX.finditer(original)
    ]


def check_layout(original: str, masked: str, profile: str) -> list[Finding]:
    found: list[Finding] = []
    bullets = list(BOLD_BULLET_RX.finditer(masked))
    # One bold lead term can be a legitimate definition. Two or more is the
    # layout both skills call a chatbot fingerprint.
    if len(bullets) >= MIN_REPEAT:
        found.extend(
            Finding(
                "H-BOLD-BULLETS",
                HARD,
                _line_of(masked, hit.start()),
                _context(original, hit.start(), hit.end()),
                "Bold lead term bullets. Write the point as prose.",
            )
            for hit in bullets
        )
    tags = HASHTAG_RX.findall(masked)
    if len(tags) >= HASHTAG_LIMIT:
        found.append(
            Finding(
                "H-HASHTAGS",
                HARD,
                _line_of(masked, masked.rfind(tags[-1])),
                " ".join(tags),
                f"{len(tags)} hashtags. Cut to two or three specific tags.",
            )
        )
    bangs = list(EXCLAIM_RX.finditer(masked))
    exclaim_limit = {"email": EMAIL_EXCLAIM_LIMIT, "social": SOCIAL_EXCLAIM_LIMIT}.get(
        profile, MIN_REPEAT
    )
    if len(bangs) >= exclaim_limit:
        found.append(
            Finding(
                "A-EXCLAIM",
                ADVISORY,
                _line_of(masked, bangs[0].start()),
                f"{len(bangs)} exclamation points",
                "Forced enthusiasm. One per piece is plenty.",
            )
        )
    triads = list(TRIAD_RX.finditer(masked))
    if len(triads) > 1 and profile != "technical":
        found.extend(
            Finding(
                "A-TRIAD",
                ADVISORY,
                _line_of(masked, hit.start()),
                _context(original, hit.start(), hit.end()),
                f"One of {len(triads)} three item groups. One per piece at most.",
            )
            for hit in triads
        )
    return found


CONTRAST_RX: Final = _rx(r", not (?!only\b|just\b)|\brather than\b|\binstead of\b")


def check_contrast_budget(masked: str) -> list[Finding]:
    """One summary finding when reversed contrasts exceed Rock's own rate."""
    hits = CONTRAST_RX.findall(masked)
    total = _word_count(masked)
    if len(hits) < MIN_REPEAT or not total or 1000 * len(hits) / total <= CONTRAST_PER_1K:
        return []
    return [
        Finding(
            "A-CONTRAST-BUDGET",
            ADVISORY,
            1,
            f"{len(hits)} contrast constructions in {total} words",
            "Rock's typed mail runs about 1 per 1,000 words. Keep the one real contrast.",
        )
    ]


def check_vocab_density(masked: str) -> list[Finding]:
    found: list[Finding] = []
    for start, body in _paragraphs(masked):
        hits = sorted({m.group(0).lower() for m in TIER2.finditer(body)})
        if len(hits) >= MIN_REPEAT:
            found.append(
                Finding(
                    "A-TIER2-CLUSTER",
                    ADVISORY,
                    _line_of(masked, start),
                    ", ".join(hits),
                    "Two or more Tier 2 words in one paragraph.",
                )
            )
    total = _word_count(masked)
    tier3 = len(TIER3.findall(masked))
    if total and tier3 / total >= TIER3_DENSITY:
        found.append(
            Finding(
                "A-TIER3-DENSITY",
                ADVISORY,
                1,
                f"{tier3} of {total} words",
                "Vague praise words at 3% or more. Replace some with numbers.",
            )
        )
    return found


def check_cadence(masked: str, profile: str) -> list[Finding]:
    """Surface mechanical proxies for cadence tells.

    These are counts with quoted spans, never a grade. A script cannot judge
    whether a landing was earned. It can show the reader where short
    sentences cluster so the judgment takes seconds.
    """
    if profile == "technical":
        # Terse fragments are the correct register in docs (anti-ai-slop 230).
        return []
    found: list[Finding] = []
    lengths: list[int] = []
    closers: list[tuple[int, str]] = []
    eligible = 0
    for start, body in _paragraphs(masked):
        sentences = [s for s in _sentences(body) if _word_count(s)]
        if not sentences:
            continue
        line = _line_of(masked, start)
        counts = [_word_count(s) for s in sentences]
        lengths.extend(counts)
        found.extend(_fragment_runs(sentences, counts, line, profile))
        if len(sentences) >= (
            FORMAL_LONG_PARAGRAPH if profile == "formal" else LONG_PARAGRAPH_SENTENCES
        ):
            found.append(
                Finding(
                    "A-LONG-PARAGRAPH",
                    ADVISORY,
                    line,
                    f"{len(sentences)} sentences in one paragraph",
                    "Rock's median paragraph is one sentence. Split at four.",
                )
            )
        if len(sentences) >= MIN_REPEAT:
            eligible += 1
            if counts[-1] <= SHORT_CLOSER_WORDS and profile != "email":
                closers.append((line, sentences[-1]))
            if CLOSER_ANTITHESIS_RX.search(sentences[-1]):
                found.append(
                    Finding(
                        "A-ANTITHESIS-REVERSED",
                        ADVISORY,
                        line,
                        sentences[-1],
                        "Paragraph lands on rather than or instead of.",
                    )
                )
        is_label = counts[0] <= TOPIC_LABEL_WORDS and sentences[0].endswith(".")
        if is_label and len(sentences) >= MIN_REPEAT and profile != "email":
            found.append(
                Finding(
                    "A-TOPIC-LABEL",
                    ADVISORY,
                    line,
                    sentences[0],
                    "Possible topic label opener. Open with the claim.",
                )
            )
    # Reported only when short closers are the majority shape, because one
    # short landing is what coffee-peer-voice says a piece can earn.
    if len(closers) >= MIN_REPEAT and len(closers) * 2 > eligible:
        found.extend(
            Finding(
                "A-SHORT-CLOSER",
                ADVISORY,
                line,
                sentence,
                f"{len(closers)} of {eligible} paragraphs end on a short "
                "sentence. Keep the one the content earned.",
            )
            for line, sentence in closers
        )
    if profile != "formal":
        found.extend(_smoothness(lengths))
    if len(lengths) >= UNIFORM_MIN_SENTENCES:
        mid = sum(1 for n in lengths if n in UNIFORM_BAND)
        if mid * 2 > len(lengths):
            found.append(
                Finding(
                    "A-UNIFORM",
                    ADVISORY,
                    1,
                    f"{mid} of {len(lengths)} sentences run 15 to 25 words",
                    "Uniform sentence length. Vary the clause count.",
                )
            )
    return found


def _smoothness(lengths: list[int]) -> list[Finding]:
    """Flag a draft that reads smoother than Rock's measured cadence."""
    found: list[Finding] = []
    if len(lengths) >= SMOOTH_MIN_SENTENCES:
        mean = sum(lengths) / len(lengths)
        if mean > SMOOTH_MEAN_WORDS:
            found.append(
                Finding(
                    "A-SMOOTH",
                    ADVISORY,
                    1,
                    f"average sentence is {mean:.0f} words",
                    "Rock's typed mail averages 12. Shorten or split the long ones.",
                )
            )
    if len(lengths) >= SHORT_SHARE_MIN_SENTENCES:
        share = sum(1 for n in lengths if n <= REACTION_WORDS) / len(lengths)
        if share < SHORT_SHARE_FLOOR:
            found.append(
                Finding(
                    "A-SMOOTH",
                    ADVISORY,
                    1,
                    f"{share:.0%} of sentences run five words or fewer",
                    "About 27% of Rock's do. Let a short complete sentence react.",
                )
            )
    return found


def _fragment_runs(
    sentences: list[str], counts: list[int], line: int, profile: str
) -> list[Finding]:
    found: list[Finding] = []
    run: list[str] = []
    # The trailing sentinel is one word too long to join a run, so it flushes
    # a run that reaches the end of the paragraph. No zip(strict=...) here:
    # that keyword does not exist on Python 3.9.
    for index, count in enumerate([*counts, SHORT_SENTENCE_WORDS + 1]):
        if count <= SHORT_SENTENCE_WORDS:
            run.append(sentences[index])
            continue
        if len(run) >= (EMAIL_FRAGMENT_RUN if profile == "email" else MIN_REPEAT):
            found.append(
                Finding(
                    "A-FRAGMENT-RUN",
                    ADVISORY,
                    line,
                    " ".join(run),
                    f"{len(run)} short sentences in a row. Rejoin them with "
                    "the causal link stated.",
                )
            )
        run = []
    return found


def check_closers(masked: str) -> list[Finding]:
    """Flag a message that ends on motive narration or an invented gate.

    Reads only the last CLOSER_SENTENCES sentences of the last prose
    paragraph, after sign-off lines are dropped. Earlier in a message the
    same phrases can open a real update, so they are left alone there.
    """
    for paragraph in reversed(list(_paragraphs(masked))):
        sentences = [s for s in _sentences(paragraph[1]) if _word_count(s)]
        while sentences and SIGN_OFF_RX.match(sentences[-1]):
            sentences.pop()
        if sentences:
            line = _line_of(masked, paragraph[0])
            break
    else:
        return []
    found: list[Finding] = []
    for sentence in sentences[-CLOSER_SENTENCES:]:
        motive = CLOSER_MOTIVE_RX.search(sentence)
        if motive and not CLOSER_FACT_RX.match(sentence, motive.end()):
            found.append(
                Finding(
                    "H-CLOSER-MOTIVE",
                    HARD,
                    line,
                    sentence,
                    "Closing line narrates why the message was sent. "
                    "End on the last fact or on what you're doing next.",
                )
            )
        if CLOSER_GATE_RX.search(sentence):
            found.append(
                Finding(
                    "A-CLOSER-GATE",
                    ADVISORY,
                    line,
                    sentence,
                    "Closing ask adds a review step. Keep it only if the writer "
                    "asked for that gate, and name what they're waiting on.",
                )
            )
    return found


# ---------------------------------------------------------------------------
# 1.6.0 checks. Each one is a count or a co-occurrence with a quoted span,
# never a grade, per the third maintainer note in coffee-peer-voice.
# ---------------------------------------------------------------------------

# Register 2026-10-19: "no false conversation starters." Rock's posts end on
# a question about 1 time in 100 (voice guide). A comment that ends on a
# roadmap question to the named author is his move and passes, because the
# generic forms below never start with a name.
ENGAGEMENT_HARD_RX: Final = _rx(
    r"^(?:thoughts|agree|agree or disagree|what do you think|what say you"
    r"|who's with me|am I wrong|sound off|discuss)\?{1,3}$"
    r"|\blet me know in the comments\b|\bdrop (?:a|your) (?:comment|thoughts)\b"
    r"|\bcomment below\b|\bin the comments\b"
)
ENGAGEMENT_SOFT_RX: Final = re.compile(
    r"^(?:What's|What is|What was|How do|How does|How are|Have you|Who else"
    r"|Which|Where do|When did|What would)\b[^?]{0,160}\b(?:you|your)\b[^?]{0,80}\?$"
)
ASK_RX: Final = re.compile(
    r"\?$|^(?:Can|Could|Would|Will) (?:you|we)\b|^Please\b|\bplease\b", re.IGNORECASE
)
LIST_LINE_RX: Final = re.compile(r"^[ \t]*(?:\d{1,2}[.)]|[-*+•]) ", re.MULTILINE)
URL_OR_DOMAIN_RX: Final = re.compile(
    r"https?://|\bwww\.|\b[\w-]{2,40}\.(?:com|org|io|ai|net|gov|edu|dev|co)\b"
)
# Noun sense only: "reports to the CFO" is a verb and passes.
REPORT_RX: Final = _rx(
    r"\b(?:the|a|an|their|its|his|her|our|my|new|latest|this|that|[\w-]{1,30}'s)"
    r" (?:[\w-]{1,20} ){0,2}(?:report|paper|study|survey|preprint|whitepaper)s?\b"
)
# Code identifiers in a LinkedIn or X comment (register 2026-10-26:
# "nobody includes a fucking file name in a li comment").
CODE_TOKEN_RX: Final = re.compile(
    r"\b[\w-]{1,60}\.(?:py|js|ts|tsx|json|ya?ml|toml|go|rs|java|rb|sh|ipynb)\b"
    r"|\b[a-z][a-z0-9]{1,30}(?:_[a-z0-9]{1,30}){1,6}\b|\b[A-Za-z_]{2,40}\(\)"
)
INITIAL_CONJ_RX: Final = re.compile(r"^(?:And|But|Or|Yet|Nor)\b")
# Synonym cycling (anti-ai-slop catalog; register 2026-10-04 rotated tries,
# attempts, and runs for one unit). A group fires when three distinct members
# appear in one draft. Determiners keep the verb senses ("he tries") out.
SYNONYM_GROUPS: Final = (
    re.compile(
        r"\b(?:the|a|an|one|each|every|per|of|those|these|its|their|\d{1,6}|n)"
        r" (attempts?|tries|try|trials?|runs?)\b",
        re.IGNORECASE,
    ),
    _rx(r"\b(developers?|engineers?|practitioners?|builders?|coders?|programmers?)\b"),
    _rx(r"\b(vendors?|providers?|suppliers?|partners?)\b"),
    _rx(r"\b(tools?|platforms?|solutions?|products?)\b"),
)
# Acronyms in posts for a broad audience get spelled out on first use
# (register 2026-10-30 IoCs, IAM, SSO; 2026-10-11 TOC; 2026-10-09 EMA;
# 2026-10-04 ASR). The allowlist holds the terms Rock's readers already know.
# Caps emphasis is Rock's ("attribution is HARD," "BEFORE EXECUTION"), so a
# common English word in caps, or a caps word next to another, never counts.
ACRONYM_RX: Final = re.compile(r"\b[A-Z][A-Za-z]{0,1}[A-Z]{1,4}s?\b")
ACRONYM_ALLOW: Final = frozenset(
    "AI ML LLM LLMs GPT CEO CFO CTO CIO CISO CISOs COO CPO CRO VP SVP EVP US UK EU"
    " API APIs URL URLs PDF PDFs IT OT OK PR PRs FAQ HR SaaS AWS NSA CISA FBI NIST"
    " ISO OWASP RSA RSAC SOC SOCs CVE CVEs MFA VPN DNS SQL HTTP HTTPS SDK CLI GPU"
    " CPU RAM USB TV DM DMs AM PM ET PT MT UTC Q1 Q2 Q3 Q4 FY TLDR TL DR BS FUD"
    " SLA SLAs MBA".split()
)
CAPS_WORDS: Final = frozenset(
    "IS BE IN ON AT TO DO NO SO OR WE ME MY THE AND BUT NOT ALL ANY YOU OUR ONE TWO"
    " NOW NEW BIG BAD WHY HOW WHO YES WOW OMG HARD DONE LAST THAT THIS THEY WILL"
    " MUST NEVER EVER ONLY VERY MORE MOST STOP WAIT WHAT WHEN SWEET SHORT FIRST"
    " AFTER CLOUD REAL TRUE HELL DAMN HYPE SLOP FREE STILL EVERY BEFORE SAME"
    " ITS HIS HER ARE WAS HAS HAD CAN DID GOT GET OUT OFF UP".split()
)
DATE_RX: Final = re.compile(
    r"\b(?:19|20)\d{2}s?\b|\b(?:January|February|March|April|June|July|August"
    r"|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept?"
    r"|Oct|Nov|Dec)\b|\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday"
    r"|Sunday)\b|\b(?:last|this|next) (?:week|month|quarter|year|spring|summer"
    r"|fall|winter)\b|\byesterday\b|\bQ[1-4]\b|\b(?:\d{1,3}|a few|two|three"
    r"|several) (?:years|months|weeks|decades) ago\b|\bdecades?\b"
)
FIRST_PERSON_RX: Final = re.compile(
    r"\bI(?:'m|'ve|'d|'ll)?\b|\b(?:[Mm]y|me|[Ww]e|[Oo]ur|[Ww]e've|[Ww]e're|us)\b"
)
EVIDENCE_RX: Final = re.compile(
    r"\d|\baccording to\b|\b[A-Z][\w&.-]{1,30} (?:said|says|found|reported|wrote"
    r"|published|told|shows|showed)\b"
)
ROUTE_RX: Final = _rx(
    r"\b(?:link|download|sign up|subscribe|register|join|reply|repo|github"
    r"|available (?:on|at|from)|reach out|book a|grab (?:a|the))\b"
)
ROADMAP_SOFT_RX: Final = _rx(
    r"\b(?:we'll|I'll|we will|I will) (?:cover|explore|walk (?:you )?through"
    r"|look at|break down|go over|discuss|examine|dig into|unpack)\b"
    r"|\b(?:this|the) (?:post|article|guide|piece|issue) (?:covers|explores"
    r"|walks|looks at|breaks down)\b"
    r"|\bhere(?:'s| is) (?:what|how) (?:we'll|you'll|I'll|to)\b"
    r"|\bhere are the (?:three|four|five|six|seven|\d{1,2})\b"
)
RECAP_SOFT_RX: Final = re.compile(
    r"^(?:Ultimately|In the end|At the end of the day|Long story short"
    r"|The lesson|The takeaway|So the lesson|The point is|The real lesson)\b"
)
LEGACY_TERMS_RX: Final = _rx(
    r"\b(?:legacy|traditional|outdated|old-school|antiquated|reactive|siloed"
    r"|fragmented|rigid|paper-based|the old way|yesterday's)\b"
)
MODERN_TERMS_RX: Final = _rx(
    r"\b(?:modern|proactive|integrated|unified|next-gen(?:eration)?|ai-powered"
    r"|ai-driven|intelligent|real-time|cloud-native|agile|the new way)\b"
)
STOPWORDS: Final = frozenset(
    "this that with from have they them their there what when where which while"
    " your yours about into over under than then also just only more most some"
    " such very will would could should because been being were does doing done"
    " each every other these those here every after before again still even much"
    " many like make made want need know think really thing things".split()
)


def _head(word: str) -> str:
    """Singular head noun for synonym groups ("tries" and "try" are one head)."""
    low = word.lower()
    if low in ("tries", "try"):
        return "try"
    return low[:-1] if low.endswith("s") and len(low) > 3 else low


def _stem(word: str) -> str:
    for suffix in ("ing", "ed", "es", "ly", "s"):
        if len(word) > len(suffix) + 3 and word.endswith(suffix):
            return word[: -len(suffix)]
    return word


def _content_words(text: str) -> set[str]:
    return {
        _stem(w.lower())
        for w in WORD_RX.findall(text)
        if len(w) >= 4 and w.lower() not in STOPWORDS and not w.isdigit()
    }


def _prose_paragraphs(masked: str) -> list[tuple[int, list[str]]]:
    """(line, sentences) for each prose paragraph that has words."""
    out: list[tuple[int, list[str]]] = []
    for start, body in _paragraphs(masked):
        sentences = [s for s in _sentences(body) if _word_count(s)]
        if sentences:
            out.append((_line_of(masked, start), sentences))
    return out


def _last_sentence(masked: str) -> tuple[int, str] | None:
    for line, sentences in reversed(_prose_paragraphs(masked)):
        while sentences and SIGN_OFF_RX.match(sentences[-1]):
            sentences.pop()
        if sentences:
            return line, sentences[-1]
    return None


def check_message_rules(original: str, masked: str, profile: str) -> list[Finding]:
    """Register rules that need the whole message, not one span."""
    found: list[Finding] = []
    paragraphs = _prose_paragraphs(masked)
    total = _word_count(masked)

    cap = {"email": EMAIL_WORD_CAP, "social": SOCIAL_WORD_CAP}.get(profile)
    if cap and total > cap:
        found.append(
            Finding(
                "A-LENGTH",
                ADVISORY,
                1,
                f"{total} words",
                f"Over the {cap}-word read for this channel. Cut to the asks and the facts.",
            )
        )

    if profile == "email":
        asks = [s for _, ss in paragraphs for s in ss if ASK_RX.search(s)]
        if len(asks) >= ASKS_FOR_LIST and not LIST_LINE_RX.search(original):
            found.append(
                Finding(
                    "A-ASKS-UNLISTED",
                    ADVISORY,
                    paragraphs[0][0],
                    f"{len(asks)} asks in prose",
                    "Three or more separate asks get a numbered list, point first.",
                )
            )

    if profile in ("email", "social", "blog", "formal"):
        for line, sentences in paragraphs:
            for sentence in sentences:
                if INITIAL_CONJ_RX.match(sentence):
                    found.append(
                        Finding(
                            "A-INITIAL-CONJ",
                            ADVISORY,
                            line,
                            sentence[:80],
                            "Rock opens under 0.3% of sentences with And, But, or Or. "
                            "Join it to the sentence before. 'So' is his and passes.",
                        )
                    )

    if profile in ("social", "blog", "formal"):
        found.extend(_acronyms(masked))

    if profile == "social":
        tail = _last_sentence(masked)
        if tail:
            line, sentence = tail
            if ENGAGEMENT_HARD_RX.search(sentence):
                found.append(
                    Finding(
                        "H-ENGAGEMENT-BAIT",
                        HARD,
                        line,
                        sentence,
                        "Engagement prompt. End on the last real point or where to get the thing.",
                    )
                )
            elif ENGAGEMENT_SOFT_RX.search(sentence):
                found.append(
                    Finding(
                        "A-CLOSING-QUESTION",
                        ADVISORY,
                        line,
                        sentence,
                        "Generic closing question. His posts end on one 1 time in 100. "
                        "A roadmap question to the named author is fine.",
                    )
                )
        if REPORT_RX.search(masked) and not URL_OR_DOMAIN_RX.search(original):
            found.append(
                Finding(
                    "A-REPORT-NO-LINK",
                    ADVISORY,
                    1,
                    "mentions a report, paper, or study with no link",
                    "A post that mentions a report carries its link. A comment carries "
                    "none unless Rock adds one.",
                )
            )
        for hit in CODE_TOKEN_RX.finditer(masked):
            found.append(
                Finding(
                    "A-CODE-IN-SOCIAL",
                    ADVISORY,
                    _line_of(masked, hit.start()),
                    hit.group(0),
                    "Code identifier in a social post. Say what it does in plain words.",
                )
            )

    if profile != "technical":
        for group in SYNONYM_GROUPS:
            heads = {_head(m.group(1)) for m in group.finditer(masked)}
            if len(heads) >= 3:
                found.append(
                    Finding(
                        "A-SYNONYM-CYCLE",
                        ADVISORY,
                        1,
                        ", ".join(sorted(heads)),
                        "Synonym cycling. Once a term is defined, use that term every time.",
                    )
                )
    return found


def _acronyms(masked: str) -> list[Finding]:
    found: list[Finding] = []
    seen: set[str] = set()
    for hit in ACRONYM_RX.finditer(masked):
        token = hit.group(0)
        base = token[:-1] if token.endswith("s") and token[:-1].isupper() else token
        if base in seen or base in ACRONYM_ALLOW or token in ACRONYM_ALLOW:
            continue
        if base.upper() in CAPS_WORDS:
            continue
        before = masked[max(0, hit.start() - 2) : hit.start()]
        after = masked[hit.end() : hit.end() + 2]
        if re.search(r"[A-Z]{2}\s?$", before) or re.match(r"\s?[A-Z]{2}", after):
            continue  # a run of caps is emphasis, not an acronym
        if before.endswith("-") or after.startswith("-"):
            continue  # part of an identifier such as A-SHAPE-RECAP or COVID-19
        seen.add(base)
        if f"({base})" in masked or f"({token})" in masked or f"{token} (" in masked:
            continue
        found.append(
            Finding(
                "A-ACRONYM",
                ADVISORY,
                _line_of(masked, hit.start()),
                token,
                "Spell out an acronym on first use for a broad audience: "
                "'Identity and Access Management (IAM)'.",
            )
        )
    return found


def check_shape(original: str, masked: str, profile: str) -> list[Finding]:
    """Proxies for the SlopShape core values that need position or absence.

    The regex rules above catch the explicit forms anywhere. These checks read
    where a thing sits (first paragraph, last paragraph) or what a draft of
    real length lacks entirely (a date, a first person, a route out).
    """
    if profile not in ("blog", "social", "formal"):
        return []
    found: list[Finding] = []
    paragraphs = _prose_paragraphs(masked)
    if not paragraphs:
        return found
    total = _word_count(masked)

    first_line, first = paragraphs[0]
    opening = " ".join(first)
    hit = ROADMAP_SOFT_RX.search(opening)
    if hit and len(paragraphs) >= 2:
        found.append(
            Finding(
                "A-SHAPE-ROADMAP",
                ADVISORY,
                first_line,
                _context(opening, hit.start(), hit.end()),
                f"Opening announces the flow (SlopShape thesis-first, gap {GAP_THESIS_FIRST}). "
                "Start on the news or the claim.",
            )
        )

    last_line, last = paragraphs[-1]
    if len(paragraphs) >= 2 and RECAP_SOFT_RX.match(last[0]):
        found.append(
            Finding(
                "A-SHAPE-RECAP",
                ADVISORY,
                last_line,
                last[0][:100],
                f"Closing paragraph opens as a recap (SlopShape restated thesis, gap "
                f"{GAP_RESTATED_THESIS}). End on a new point or the next step.",
            )
        )

    if len(paragraphs) >= RESTATE_MIN_PARAGRAPHS and total >= SHAPE_MIN_WORDS // 2:
        head, tail = _content_words(opening), _content_words(" ".join(last))
        shared = head & tail
        union = head | tail
        if (
            union
            and len(shared) >= RESTATE_MIN_SHARED
            and len(shared) / len(union) >= RESTATE_JACCARD
        ):
            found.append(
                Finding(
                    "A-SHAPE-RESTATE",
                    ADVISORY,
                    last_line,
                    f"closing shares {len(shared)} content words with the opening: "
                    + ", ".join(sorted(shared)[:8]),
                    f"Closing restates the opening (SlopShape gap {GAP_RESTATED_THESIS}, "
                    "the largest in the paper). End somewhere the opening did not go.",
                )
            )

    for line, sentences in paragraphs:
        body = " ".join(sentences)
        legacy, modern = LEGACY_TERMS_RX.search(body), MODERN_TERMS_RX.search(body)
        if legacy and modern:
            found.append(
                Finding(
                    "A-SHAPE-LEGACY",
                    ADVISORY,
                    line,
                    f"{legacy.group(0)} ... {modern.group(0)}",
                    f"Legacy-versus-modern contrast (SlopShape gap {GAP_LEGACY_MODERN}). "
                    "Describe what the reader runs today and what broke, with a date.",
                )
            )

    if total >= SHAPE_MIN_WORDS:
        if not DATE_RX.search(masked):
            found.append(
                Finding(
                    "A-SHAPE-NODATE",
                    ADVISORY,
                    1,
                    f"no date or period in {total} words",
                    f"Human posts carry historical dates and periods (SlopShape gap "
                    f"{GAP_HISTORICAL_DATE}). Date the event, the report, or the change.",
                )
            )
        if (
            profile != "formal"
            and not FIRST_PERSON_RX.search(masked)
            and not (EVIDENCE_RX.search(masked) or URL_OR_DOMAIN_RX.search(original))
        ):
            found.append(
                Finding(
                    "A-SHAPE-INSTITUTIONAL",
                    ADVISORY,
                    1,
                    f"no first person, number, or named source in {total} words",
                    f"Confident institutional voice (SlopShape gap {GAP_INSTITUTIONAL}). "
                    "Credibility comes from what Rock did, a named source, or a number.",
                )
            )
        if profile == "blog" and not (URL_OR_DOMAIN_RX.search(original) or ROUTE_RX.search(masked)):
            found.append(
                Finding(
                    "A-SHAPE-NOROUTE",
                    ADVISORY,
                    1,
                    "no link or route beyond the post",
                    f"Human posts route the reader out to a resource (SlopShape gap "
                    f"{GAP_NO_ROUTE}). Link the primary source or say where to get it.",
                )
            )
    return found


def check_uniformity(masked: str, profile: str) -> list[Finding]:
    """Sentence-length burstiness and paragraph skeleton sameness."""
    if profile == "technical":
        return []
    found: list[Finding] = []
    paragraphs = _prose_paragraphs(masked)
    lengths = [_word_count(s) for _, ss in paragraphs for s in ss]
    if len(lengths) >= BURSTINESS_MIN_SENTENCES:
        mean = sum(lengths) / len(lengths)
        sd = (sum((n - mean) ** 2 for n in lengths) / len(lengths)) ** 0.5
        cv = sd / mean if mean else 0.0
        if cv < BURSTINESS_CV_FLOOR:
            found.append(
                Finding(
                    "A-BURSTINESS",
                    ADVISORY,
                    1,
                    f"sentence-length variation {cv:.2f} over {len(lengths)} sentences",
                    "Rock's samples run 0.34 to 0.68. Let some sentences run 2 to 5 "
                    "words and some past 25, from clause count.",
                )
            )
    if len(paragraphs) >= PARA_UNIFORM_MIN_PARAGRAPHS:
        counts = [len(ss) for _, ss in paragraphs]
        words = [sum(_word_count(s) for s in ss) for _, ss in paragraphs]
        mean_w = sum(words) / len(words)
        sd_w = (sum((n - mean_w) ** 2 for n in words) / len(words)) ** 0.5
        same_count = max(counts) - min(counts) <= 1 and min(counts) >= PARA_UNIFORM_MIN_SENTENCES
        if same_count or (mean_w and sd_w / mean_w < PARA_UNIFORM_WORD_CV):
            found.append(
                Finding(
                    "A-PARA-UNIFORM",
                    ADVISORY,
                    paragraphs[0][0],
                    f"{len(paragraphs)} paragraphs of {min(counts)} to {max(counts)} "
                    f"sentences, {min(words)} to {max(words)} words",
                    "Same skeleton every paragraph. Give one a single sentence and let "
                    "another run long.",
                )
            )
    return found


# Rule families that make up the paper's "tidy, self-announcing" post.
SHAPE_FAMILIES: Final = {
    "H-SHAPE-ROADMAP": "thesis-first roadmap",
    "A-SHAPE-ROADMAP": "thesis-first roadmap",
    "H-SHAPE-RECAP": "recap ending",
    "A-SHAPE-RECAP": "recap ending",
    "A-SHAPE-RESTATE": "recap ending",
    "H-SHAPE-ERA": "legacy-versus-modern framing",
    "A-SHAPE-LEGACY": "legacy-versus-modern framing",
    "A-SHAPE-NEXTGEN": "legacy-versus-modern framing",
    "A-SHAPE-INSTITUTIONAL": "institutional voice",
    "A-SHAPE-NODATE": "no historical date",
    "A-SHAPE-NOROUTE": "no route out",
}


def check_modal_shape(found: list[Finding]) -> list[Finding]:
    families = sorted({SHAPE_FAMILIES[f.rule] for f in found if f.rule in SHAPE_FAMILIES})
    if len(families) < MODAL_MIN_FAMILIES:
        return []
    return [
        Finding(
            "A-SHAPE-MODAL",
            ADVISORY,
            1,
            ", ".join(families),
            f"{len(families)} AI-leaning shape families in one draft. This is the "
            "modal AI configuration in SlopShape. Rebuild the skeleton, not the words.",
        )
    ]


def lint(text: str, profile: str = "blog", include_quotes: bool = False) -> list[Finding]:
    """Return every finding for `text`, ordered by line."""
    if profile not in PROFILES:
        raise ValueError(f"unknown profile: {profile}")
    masked = mask(text, include_quotes)
    found = check_rules(text, masked, profile)
    found.extend(check_open_asks(text))
    if profile != "casual":
        # Casual catches fingerprints and chatbot artifacts only, so typos
        # and loose habits in Slack survive (anti-ai-slop line 232).
        checks: tuple[Callable[[], list[Finding]], ...] = (
            lambda: check_layout(text, masked, profile),
            lambda: check_vocab_density(masked),
            lambda: check_cadence(masked, profile),
            lambda: check_contrast_budget(masked),
            lambda: check_closers(masked),
            lambda: check_message_rules(text, masked, profile),
            lambda: check_shape(text, masked, profile),
            lambda: check_uniformity(masked, profile),
        )
        for check in checks:
            found.extend(check())
        found.extend(check_modal_shape(found))
    return sorted(set(found), key=lambda f: (f.line, f.severity, f.rule, f.span))


def render(findings: list[Finding], profile: str) -> str:
    out = [f"slop_lint {VERSION} profile={profile}"]
    for severity in (HARD, ADVISORY, OPEN_ASK):
        group = [f for f in findings if f.severity == severity]
        out.append(f"\n{severity}: {len(group)}")
        out.extend(f'  L{f.line} [{f.rule}] "{f.span}"\n      {f.message}' for f in group)
    return "\n".join(out)


def _read(path: str | None) -> str:
    if path is None or path == "-":
        raw = sys.stdin.buffer.read(MAX_BYTES + 1)
    else:
        with open(path, "rb") as handle:
            raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError(f"input exceeds {MAX_BYTES} bytes")
    return raw.decode("utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="slop_lint", description="Flag mechanical AI writing tells."
    )
    parser.add_argument("path", nargs="?", help="draft file, or - for stdin")
    parser.add_argument("--profile", choices=PROFILES, default="blog")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument(
        "--include-quotes",
        action="store_true",
        help="also lint blockquotes and double-quoted strings",
    )
    parser.add_argument(
        "--advisory-only",
        action="store_true",
        help="report everything and always exit 0",
    )
    parser.add_argument("--version", action="version", version=VERSION)
    args = parser.parse_args(argv)

    if os.environ.get(DISABLE_ENV) == "1":
        print(f"slop_lint disabled by {DISABLE_ENV}=1", file=sys.stderr)
        return 0
    try:
        text = _read(args.path)
    except (OSError, ValueError) as error:
        print(f"slop_lint: {error}", file=sys.stderr)
        return EXIT_USAGE

    try:
        findings = lint(text, args.profile, args.include_quotes)
    except Exception as error:  # noqa: BLE001 - error boundary: report, never crash
        print(f"slop_lint: internal error, check did not run: {error!r}", file=sys.stderr)
        return EXIT_INTERNAL
    if args.json:
        payload = {
            "version": VERSION,
            "owner": OWNER,
            "profile": args.profile,
            "findings": [asdict(f) for f in findings],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(render(findings, args.profile))
    hard = any(f.severity == HARD for f in findings)
    return 1 if hard and not args.advisory_only else 0


if __name__ == "__main__":
    sys.exit(main())
