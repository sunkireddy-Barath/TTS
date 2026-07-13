import axios, { AxiosError } from 'axios'
import { API_BASE } from './constants'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    // ngrok free tier returns an HTML interstitial unless this header is sent
    'ngrok-skip-browser-warning': 'true',
  },
})

// ─── Error extraction helper ──────────────────────────────────────────────────
// When responseType is 'blob', axios returns the error body as a Blob too.
// We parse it back to JSON to get the FastAPI detail message.
async function extractErrorMessage(err: unknown): Promise<string> {
  if (err instanceof AxiosError) {
    const data = err.response?.data
    if (data instanceof Blob) {
      try {
        const text   = await data.text()
        const parsed = JSON.parse(text)
        return parsed?.detail ?? parsed?.message ?? text
      } catch {
        return `Server error ${err.response?.status ?? ''}`
      }
    }
    if (typeof data === 'object' && data?.detail) return String(data.detail)
    if (err.message) return err.message
  }
  return 'Unknown error — is the backend running?'
}

// ─── Voice Design ─────────────────────────────────────────────────────────────
export interface VoiceDesignParams {
  text:       string
  language:   string
  gender:     string
  age:        number
  emotion:    string
  expression: string
  version:    number
}

export async function generateVoiceDesign(
  params: VoiceDesignParams,
): Promise<Blob> {
  const form = new FormData()
  Object.entries(params).forEach(([k, v]) => form.append(k, String(v)))

  try {
    const res = await api.post('/api/voice-design', form, {
      responseType: 'blob',
    })
    return res.data as Blob
  } catch (err) {
    const msg = await extractErrorMessage(err)
    throw new Error(msg)
  }
}

// ─── Voice Clone ──────────────────────────────────────────────────────────────
export interface VoiceCloneParams {
  text:             string
  target_language:  string
  reference_audio:  File
  gender:           string
  age:              number
  emotion:          string
  expression:       string
  version:          number
  ref_text?:        string   // Optional: transcription of reference audio
                             // If omitted, VoiceX uses Whisper to auto-transcribe
}

export async function generateVoiceClone(
  params: VoiceCloneParams,
): Promise<Blob> {
  const form = new FormData()
  form.append('text',            params.text)
  form.append('target_language', params.target_language)
  form.append('reference_audio', params.reference_audio)
  form.append('gender',          params.gender)
  form.append('age',             String(params.age))
  form.append('emotion',         params.emotion)
  form.append('expression',      params.expression)
  form.append('version',         String(params.version))
  // ref_text is optional — omit if empty so VoiceX uses Whisper auto-transcription
  if (params.ref_text?.trim()) {
    form.append('ref_text', params.ref_text.trim())
  }

  try {
    const res = await api.post('/api/voice-clone', form, {
      responseType: 'blob',
    })
    return res.data as Blob
  } catch (err) {
    const msg = await extractErrorMessage(err)
    throw new Error(msg)
  }
}

// ─── Utilities ────────────────────────────────────────────────────────────────
export async function removeAudioNoise(file: File): Promise<Blob> {
  const form = new FormData()
  form.append('reference_audio', file)

  try {
    const res = await api.post('/api/remove-noise', form, {
      responseType: 'blob',
    })
    return res.data as Blob
  } catch (err) {
    const msg = await extractErrorMessage(err)
    throw new Error(msg)
  }
}

// ─── Health ───────────────────────────────────────────────────────────────────
export async function checkHealth(): Promise<{
  status: string
  model_loaded: boolean
  device: string
}> {
  const res = await api.get('/api/health')
  return res.data
}
