// ─── Language catalogue types & data ────────────────────────────────────────
export interface LanguageOption {
  value: string
  label: string
}

export interface LanguageGroup {
  group: string
  languages: LanguageOption[]
}

export const LANGUAGE_GROUPS: LanguageGroup[] = [
  {
    group: 'English Accents',
    languages: [
      { value: 'en-US', label: 'American English' },
      { value: 'en-GB', label: 'British English' },
      { value: 'en-AU', label: 'Australian English' },
      { value: 'en-IN', label: 'Indian English' },
      { value: 'en-CA', label: 'Canadian English' },
      { value: 'en-NZ', label: 'New Zealand English' },
      { value: 'en-ZA', label: 'South African English' },
      { value: 'en-IE', label: 'Irish English' },
      { value: 'en-SG', label: 'Singaporean English' },
      { value: 'en-NG', label: 'Nigerian English' },
    ],
  },
  {
    group: 'Indian Languages',
    languages: [
      { value: 'ta',  label: 'Tamil' },
      { value: 'te',  label: 'Telugu' },
      { value: 'hi',  label: 'Hindi' },
      { value: 'ml',  label: 'Malayalam' },
      { value: 'kn',  label: 'Kannada' },
      { value: 'bn',  label: 'Bengali' },
      { value: 'mr',  label: 'Marathi' },
      { value: 'gu',  label: 'Gujarati' },
      { value: 'pa',  label: 'Punjabi' },
      { value: 'or',  label: 'Odia' },
      { value: 'as',  label: 'Assamese' },
      { value: 'sa',  label: 'Sanskrit' },
      { value: 'ne',  label: 'Nepali' },
      { value: 'ur',  label: 'Urdu' },
      { value: 'ks',  label: 'Kashmiri' },
      { value: 'sd',  label: 'Sindhi' },
      { value: 'mai', label: 'Maithili' },
      { value: 'doi', label: 'Dogri' },
      { value: 'kok', label: 'Konkani' },
      { value: 'mni', label: 'Meitei (Manipuri)' },
      { value: 'sat', label: 'Santali' },
      { value: 'bho', label: 'Bhojpuri' },
    ],
  },
  {
    group: 'Foreign Languages',
    languages: [
      { value: 'es',    label: 'Spanish' },
      { value: 'es-MX', label: 'Mexican Spanish' },
      { value: 'fr',    label: 'French' },
      { value: 'fr-CA', label: 'Canadian French' },
      { value: 'de',    label: 'German' },
      { value: 'it',    label: 'Italian' },
      { value: 'pt',    label: 'Portuguese' },
      { value: 'pt-BR', label: 'Brazilian Portuguese' },
      { value: 'nl',    label: 'Dutch' },
      { value: 'pl',    label: 'Polish' },
      { value: 'ru',    label: 'Russian' },
      { value: 'uk',    label: 'Ukrainian' },
      { value: 'cs',    label: 'Czech' },
      { value: 'sk',    label: 'Slovak' },
      { value: 'sv',    label: 'Swedish' },
      { value: 'da',    label: 'Danish' },
      { value: 'no',    label: 'Norwegian' },
      { value: 'fi',    label: 'Finnish' },
      { value: 'hu',    label: 'Hungarian' },
      { value: 'ro',    label: 'Romanian' },
      { value: 'el',    label: 'Greek' },
      { value: 'tr',    label: 'Turkish' },
      { value: 'bg',    label: 'Bulgarian' },
      { value: 'hr',    label: 'Croatian' },
      { value: 'sr',    label: 'Serbian' },
      { value: 'sl',    label: 'Slovenian' },
      { value: 'et',    label: 'Estonian' },
      { value: 'lv',    label: 'Latvian' },
      { value: 'lt',    label: 'Lithuanian' },
      { value: 'ca',    label: 'Catalan' },
      { value: 'gl',    label: 'Galician' },
      { value: 'eu',    label: 'Basque' },
      { value: 'is',    label: 'Icelandic' },
      { value: 'lb',    label: 'Luxembourgish' },
      { value: 'mt',    label: 'Maltese' },
      { value: 'cy',    label: 'Welsh' },
      { value: 'ga',    label: 'Irish' },
      { value: 'sq',    label: 'Albanian' },
      { value: 'mk',    label: 'Macedonian' },
      { value: 'bs',    label: 'Bosnian' },
      { value: 'zh-CN', label: 'Mandarin Chinese (Simplified)' },
      { value: 'zh-TW', label: 'Mandarin Chinese (Traditional)' },
      { value: 'yue',   label: 'Cantonese' },
      { value: 'ja',    label: 'Japanese' },
      { value: 'ko',    label: 'Korean' },
      { value: 'vi',    label: 'Vietnamese' },
      { value: 'th',    label: 'Thai' },
      { value: 'my',    label: 'Burmese' },
      { value: 'km',    label: 'Khmer' },
      { value: 'lo',    label: 'Lao' },
      { value: 'mn',    label: 'Mongolian' },
      { value: 'bo',    label: 'Tibetan' },
      { value: 'id',    label: 'Indonesian' },
      { value: 'ms',    label: 'Malay' },
      { value: 'tl',    label: 'Filipino (Tagalog)' },
      { value: 'jv',    label: 'Javanese' },
      { value: 'su',    label: 'Sundanese' },
      { value: 'ceb',   label: 'Cebuano' },
      { value: 'ar',    label: 'Arabic (Modern Standard)' },
      { value: 'ar-EG', label: 'Arabic (Egyptian)' },
      { value: 'ar-SA', label: 'Arabic (Gulf)' },
      { value: 'he',    label: 'Hebrew' },
      { value: 'fa',    label: 'Persian (Farsi)' },
      { value: 'ps',    label: 'Pashto' },
      { value: 'ku',    label: 'Kurdish' },
      { value: 'az',    label: 'Azerbaijani' },
      { value: 'kk',    label: 'Kazakh' },
      { value: 'ky',    label: 'Kyrgyz' },
      { value: 'uz',    label: 'Uzbek' },
      { value: 'tk',    label: 'Turkmen' },
      { value: 'tg',    label: 'Tajik' },
      { value: 'hy',    label: 'Armenian' },
      { value: 'ka',    label: 'Georgian' },
      { value: 'sw',    label: 'Swahili' },
      { value: 'am',    label: 'Amharic' },
      { value: 'ha',    label: 'Hausa' },
      { value: 'yo',    label: 'Yoruba' },
      { value: 'ig',    label: 'Igbo' },
      { value: 'zu',    label: 'Zulu' },
      { value: 'xh',    label: 'Xhosa' },
      { value: 'st',    label: 'Sotho' },
      { value: 'sn',    label: 'Shona' },
      { value: 'so',    label: 'Somali' },
      { value: 'rw',    label: 'Kinyarwanda' },
      { value: 'mg',    label: 'Malagasy' },
      { value: 'si',    label: 'Sinhala' },
      { value: 'dz',    label: 'Dzongkha' },
      { value: 'mi',    label: 'Māori' },
      { value: 'haw',   label: 'Hawaiian' },
      { value: 'sm',    label: 'Samoan' },
    ],
  },
]

