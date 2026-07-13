"""
tag_parser.py
Parses Version-3 advanced emotion tag markup from user text.

Supported tags:
    <happy> … </happy>
    <sad>   … </sad>
    <angry> … </angry>
    <excited> … </excited>
    <calm>  … </calm>
    <whisper> … </whisper>

Output: list of TextSegment objects, each carrying its own emotion.
"""

import re
from dataclasses import dataclass
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


@dataclass
class TextSegment:
    """A single segment of text with its associated emotion."""
    text: str
    emotion: str = "neutral"


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
        Converts inline expressions like <giggle> or [giggle] into their 
        mapped OmniVoice tokens (e.g. [laughter]).
        """
        for expr, tag in EXPRESSION_TAG_MAP.items():
            if not tag:
                continue
            
            # Allow users to type either <question_ah> or <question-ah>
            expr_pattern = expr.replace("_", "[-_]")
            
            # Convert <giggle> -> [laughter] with spaces but NO COMMAS.
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
        segment with the default_emotion. Expression tags are converted to OmniVoice native tags.

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

        # IMPORTANT STABILITY FIX:
        # 1. Tags MUST be in their own segment with "neutral" emotion. If they share a segment
        #    with extreme pitch (like "high pitch" for happy), the vocoder crashes into static.
        # 2. Tags MUST have at least one spoken phoneme in their segment. If they are alone,
        #    the model generates a silent breath. We solve this by injecting a natural "anchor word".
        
        anchor_map = {
            "[laughter]": "ha ha",
            "[sigh]": "ah",
            "[surprise-ah]": "oh",
            "[surprise-oh]": "oh",
            "[surprise-wa]": "wa",
            "[surprise-yo]": "yo",
            "[question-en]": "hmm",
            "[question-ah]": "ah",
            "[question-oh]": "oh",
            "[question-ei]": "ei",
            "[question-yi]": "yi",
            "[dissatisfaction-hnn]": "ugh",
            "[confirmation-en]": "mhm",
        }
        
        final_segments: List[TextSegment] = []
        expr_re = re.compile(r"(\[[a-z-]+\])")
        
        for seg in segments:
            if not seg.text.strip():
                continue
                
            parts = expr_re.split(seg.text)
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                if expr_re.match(part):
                    # It's an expression tag. Inject anchor phonemes and force neutral emotion.
                    anchor = anchor_map.get(part, "ah")
                    anchored_text = f"{anchor} {part}"
                    final_segments.append(TextSegment(text=anchored_text, emotion="neutral"))
                else:
                    # Normal text. Keep original emotion.
                    final_segments.append(TextSegment(text=part, emotion=seg.emotion))

        return final_segments

    @staticmethod
    def has_tags(text: str) -> bool:
        """Return True if *text* contains at least one emotion tag or expression tag."""
        if bool(_TAG_RE.search(text)):
            return True
        for expr, tag in EXPRESSION_TAG_MAP.items():
            if not tag: continue
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
            if not tag: continue
            expr_pattern = expr.replace("_", "[-_]")
            result = re.sub(rf"<{expr_pattern}>", "", result, flags=re.IGNORECASE)
            result = re.sub(rf"\[{expr_pattern}\]", "", result, flags=re.IGNORECASE)
            
        result = re.sub(r"\s+", " ", result).strip()
        return result
