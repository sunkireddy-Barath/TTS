import React, { useState } from 'react'
import { Loader2 } from 'lucide-react'
import { type AppVersion } from '../constants'
import { generateVoiceClone } from '../api'
import LanguageSelector from '../components/LanguageSelector'
import EmotionPicker from '../components/EmotionPicker'
import GenderAgePicker from '../components/GenderAgePicker'
import ExpressionPicker from '../components/ExpressionPicker'
import AudioPlayer from '../components/AudioPlayer'
import AudioUploader from '../components/AudioUploader'
import VersionSwitcher from '../components/VersionSwitcher'

const VoiceClonePage: React.FC = () => {
  const [version, setVersion]           = useState<AppVersion>(1)
  const [referenceAudio, setReferenceAudio] = useState<File | null>(null)
  const [refText, setRefText]           = useState('')
  const [text, setText]                 = useState('')
  const [targetLanguage, setTargetLanguage] = useState('ta')
  const [gender, setGender]             = useState('neutral')
  const [age, setAge]                   = useState(30)
  const [emotion, setEmotion]           = useState('neutral')
  const [expression, setExpression]     = useState('none')

  const [loading, setLoading]           = useState(false)
  const [error, setError]               = useState<string | null>(null)
  const [audioBlob, setAudioBlob]       = useState<Blob | null>(null)

  const charCount = text.length
  const maxChars  = 3000

  // When version changes reset incompatible fields and audio
  const handleVersionChange = (v: AppVersion) => {
    setVersion(v)
    setAudioBlob(null)
    setError(null)
    if (v === 1) setExpression('none') // V1 has no expressions
  }

  const handleGenerate = async () => {
    if (!text.trim())    { setError('Please enter target text.'); return }
    if (!referenceAudio) { setError('Please upload a reference voice audio.'); return }
    setError(null)
    setLoading(true)
    setAudioBlob(null)

    // V1 never sends an expression (spec requirement)
    const effectiveExpression = version === 1 ? 'none' : expression

    try {
      const blob = await generateVoiceClone({
        text,
        target_language: targetLanguage,
        reference_audio: referenceAudio,
        gender,
        age,
        emotion,
        expression: effectiveExpression,
        version,
        ref_text: refText,
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
            style={{ background: 'linear-gradient(135deg, #ec4899, #8b5cf6)' }}
          >
            <span className="text-white font-bold text-xl">VC</span>
          </div>
          <h1 className="font-display text-3xl font-bold text-gradient">
            Cross-Lingual Voice Cloning
          </h1>
        </div>
        <p className="text-slate-400 ml-[52px] text-sm">
          Clone any speaker's voice and make it speak in any of 100+ languages.
          Upload a reference recording, pick a target language, and generate.
        </p>
      </div>

      {/* ── How it works strip ── */}
      <div className="glass-card p-4 mb-6">
        <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
          {[
            { n: '1', label: 'Upload reference voice' },
            { n: '2', label: 'Enter target text' },
            { n: '3', label: 'Choose target language' },
          ].map(({ n, label }, idx, arr) => (
            <React.Fragment key={n}>
              <div className="flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-brand-600/30 text-brand-400 flex items-center justify-center font-bold text-xs flex-shrink-0">
                  {n}
                </span>
                {label}
              </div>
              {idx < arr.length - 1 && (
                <span className="text-slate-600 hidden sm:block mx-2">--&gt;</span>
              )}
            </React.Fragment>
          ))}
          <span className="text-slate-600 hidden sm:block mx-2">--&gt;</span>
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded-full bg-emerald-600/30 text-emerald-400 flex items-center justify-center font-bold text-xs flex-shrink-0">
              OK
            Same voice · New language
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-[1fr_380px] gap-8">

        {/* ── Left: main form ── */}
        <div className="space-y-5">

          {/* Reference audio upload */}
          <div className="glass-card p-5">
            <AudioUploader value={referenceAudio} onChange={setReferenceAudio} />
          </div>

          {/* Optional: reference audio transcription */}
          <div className="glass-card p-5">
            <div className="flex items-center justify-between mb-2">
              <label htmlFor="ref-text" className="field-label mb-0">
                Reference Audio Transcript
                <span className="ml-2 text-xs font-normal text-slate-500">(optional)</span>
              </label>
            </div>
            <textarea
              id="ref-text"
              className="field-input resize-none"
              rows={2}
              placeholder="Type what the person says in the reference audio… Leave blank and VoiceX will auto-transcribe via Whisper."
              value={refText}
              maxLength={500}
              onChange={(e) => setRefText(e.target.value)}
            />
            <div className="mt-1 flex items-start gap-2 text-xs text-slate-500">
              <span className="mt-0.5 flex-shrink-0 text-emerald-400 font-bold">i</span>
              <span>
                Providing the transcript improves cloning accuracy.
                If left blank, VoiceX uses Whisper ASR to auto-transcribe.
              </span>
            </div>
          </div>

          {/* Target text */}
          <div className="glass-card p-5">
            <div className="flex items-center justify-between mb-2">
              <label htmlFor="clone-text" className="field-label mb-0">
                {version === 3 ? 'Target Text (with Emotion Tags)' : 'Target Text'}
              </label>
              <span
                className={`text-xs ${charCount > maxChars * 0.9 ? 'text-amber-400' : 'text-slate-600'}`}
              >
                {charCount} / {maxChars}
              </span>
            </div>
            <textarea
              id="clone-text"
              className="field-input resize-none"
              rows={version === 3 ? 12 : 5}
              placeholder={
                version === 3
                  ? 'Write text with emotion tags for per-sentence control:\n\n<happy>\nI won the match today!\n</happy>\n\n<sad>\nBut my friend wasn\'t there to celebrate.\n</sad>\n\n<excited>\nWe play again tomorrow!\n</excited>\n\nSupported: <happy> <sad> <angry> <excited> <calm> <whisper>'
                  : 'Type the text you want the cloned voice to speak in the target language…'
              }
              value={text}
              maxLength={maxChars}
              onChange={(e) => setText(e.target.value)}
            />
            
            {version === 3 ? (
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
                  <span className="mt-0.5 flex-shrink-0 text-accent-400 font-bold">i</span>
                  <div>
                    <span className="text-slate-400">Expression tags (write directly in text):</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {['[laughter]', '[sigh]', '[confirmation-en]', '[question-en]', '[question-ah]', '[question-oh]', '[question-ei]', '[question-yi]', '[surprise-ah]', '[surprise-oh]', '[surprise-wa]', '[surprise-yo]', '[dissatisfaction-hnn]'].map((tag) => (
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
            ) : (
              <div className="mt-2 flex items-start gap-2 text-xs text-slate-500">
                <span className="mt-0.5 flex-shrink-0 text-brand-400 font-bold">i</span>
                <span>
                  Example — Tamil:{' '}
                  <span className="text-slate-300 select-all">வணக்கம் நண்பர்களே</span>.
                  {' '}Write in the target language script for the most natural output.
                </span>
              </div>
            )}
          </div>

          {/* Target language */}
          <div className="glass-card p-5">
            <LanguageSelector
              value={targetLanguage}
              onChange={setTargetLanguage}
              id="clone-target-language"
            />
          </div>

          {/* Gender + Age */}
          <div className="glass-card p-5">
            <GenderAgePicker
              gender={gender}
              age={age}
              onGenderChange={setGender}
              onAgeChange={setAge}
              disabledGender={true}
            />
          </div>

          {/* Emotion — shown for V1 and V2 (V3 uses tags in text) */}
          {version !== 3 && (
            <div className="glass-card p-5">
              <EmotionPicker value={emotion} onChange={setEmotion} />
            </div>
          )}

          {/* Expression — V2 only */}
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
            id="generate-voice-clone"
            type="button"
            disabled={loading || !text.trim() || !referenceAudio}
            onClick={handleGenerate}
            className="btn-primary w-full py-4 text-base"
            style={{
              background: loading
                ? undefined
                : 'linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%)',
              boxShadow: '0 4px 20px rgba(236,72,153,0.35)',
            }}
          >
            {loading ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Cloning Voice…
              </>
            ) : (
              <>
                Clone &amp; Generate
              </>
            )}
          </button>

          {/* Audio player */}
          {audioBlob && (
            <AudioPlayer
              audioBlob={audioBlob}
              fileName={`voice_clone_${targetLanguage}.wav`}
            />
          )}
        </div>

        {/* ── Right: settings panel ── */}
        <aside className="space-y-5">

          {/* Version switcher */}
          <div className="glass-card p-5">
            <p className="field-label mb-3">Mode</p>
            <VersionSwitcher version={version} onChange={handleVersionChange} />
            <div className="mt-3 text-xs text-slate-500">
              {version === 1 && <p>Basic clone with emotion control. No expressions.</p>}
              {version === 2 && <p>Adds expression injection — tags appended silently before inference.</p>}
              {version === 3 && <p>Advanced: emotion tags in text are stripped before cloning for clean output.</p>}
            </div>
          </div>

          {/* Summary */}
          <div className="glass-card p-5 space-y-3">
            <p className="field-label">Current Settings</p>
            {(
              [
                ['Reference',        referenceAudio?.name ?? 'Not uploaded'],
                ['Target Language',  targetLanguage],
                ['Gender',           gender],
                ['Age',              String(age)],
                ['Emotion',          emotion],
                ...(version === 2 ? [['Expression', expression]] as [string, string][] : []),
                ['Mode',             `Version ${version}`],
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
                <span className="text-pink-400 mt-0.5">-</span>
                <span>Use a clear, noise-free reference audio for best results.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-pink-400 mt-0.5">-</span>
                <span>5–30 seconds of reference audio works best.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-pink-400 mt-0.5">-</span>
                <span>Native-script text produces the most natural phonetics.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-pink-400 mt-0.5">-</span>
                <span>Age and gender hints help shape the vocal style.</span>
              </li>
              {version === 2 && (
                <li className="flex items-start gap-2">
                  <span className="text-accent-400 mt-0.5">-</span>
                  <span>Expression adds a vocal flair — tag is appended silently by the backend.</span>
                </li>
              )}
            </ul>
          </div>

        </aside>
      </div>
    </main>
  )
}

export default VoiceClonePage