// ─── Emotion options ─────────────────────────────────────────────────────────
export interface EmotionOption {
  value: string
  label: string
  emoji: string
  color: string
}

export const EMOTIONS: EmotionOption[] = [
  { value: 'neutral',    label: 'Neutral',    emoji: '😐', color: '#64748b' },
  { value: 'happy',      label: 'Happy',      emoji: '😊', color: '#eab308' },
  { value: 'excited',    label: 'Excited',    emoji: '🤩', color: '#f97316' },
  { value: 'sad',        label: 'Sad',        emoji: '😢', color: '#3b82f6' },
  { value: 'angry',      label: 'Angry',      emoji: '😠', color: '#ef4444' },
  { value: 'calm',       label: 'Calm',       emoji: '😌', color: '#10b981' },
  { value: 'whisper',    label: 'Whisper',    emoji: '🤫', color: '#8b5cf6' },
  { value: 'fearful',    label: 'Fearful',    emoji: '😨', color: '#6366f1' },
  { value: 'surprised',  label: 'Surprised',  emoji: '😲', color: '#ec4899' },
  { value: 'disgusted',  label: 'Disgusted',  emoji: '🤢', color: '#84cc16' },
]

// ─── Expression options (v2) ──────────────────────────────────────────────────
export interface ExpressionOption {
  value: string
  label: string
}

export const EXPRESSIONS: ExpressionOption[] = [
  { value: 'none',            label: 'None' },
  { value: 'giggle',          label: 'Giggle' },
  { value: 'laughter',        label: 'Laughter' },
  { value: 'sigh',            label: 'Sigh' },
  { value: 'question',        label: 'Question' },
  { value: 'question_en',     label: 'Question (en)' },
  { value: 'question_ah',     label: 'Question (ah)' },
  { value: 'question_oh',     label: 'Question (oh)' },
  { value: 'question_ei',     label: 'Question (ei)' },
  { value: 'question_yi',     label: 'Question (yi)' },
  { value: 'surprise',        label: 'Surprise' },
  { value: 'surprise_ah',     label: 'Surprise (ah)' },
  { value: 'surprise_oh',     label: 'Surprise (oh)' },
  { value: 'surprise_wa',     label: 'Surprise (wa)' },
  { value: 'surprise_yo',     label: 'Surprise (yo)' },
  { value: 'dissatisfaction', label: 'Dissatisfaction' },
  { value: 'confirmation',    label: 'Confirmation' },
]

// ─── Gender options ───────────────────────────────────────────────────────────
export interface GenderOption {
  value: string
  label: string
  icon: string
}

export const GENDERS: GenderOption[] = [
  { value: 'male',    label: 'Male',    icon: '♂' },
  { value: 'female',  label: 'Female',  icon: '♀' },
  { value: 'neutral', label: 'Neutral', icon: '⚬' },
]

// ─── App version ──────────────────────────────────────────────────────────────
export type AppVersion = 1 | 2 | 3

// ─── API base URL ──────────────────────────────────────────────────────────────
export const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'
