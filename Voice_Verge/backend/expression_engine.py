"""
expression_engine.py

Maps user-facing Expression dropdown values to OmniVoice expression tags.

Expression map contains ONLY the tokens OmniVoice actually understands —
no extras, no approximations.

Injection rule
--------------
The tag is inserted immediately after EVERY emotion-punctuation symbol
in the text so that the non-verbal token fires at the exact moment the
punctuation marks a phrase/sentence boundary.  This works for all 100+
supported languages because each script's punctuation characters are
registered in SENTENCE_END_PUNCT and CLAUSE_PUNCT below.

If the text contains no punctuation at all the tag is appended at the end.
"""

import logging
from typing import Dict, List

logger = logging.getLogger("omnivoice_studio")


# ---------------------------------------------------------------------------
# Expression → OmniVoice tag map
# Exactly the tokens OmniVoice supports — nothing else.
# ---------------------------------------------------------------------------
EXPRESSION_TAG_MAP: Dict[str, str] = {
    "none":            "",
    "giggle":          "[laughter]",
    "laughter":        "[laughter]",
    "laugh":           "[laughter]",
    "sigh":            "[sigh]",
    "question":        "[question-en]",
    "question_en":     "[question-en]",
    "question_ah":     "[question-ah]",
    "question_oh":     "[question-oh]",
    "question_ei":     "[question-ei]",
    "question_yi":     "[question-yi]",
    "surprise":        "[surprise-ah]",
    "surprise_ah":     "[surprise-ah]",
    "surprise_oh":     "[surprise-oh]",
    "surprise_wa":     "[surprise-wa]",
    "surprise_yo":     "[surprise-yo]",
    "dissatisfaction": "[dissatisfaction-hnn]",
    "confirmation":    "[confirmation-en]",
}


# ---------------------------------------------------------------------------
# Punctuation registry — covers all 100+ language scripts in the registry.
#
# SENTENCE_END_PUNCT
#   Marks the end of a complete utterance — highest-priority injection point.
#   Scripts covered:
#     Latin/European      . ! ?
#     Devanagari          । ॥           Hindi, Marathi, Sanskrit, Nepali,
#                                       Konkani, Dogri, Maithili, Bodo
#     Urdu/Sindhi/Kashmiri ۔            (Arabic-script Urdu)
#     Arabic/Persian/     ؟             Arabic, Persian (Dari/Farsi), Pashto,
#     Pashto/Kurdish                    Northern & Central Kurdish
#     CJK                 。 ！ ？      Chinese (Mandarin/Cantonese), Japanese,
#                                       Korean (mixed-script formal text)
#     Tibetan             ། ༎           Standard Tibetan (Lhasa)
#     Ethiopic            ። ፡           Amharic, Tigrinya
#     Armenian            ։ ՜ ՞          Armenian
#     Khmer               ។ ៕           Khmer (Cambodian)
#     Myanmar             ။             Burmese (Myanmar)
#     Sinhala, Georgian,  .             these scripts use the Latin full stop
#     Hebrew, Greek,                    (already covered above)
#     Maltese, Breton,
#     Irish, Welsh, Basque,
#     Catalan, Galician,
#     Maori, Hawaiian,
#     Guarani, Quechua, etc.
#
# CLAUSE_PUNCT
#   Marks a phrase/clause boundary — used only when no SENTENCE_END_PUNCT
#   is present in the text.
#   Scripts covered:
#     Latin/European      , ; :
#     Arabic-script       ، ؛           Urdu, Arabic, Persian
#     CJK                 ， 、 ； ：   Chinese, Japanese
#     Armenian            ՝
#     Ethiopic            ፣ ፤ ፥
#     Tibetan             ་             tsek (inter-syllable, also clause-level)
#     Khmer               ៖
#     Myanmar             ၊
# ---------------------------------------------------------------------------

