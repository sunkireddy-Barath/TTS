"""
tag_parser.py
Parses Version-3 advanced emotion tag markup from user text.

Supported emotion tags (V3 inline):
    <happy> … </happy>
    <sad>   … </sad>
    <angry> … </angry>
    <excited> … </excited>
    <calm>  … </calm>
    <whisper> … </whisper>
    <neutral> … </neutral>
    <fearful> … </fearful>
    <surprised> … </surprised>
    <disgusted> … </disgusted>

Supported expression inline tags (V3 inline, converted to OmniVoice tokens):
    <laugh> / <giggle> / <laughter>  → [laughter]
    <sigh>                           → [sigh]
    <surprise> / <gasp>              → [surprise-ah]
    <question>                       → [question-en]
    <dissatisfaction>                → [dissatisfaction-hnn]
    <confirmation>                   → [confirmation-en]

Output: list of TextSegment objects, each carrying its own emotion and
        an `is_expression_segment` flag so callers can choose a clean instruct.
"""

import re
from dataclasses import dataclass, field
from typing import List

from expression_engine import EXPRESSION_TAG_MAP


SUPPORTED_EMOTIONS = {
    "happy", "sad", "angry", "excited", "calm", "whisper",
    "neutral", "fearful", "surprised", "disgusted",
}

# Regex that captures any <emotion> … </emotion> block
_TAG_RE = re.compile(
    r"<(?P<emotion>" + "|".join(SUPPORTED_EMOTIONS) + r")>"
    r"(?P<content>.*?)"
    r"</(?P=emotion)>",
    re.DOTALL | re.IGNORECASE,
)

# ── Expression-only segment detector ─────────────────────────────────────────
# Matches: optional anchor word(s) followed by a single [xxx-yyy] token.
# Examples:  "ha ha [laughter]"  "ah [sigh]"  "[laughter]"
_EXPR_ONLY_RE = re.compile(r'^\s*(?:[a-z][\w\s]*)?\[[a-z][a-z-]*\]\s*$', re.IGNORECASE)


def is_expression_only(text: str) -> bool:
    """Return True if *text* is purely an anchor word + one expression token."""
    return bool(_EXPR_ONLY_RE.match(text.strip()))


@dataclass
class TextSegment:
    """A single segment of text with its associated emotion."""
    text: str
    emotion: str = "neutral"
    is_expression_segment: bool = False  # True → caller should use gender-only instruct


