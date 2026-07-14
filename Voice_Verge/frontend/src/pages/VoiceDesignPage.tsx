import React, { useState } from 'react'
import { Loader2 } from 'lucide-react'
import { type AppVersion } from '../constants'
import { generateVoiceDesign } from '../api'
import LanguageSelector from '../components/LanguageSelector'
import EmotionPicker from '../components/EmotionPicker'
import GenderAgePicker from '../components/GenderAgePicker'
import ExpressionPicker from '../components/ExpressionPicker'
import AudioPlayer from '../components/AudioPlayer'
import VersionSwitcher from '../components/VersionSwitcher'

// Version 3 placeholder showing supported emotion tags
const V3_PLACEHOLDER = `Write text with emotion tags for per-sentence control:

<happy>
I won the match today!
</happy>

<sad>
But my friend wasn't there to celebrate.
</sad>

<excited>
We play again tomorrow!
</excited>

Supported: <happy> <sad> <angry> <excited> <calm> <whisper>`

// Version 3 supported expression tag reference shown inline
const V3_EXPRESSION_TAGS = [
  '[laughter]', '[sigh]', '[confirmation-en]',
  '[question-en]', '[question-ah]', '[question-oh]', '[question-ei]', '[question-yi]',
  '[surprise-ah]', '[surprise-oh]', '[surprise-wa]', '[surprise-yo]',
  '[dissatisfaction-hnn]',
]