SENTENCE_END_PUNCT: frozenset = frozenset([
    # Latin / European (English, French, German, Spanish, Italian, Portuguese,
    # Polish, Dutch, Swedish, Norwegian, Danish, Finnish, Greek, Czech, Hungarian,
    # Romanian, Ukrainian, Bulgarian, Croatian, Serbian, Slovak, Slovenian,
    # Albanian, Macedonian, Lithuanian, Latvian, Estonian, Icelandic, Irish,
    # Welsh, Basque, Catalan, Galician, Luxembourgish, Maltese, Breton, Cornish,
    # Yiddish [in romanised form], Afrikaans, Swahili, Yoruba, Hausa, Zulu,
    # Xhosa, Shona, Wolof, Twi, Somali, Igbo, Maori, Hawaiian, Guarani,
    # Ayacucho Quechua, Haitian Creole, Belarusian, Tatar, Bashkir, Tajik,
    # Turkmen, Northern & Central Kurdish, Azerbaijani, Cebuano, Javanese, etc.)
    '.', '!', '?',

    # Devanagari (Hindi, Marathi, Sanskrit, Nepali, Konkani, Dogri, Maithili, Bodo)
    '।',   # U+0964  DEVANAGARI DANDA
    '॥',   # U+0965  DEVANAGARI DOUBLE DANDA

    # Urdu / Sindhi / Kashmiri (written in Arabic script)
    '۔',   # U+06D4  ARABIC FULL STOP

    # Arabic / Persian (Farsi, Dari) / Southern Pashto / Kurdish
    '؟',   # U+061F  ARABIC QUESTION MARK

    # CJK — Mandarin Chinese, Cantonese, Japanese, Korean
    '。',   # U+3002  IDEOGRAPHIC FULL STOP
    '！',   # U+FF01  FULLWIDTH EXCLAMATION MARK
    '？',   # U+FF1F  FULLWIDTH QUESTION MARK

    # Tibetan (Standard Tibetan / Lhasa dialect)
    '།',   # U+0F0D  TIBETAN MARK SHAD
    '༎',   # U+0F0E  TIBETAN MARK NYIS SHAD (double shad, end of section)

    # Ethiopic (Amharic, Tigrinya)
    '።',   # U+1362  ETHIOPIC FULL STOP
    '፡',   # U+1361  ETHIOPIC WORDSPACE (sentence boundary in some styles)

    # Armenian
    '։',   # U+0589  ARMENIAN FULL STOP
    '՜',   # U+055C  ARMENIAN EXCLAMATION MARK
    '՞',   # U+055E  ARMENIAN QUESTION MARK

    # Khmer (Cambodian)
    '។',   # U+17D4  KHMER FULL STOP
    '៕',   # U+17D5  KHMER SECTION SIGN (end of passage)

    # Myanmar / Burmese
    '။',   # U+104B  MYANMAR SIGN SECTION
])

CLAUSE_PUNCT: frozenset = frozenset([
    # Latin / European
    ',', ';', ':',

    # Arabic-script (Urdu, Arabic, Persian, Sindhi, Kashmiri)
    '،',   # U+060C  ARABIC COMMA
    '؛',   # U+061B  ARABIC SEMICOLON

    # CJK
    '，',   # U+FF0C  FULLWIDTH COMMA
    '、',   # U+3001  IDEOGRAPHIC COMMA (Japanese 読点)
    '；',   # U+FF1B  FULLWIDTH SEMICOLON
    '：',   # U+FF1A  FULLWIDTH COLON

    # Armenian
    '՝',   # U+055D  ARMENIAN COMMA

    # Ethiopic (Amharic, Tigrinya)
    '፣',   # U+1363  ETHIOPIC COMMA
    '፤',   # U+1364  ETHIOPIC SEMICOLON
    '፥',   # U+1365  ETHIOPIC COLON

    # Tibetan
    '་',   # U+0F0B  TIBETAN MARK INTERSYLLABIC TSHEG (clause boundary in verse)

    # Khmer
    '៖',   # U+17D6  KHMER COLON

    # Myanmar / Burmese
    '၊',   # U+104A  MYANMAR SIGN LITTLE SECTION (comma equivalent)
])

# All emotion-relevant punctuation in one set for quick membership testing
ALL_PUNCT: frozenset = SENTENCE_END_PUNCT | CLAUSE_PUNCT