class TagParser:
    """
    Parses emotion-tagged text and returns an ordered list of TextSegments.

    Usage
    -----
    segments = TagParser.parse("<happy>Great!</happy> But <sad>it ended.</sad>")
    # → [TextSegment("Great!", "happy"), TextSegment("But", "neutral"),
    #     TextSegment("it ended.", "sad")]
    """

    @staticmethod
    def _replace_inline_expressions(text: str) -> str:
        """
        Converts inline expression tags like <giggle>, <laugh>, [giggle] into
        their mapped OmniVoice tokens (e.g. [laughter]).

        This handles BOTH the standard EXPRESSION_TAG_MAP keys AND common
        user-friendly aliases so V3 text like "<laugh>ha</laugh>" works naturally.
        """
        # Extra user-friendly aliases not in the tag map
        EXTRA_ALIASES = {
            "laugh":          "[laughter]",
            "giggle":         "[laughter]",
            "laughter":       "[laughter]",
            "sigh":           "[sigh]",
            "gasp":           "[surprise-ah]",
            "surprise":       "[surprise-ah]",
            "surprised":      "[surprise-ah]",
            "question":       "[question-en]",
            "dissatisfaction":"[dissatisfaction-hnn]",
            "confirmation":   "[confirmation-en]",
        }

        # Merge with the canonical map (canonical takes precedence for mapped keys)
        combined = dict(EXTRA_ALIASES)
        for expr, tag in EXPRESSION_TAG_MAP.items():
            if tag:
                combined[expr] = tag

        for expr, tag in combined.items():
            if not tag:
                continue
            # Allow users to type either <question_ah> or <question-ah>
            expr_pattern = expr.replace("_", "[-_]")

            # Convert <giggle> → [laughter] with spaces but NO COMMAS.
            # Commas cause hard pauses which make the vocoder crash on non-speech sounds.
            text = re.sub(rf"<{expr_pattern}>", f" {tag} ", text, flags=re.IGNORECASE)
            text = re.sub(rf"\[{expr_pattern}\]", f" {tag} ", text, flags=re.IGNORECASE)

        # Remove double spaces.
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def parse(text: str, default_emotion: str = "neutral") -> List[TextSegment]:
        """
        Parse text containing optional emotion tags and inline expression tags.

        If no emotion tags are found, the entire text is returned as a single
        segment with the default_emotion. Expression tags are converted to OmniVoice
        native tokens.

        Parameters
        ----------
        text : str
            Raw user input (may or may not contain emotion tags).
        default_emotion : str
            The emotion to apply to text outside of emotion tags.

        Returns
        -------
        List[TextSegment]
            Ordered list of segments with emotions assigned.
            Each segment with is_expression_segment=True contains ONLY an
            anchor word + one OmniVoice expression token.
        """
        segments: List[TextSegment] = []
        cursor = 0

        # Pre-process inline expression tags before splitting emotions
        text = TagParser._replace_inline_expressions(text)

        for match in _TAG_RE.finditer(text):
            # Text before the tag → default_emotion
            before = text[cursor:match.start()].strip()
            if before:
                segments.append(TextSegment(text=before, emotion=default_emotion))

            emotion  = match.group("emotion").lower()
            content  = match.group("content").strip()
            if content:
                segments.append(TextSegment(text=content, emotion=emotion))

            cursor = match.end()

        # Remaining text after the last tag → default_emotion
        tail = text[cursor:].strip()
        if tail:
            segments.append(TextSegment(text=tail, emotion=default_emotion))

        # Fallback: no tags found
        if not segments:
            segments.append(TextSegment(text=text.strip(), emotion=default_emotion))

        # ── Expression Segment Isolation ─────────────────────────────────────
        # CRITICAL STABILITY RULES:
        # 1. Expression tokens MUST be in their own segment with neutral emotion
        #    AND gender-only instruct. Pitch hints (e.g. "high pitch") cause blank
        #    or noisy audio when mixed with [laughter] / [sigh] / [surprise-ah].
        # 2. Expression tokens MUST have at least one spoken phoneme (anchor word)
        #    before the token. Without it, the model generates silent breath.
        #
        # anchor_map: maps each token to its most natural-sounding anchor phoneme.
        anchor_map = {
            "[laughter]":           "ha ha",
            "[sigh]":               "ah",
            "[surprise-ah]":        "oh",
            "[surprise-oh]":        "oh",
            "[surprise-wa]":        "wa",
            "[surprise-yo]":        "yo",
            "[question-en]":        "hmm",
            "[question-ah]":        "ah",
            "[question-oh]":        "oh",
            "[question-ei]":        "ei",
            "[question-yi]":        "yi",
            "[dissatisfaction-hnn]":"ugh",
            "[confirmation-en]":    "mhm",
        }

        final_segments: List[TextSegment] = []
        expr_re = re.compile(r"(\[[a-z][a-z-]*\])")

        for seg in segments:
            if not seg.text.strip():
                continue

            parts = expr_re.split(seg.text)
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                if expr_re.match(part):
                    # ── Expression token ──────────────────────────────────────
                    # Always force:
                    #   emotion = "neutral"
                    #   is_expression_segment = True
                    #   text = anchor_word + [token]
                    anchor = anchor_map.get(part, "ah")
                    anchored_text = f"{anchor} {part}"
                    final_segments.append(TextSegment(
                        text=anchored_text,
                        emotion="neutral",
                        is_expression_segment=True,
                    ))
                else:
                    # ── Normal speech text ────────────────────────────────────
                    # STABILITY FIX: skip pure punctuation segments.
                    if not re.search(r'[\w\u0080-\uFFFF]', part):
                        continue
                    final_segments.append(TextSegment(
                        text=part,
                        emotion=seg.emotion,
                        is_expression_segment=False,
                    ))

        return final_segments

    @staticmethod
    def has_tags(text: str) -> bool:
        """Return True if *text* contains at least one emotion tag or expression tag."""
        if bool(_TAG_RE.search(text)):
            return True
        for expr, tag in EXPRESSION_TAG_MAP.items():
            if not tag:
                continue
            expr_pattern = expr.replace("_", "[-_]")
            if re.search(rf"<{expr_pattern}>", text, flags=re.IGNORECASE) or \
               re.search(rf"\[{expr_pattern}\]", text, flags=re.IGNORECASE):
                return True
        return False

    @staticmethod
    def strip_tags(text: str) -> str:
        """Remove all emotion tags from *text*, returning plain content."""
        result = _TAG_RE.sub(lambda m: m.group("content").strip(), text)
        return result.strip()

    @staticmethod
    def strip_all_tags(text: str) -> str:
        """Remove all emotion tags and expression tags from *text*."""
        result = _TAG_RE.sub(lambda m: m.group("content").strip(), text)

        for expr, tag in EXPRESSION_TAG_MAP.items():
            if not tag:
                continue
            expr_pattern = expr.replace("_", "[-_]")
            result = re.sub(rf"<{expr_pattern}>", "", result, flags=re.IGNORECASE)
            result = re.sub(rf"\[{expr_pattern}\]", "", result, flags=re.IGNORECASE)

        result = re.sub(r"\s+", " ", result).strip()
        return result