const VoiceDesignPage: React.FC = () => {
  const [version, setVersion]     = useState<AppVersion>(1)
  const [text, setText]           = useState('')
  const [language, setLanguage]   = useState('en-US')
  const [gender, setGender]       = useState('neutral')
  const [age, setAge]             = useState(30)
  const [emotion, setEmotion]     = useState('neutral')
  const [expression, setExpression] = useState('none')

  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState<string | null>(null)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)

  const charCount = text.length
  const maxChars  = 3000

  // When version changes reset incompatible fields
  const handleVersionChange = (v: AppVersion) => {
    setVersion(v)
    setAudioBlob(null)
    setError(null)
    if (v === 1) setExpression('none') // V1 has no expressions
  }

  const handleGenerate = async () => {
    if (!text.trim()) { setError('Please enter some text.'); return }
    setError(null)
    setLoading(true)
    setAudioBlob(null)

    // For V1 force expression to 'none' (spec: V1 has no expression support)
    const effectiveExpression = version === 1 ? 'none' : expression

    try {
      const blob = await generateVoiceDesign({
        text,
        language,
        gender,
        age,
        emotion,
        expression: effectiveExpression,
        version,
      })
      setAudioBlob(blob)
    } catch (err: unknown) {
      setError(
        (err instanceof Error ? err.message : null) ??
        'Generation failed. Make sure the backend is running.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="w-full min-h-[calc(100vh-64px)] px-6 lg:px-12 py-10 animate-fade-in">

      {/* ── Page header ── */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{ background: 'linear-gradient(135deg, #3b64f8, #8b5cf6)' }}
          >
            <span className="text-white font-bold text-xl">VD</span>
          </div>
          <h1 className="font-display text-3xl font-bold text-gradient">
            Voice Design
          </h1>
        </div>
        <p className="text-slate-400 ml-[52px] text-sm">
          Generate natural human speech from text using AI-powered voice design.
          Control language, gender, age, and emotion.
        </p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-[1fr_380px] gap-8">

        {/* ── Left: main form ── */}
        <div className="space-y-5">

          {/* Text input */}
          <div className="glass-card p-5">
            <div className="flex items-center justify-between mb-2">
              <label htmlFor="voice-design-text" className="field-label mb-0">
                {version === 3 ? 'Text with Emotion Tags' : 'Text to Speak'}
              </label>
              <span
                className={`text-xs ${charCount > maxChars * 0.9 ? 'text-amber-400' : 'text-slate-600'}`}
              >
                {charCount} / {maxChars}
              </span>
            </div>
            <textarea
              id="voice-design-text"
              className="field-input resize-none"
              rows={version === 3 ? 12 : 6}
              placeholder={
                version === 3
                  ? V3_PLACEHOLDER
                  : 'Type or paste the text you want to convert to speech…'
              }
              value={text}
              maxLength={maxChars}
              onChange={(e) => setText(e.target.value)}
            />

            {/* V3 helper: emotion tag hint */}
            {version === 3 && (
              <div className="mt-3 space-y-2">
                <div className="flex items-start gap-2 text-xs text-slate-500">
                  <span className="mt-0.5 flex-shrink-0 text-brand-400 font-bold">i</span>
                  <span>
                    Emotion tags: wrap each section in{' '}
                    <code className="text-accent-400 bg-accent-500/10 px-1 rounded">&lt;emotion&gt;…&lt;/emotion&gt;</code>.
                    Supported: <span className="text-slate-300">happy · sad · angry · excited · calm · whisper</span>
                  </span>
                </div>
                <div className="flex items-start gap-2 text-xs text-slate-500">
                  <span className="mt-0.5 flex-shrink-0 text-accent-400 font-bold">&lt;/&gt;</span>
                  <div>
                    <span className="text-slate-400">Expression tags (write directly in text):</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {V3_EXPRESSION_TAGS.map((tag) => (
                        <code
                          key={tag}
                          className="text-xs bg-white/5 border border-white/8 text-emerald-400 px-1.5 py-0.5 rounded"
                        >
                          {tag}
                        </code>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Language */}
          <div className="glass-card p-5">
            <LanguageSelector
              value={language}
              onChange={setLanguage}
              id="voice-design-language"
            />
          </div>

          {/* Gender + Age */}
          <div className="glass-card p-5">
            <GenderAgePicker
              gender={gender}
              age={age}
              onGenderChange={setGender}
              onAgeChange={setAge}
            />
          </div>

          {/* Emotion (hidden in V3 — user writes tags directly) */}
          {version !== 3 && (
            <div className="glass-card p-5">
              <EmotionPicker value={emotion} onChange={setEmotion} />
            </div>
          )}

          {/* Expression — V2 only (V1 has none, V3 user writes tags) */}
          {version === 2 && (
            <div className="glass-card p-5 animate-slide-up">
              <ExpressionPicker value={expression} onChange={setExpression} />
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="flex items-start gap-3 p-4 rounded-xl border border-red-500/30 bg-red-500/10 animate-slide-up">
              <span className="text-red-400 mt-0.5 flex-shrink-0 font-bold">!</span>
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}

          {/* Generate button */}
          <button
            id="generate-voice-design"
            type="button"
            disabled={loading || !text.trim()}
            onClick={handleGenerate}
            className="btn-primary w-full py-4 text-base"
          >
            {loading ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Generating Speech…
              </>
            ) : (
              <>
                Generate Speech
              </>
            )}
          </button>

          {/* Audio player */}
          {audioBlob && (
            <AudioPlayer audioBlob={audioBlob} fileName={`voice_design_${language}.wav`} />
          )}
        </div>

        {/* ── Right: settings panel ── */}
        <aside className="space-y-5">

          {/* Version switcher */}
          <div className="glass-card p-5">
            <p className="field-label mb-3">Mode</p>
            <VersionSwitcher version={version} onChange={handleVersionChange} />
            <div className="mt-3 space-y-1 text-xs text-slate-500">
              {version === 1 && (
                <p>Basic voice design with emotion control. No expressions.</p>
              )}
              {version === 2 && (
                <p>Adds Expression dropdown — Giggle, Sigh, Question, Surprise, etc. Tags injected silently on backend.</p>
              )}
              {version === 3 && (
                <p>Advanced mode — write emotion tags and expression tags directly in your text. Full manual control.</p>
              )}
            </div>
          </div>

          {/* Summary card */}
          <div className="glass-card p-5 space-y-3">
            <p className="field-label">Current Settings</p>
            {(
              [
                ['Language',   language],
                ['Gender',     gender],
                ['Age',        String(age)],
                ...(version !== 3 ? [['Emotion', emotion]] as [string, string][] : []),
                ...(version === 2 ? [['Expression', expression]] as [string, string][] : []),
                ['Mode',       `Version ${version}`],
              ] as [string, string][]
            ).map(([k, v]) => (
              <div key={k} className="flex justify-between text-xs gap-2">
                <span className="text-slate-500 flex-shrink-0">{k}</span>
                <span className="text-slate-200 font-medium capitalize truncate text-right">{v}</span>
              </div>
            ))}
          </div>

          {/* Tips */}
          <div className="glass-card p-5">
            <p className="field-label mb-3">Quick Tips</p>
            <ul className="space-y-2 text-xs text-slate-400">
              <li className="flex items-start gap-2">
                <span className="text-brand-400 mt-0.5">-</span>
                <span>Use punctuation for natural pauses and intonation.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-brand-400 mt-0.5">-</span>
                <span>Shorter texts generate faster. Split long content into sections.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-brand-400 mt-0.5">-</span>
                <span>Try different age values for character variety.</span>
              </li>
              {version === 2 && (
                <li className="flex items-start gap-2">
                  <span className="text-accent-400 mt-0.5">-</span>
                  <span>Pick an Expression to add natural vocal flair — tags are injected automatically.</span>
                </li>
              )}
              {version === 3 && (
                <li className="flex items-start gap-2">
                  <span className="text-accent-400 mt-0.5">-</span>
                  <span>Wrap sentences in emotion tags for per-sentence emotion control and mixed audio.</span>
                </li>
              )}
            </ul>
          </div>

        </aside>
      </div>
    </main>
  )
}

export default VoiceDesignPage