# ---------------------------------------------------------------------------
# Display options for the Gradio / React frontend dropdown
# ---------------------------------------------------------------------------
EXPRESSION_DISPLAY_OPTIONS: List[Dict[str, str]] = [
    {"value": "none",            "label": "None"},
    {"value": "giggle",          "label": "Giggle"},
    {"value": "laughter",        "label": "Laughter"},
    {"value": "sigh",            "label": "Sigh"},
    {"value": "question",        "label": "Question"},
    {"value": "question_en",     "label": "Question (en)"},
    {"value": "question_ah",     "label": "Question (ah)"},
    {"value": "question_oh",     "label": "Question (oh)"},
    {"value": "question_ei",     "label": "Question (ei)"},
    {"value": "question_yi",     "label": "Question (yi)"},
    {"value": "surprise",        "label": "Surprise"},
    {"value": "surprise_ah",     "label": "Surprise (ah)"},
    {"value": "surprise_oh",     "label": "Surprise (oh)"},
    {"value": "surprise_wa",     "label": "Surprise (wa)"},
    {"value": "surprise_yo",     "label": "Surprise (yo)"},
    {"value": "dissatisfaction", "label": "Dissatisfaction"},
    {"value": "confirmation",    "label": "Confirmation"},
]


# ---------------------------------------------------------------------------
# ExpressionEngine
# ---------------------------------------------------------------------------
class ExpressionEngine:
    """
    Resolves an expression label to an OmniVoice tag and injects it into
    text after every emotion-punctuation symbol.

    Injection rules (applied in this priority order):
      1. Tag is inserted after EVERY sentence-ending punctuation character
         found in the text — so multi-sentence input gets the tag at each
         sentence boundary.
      2. If no sentence-ending punctuation exists, tag is inserted after
         every clause-boundary punctuation character instead.
      3. If no punctuation at all, the tag is appended to the end.

    This means the model hears the non-verbal token exactly where the
    punctuation marks a natural emotional inflection point, across all
    100+ supported language scripts.
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @staticmethod
    def get_tag(expression: str) -> str:
        """Return the OmniVoice tag string for the given expression label."""
        key = expression.lower().strip().replace(" ", "_").replace("-", "_")
        return EXPRESSION_TAG_MAP.get(key, "")

    @classmethod
    def inject_tag(cls, text: str, expression: str) -> str:
        """
        Insert the OmniVoice expression tag into *text* at every
        emotion-punctuation boundary for the active language script.

        Parameters
        ----------
        text        Raw user text — any script, any of the 100+ languages.
        expression  Value from EXPRESSION_DISPLAY_OPTIONS, e.g. "giggle".

        Returns
        -------
        Text with the tag inserted after each punctuation boundary,
        or the original text unchanged when expression is "none".
        """
        tag = cls.get_tag(expression)
        if not tag:
            return text

        text = text.strip()
        if not text:
            return text

        # Determine which punctuation tier is present in the text
        has_sentence_end = any(ch in SENTENCE_END_PUNCT for ch in text)
        has_clause       = any(ch in CLAUSE_PUNCT       for ch in text)

        if has_sentence_end:
            active_set = SENTENCE_END_PUNCT
        elif has_clause:
            active_set = CLAUSE_PUNCT
        else:
            # No punctuation — append tag to end
            return f"{text} {tag}"

        return cls._inject_after_all(text, active_set, tag)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _inject_after_all(text: str, punct_set: frozenset, tag: str) -> str:
        """
        Rebuild *text* inserting *tag* immediately after every character
        that is in *punct_set*.

        Spacing: one space before the tag, one space after — any existing
        whitespace immediately after the punctuation is collapsed to one
        space so we don't produce double-spaces.
        """
        result: List[str] = []
        i = 0
        while i < len(text):
            ch = text[i]
            result.append(ch)
            if ch in punct_set:
                # Skip any whitespace that already follows this punctuation
                j = i + 1
                while j < len(text) and text[j] == ' ':
                    j += 1
                # Insert tag, then continue from j (non-space char or end)
                result.append(f" {tag} ")
                i = j
            else:
                i += 1

        return "".join(result).strip()

    # ------------------------------------------------------------------
    # Frontend helpers
    # ------------------------------------------------------------------

    @staticmethod
    def available_expressions() -> List[Dict[str, str]]:
        """Return the ordered display options for the frontend dropdown."""
        return EXPRESSION_DISPLAY_OPTIONS
