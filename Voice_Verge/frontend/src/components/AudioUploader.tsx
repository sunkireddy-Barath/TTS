import React, { useCallback, useRef, useState, useEffect } from 'react'
import { Upload, X, Mic } from 'lucide-react'

interface AudioUploaderProps {
  value: File | null
  onChange: (file: File | null) => void
}

const AudioUploader: React.FC<AudioUploaderProps> = ({ value, onChange }) => {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)

  useEffect(() => {
    if (value) {
      const url = URL.createObjectURL(value)
      setAudioUrl(url)
      return () => URL.revokeObjectURL(url)
    } else {
      setAudioUrl(null)
    }
  }, [value])

  const handleFile = (file: File) => {
    const allowed = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/ogg', 'audio/flac']
    if (!allowed.includes(file.type) && !file.name.match(/\.(wav|mp3|ogg|flac|m4a)$/i)) {
      alert('Please upload a WAV, MP3, OGG, or FLAC audio file.')
      return
    }
    onChange(file)
  }

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      setDragging(false)
      const file = e.dataTransfer.files[0]
      if (file) handleFile(file)
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  )

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  return (
    <div>
      <label className="field-label flex items-center gap-1.5">
        <Mic size={11} className="text-brand-400" />
        Reference Voice Audio
      </label>

      {value ? (
        /* File selected state */
        <div className="flex flex-col p-4 rounded-xl border border-brand-500/40 bg-brand-500/8 gap-3">
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
              style={{ background: 'linear-gradient(135deg, #3b64f8, #8b5cf6)' }}
            >
              <Mic size={18} className="text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{value.name}</p>
              <p className="text-xs text-slate-500">
                {(value.size / 1024).toFixed(1)} KB · {value.type || 'audio'}
              </p>
            </div>
            <button
              id="remove-reference-audio"
              type="button"
              onClick={() => onChange(null)}
              className="w-8 h-8 rounded-lg bg-white/6 hover:bg-red-500/20 flex items-center justify-center
                         transition-colors text-slate-400 hover:text-red-400 flex-shrink-0"
            >
              <X size={14} />
            </button>
          </div>
          
          {audioUrl && (
            <div className="w-full">
              <audio controls src={audioUrl} className="w-full h-8" />
            </div>
          )}
        </div>
      ) : (
        /* Drop zone */
        <div
          id="audio-drop-zone"
          className={`
            relative flex flex-col items-center justify-center gap-3 p-8 rounded-xl cursor-pointer
            border-2 border-dashed transition-all duration-200
            ${dragging
              ? 'border-brand-500 bg-brand-500/10'
              : 'border-white/10 bg-white/3 hover:border-brand-500/50 hover:bg-white/5'
            }
          `}
          onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <div
            className="w-14 h-14 rounded-2xl flex items-center justify-center"
            style={{
              background: dragging
                ? 'linear-gradient(135deg, #3b64f8, #8b5cf6)'
                : 'rgba(255,255,255,0.06)',
            }}
          >
            <Upload size={24} className={dragging ? 'text-white' : 'text-slate-500'} />
          </div>
          <div className="text-center">
            <p className="text-sm font-medium text-slate-300">
              Drop reference audio here
            </p>
            <p className="text-xs text-slate-500 mt-1">
              WAV · MP3 · OGG · FLAC — up to 50 MB
            </p>
          </div>
          <span className="btn-secondary text-xs px-4 py-2">
            Browse Files
          </span>

          <input
            ref={inputRef}
            type="file"
            accept="audio/*"
            className="hidden"
            onChange={handleChange}
          />
        </div>
      )}
    </div>
  )
}

export default AudioUploader
