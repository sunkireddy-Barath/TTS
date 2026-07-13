import React, { useRef, useState, useEffect } from 'react'
import { Download, Play, Pause, Volume2 } from 'lucide-react'

interface AudioPlayerProps {
  audioBlob: Blob | null
  fileName?: string
}

const AudioPlayer: React.FC<AudioPlayerProps> = ({
  audioBlob,
  fileName = 'speech.wav',
}) => {
  const audioRef     = useRef<HTMLAudioElement>(null)
  const [url, setUrl] = useState<string | null>(null)
  const [playing, setPlaying]   = useState(false)
  const [progress, setProgress] = useState(0)
  const [duration, setDuration] = useState(0)
  const [playbackRate, setPlaybackRate] = useState(1)

  // Update playback rate when it changes or when audio source changes
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.playbackRate = playbackRate
    }
  }, [playbackRate, url])

  // Create / revoke object URL whenever the blob changes
  useEffect(() => {
    if (!audioBlob) {
      setUrl(null)
      setPlaying(false)
      setProgress(0)
      setDuration(0)
      return
    }
    const objectUrl = URL.createObjectURL(audioBlob)
    setUrl(objectUrl)
    setPlaying(false)
    setProgress(0)
    setDuration(0)
    // Cleanup previous URL on unmount or blob change
    return () => URL.revokeObjectURL(objectUrl)
  }, [audioBlob])

  if (!audioBlob || !url) return null

  const togglePlay = () => {
    const audio = audioRef.current
    if (!audio) return
    if (playing) {
      audio.pause()
    } else {
      audio.play().catch(() => {/* autoplay policy: ignore */})
    }
    setPlaying((prev) => !prev)
  }

  const handleTimeUpdate = () => {
    const audio = audioRef.current
    if (!audio || !audio.duration || isNaN(audio.duration)) return
    setProgress((audio.currentTime / audio.duration) * 100)
  }

  const handleLoadedMetadata = () => {
    const audio = audioRef.current
    if (!audio) return
    setDuration(audio.duration ?? 0)
  }

  const handleEnded = () => {
    setPlaying(false)
    setProgress(0)
  }

  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    const audio = audioRef.current
    if (!audio || !audio.duration) return
    const rect  = e.currentTarget.getBoundingClientRect()
    const ratio = (e.clientX - rect.left) / rect.width
    audio.currentTime = Math.max(0, Math.min(ratio * audio.duration, audio.duration))
  }

  const formatTime = (s: number) => {
    if (!s || isNaN(s)) return '0:00'
    const m   = Math.floor(s / 60)
    const sec = Math.floor(s % 60)
    return `${m}:${sec.toString().padStart(2, '0')}`
  }

  const handleDownload = () => {
    const a    = document.createElement('a')
    a.href     = url
    a.download = fileName
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }

  return (
    <div className="glass-card p-5 animate-slide-up">
      <audio
        ref={audioRef}
        src={url}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={handleEnded}
        preload="metadata"
        className="hidden"
      />

      <div className="flex items-center gap-4">
        {/* Play / Pause */}
        <button
          id="audio-play-pause"
          type="button"
          onClick={togglePlay}
          aria-label={playing ? 'Pause' : 'Play'}
          className="flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center
                     transition-all duration-200 active:scale-90"
          style={{
            background:  'linear-gradient(135deg, #3b64f8, #7c3aed)',
            boxShadow:   '0 4px 20px rgba(59,100,248,0.4)',
          }}
        >
          {playing ? (
            <Pause size={18} className="text-white" />
          ) : (
            <Play size={18} className="text-white ml-0.5" />
          )}
        </button>

        {/* Progress area */}
        <div className="flex-1 min-w-0">
          {/* Animated wave bars while playing */}
          {playing && (
            <div className="flex items-end gap-0.5 h-6 mb-2">
              {Array.from({ length: 32 }).map((_, i) => (
                <div
                  key={i}
                  className="wave-bar flex-1"
                  style={{
                    animationDelay: `${(i * 0.05) % 1.2}s`,
                    minHeight: '4px',
                  }}
                />
              ))}
            </div>
          )}

          {/* Seek bar */}
          <div
            id="audio-seekbar"
            role="slider"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={Math.round(progress)}
            className="relative h-2 rounded-full cursor-pointer"
            style={{ background: 'rgba(255,255,255,0.1)' }}
            onClick={handleSeek}
          >
            <div
              className="absolute left-0 top-0 h-full rounded-full transition-all duration-100"
              style={{
                width:      `${progress}%`,
                background: 'linear-gradient(to right, #3b64f8, #8b5cf6)',
              }}
            />
          </div>

          <div className="flex justify-between mt-1 text-xs text-slate-500">
            <span>{formatTime((progress / 100) * duration)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        {/* Playback speed selector */}
        <select
          value={playbackRate}
          onChange={(e) => setPlaybackRate(parseFloat(e.target.value))}
          className="bg-transparent text-xs font-medium text-slate-400 cursor-pointer outline-none hover:text-slate-200 transition-colors appearance-none pr-1"
          title="Playback speed"
        >
          <option value={0.5} className="bg-slate-800 text-slate-200">0.5x</option>
          <option value={0.75} className="bg-slate-800 text-slate-200">0.75x</option>
          <option value={1} className="bg-slate-800 text-slate-200">1x</option>
          <option value={1.25} className="bg-slate-800 text-slate-200">1.25x</option>
          <option value={1.5} className="bg-slate-800 text-slate-200">1.5x</option>
          <option value={2} className="bg-slate-800 text-slate-200">2x</option>
        </select>

        {/* Volume icon (decorative) */}
        <Volume2 size={16} className="text-slate-500 flex-shrink-0" />

        {/* Download */}
        <button
          id="audio-download"
          type="button"
          onClick={handleDownload}
          className="btn-secondary flex-shrink-0"
          title="Download audio"
        >
          <Download size={14} />
          <span className="hidden sm:inline">Download</span>
        </button>
      </div>

      <p className="mt-3 text-xs text-slate-600 text-center">
        {fileName} · WAV · 24 kHz
      </p>
    </div>
  )
}

export default AudioPlayer
