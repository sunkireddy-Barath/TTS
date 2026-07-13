import React from 'react'
import { EMOTIONS, type EmotionOption } from '../constants'

interface EmotionPickerProps {
  value: string
  onChange: (val: string) => void
}

const EmotionPicker: React.FC<EmotionPickerProps> = ({ value, onChange }) => {
  return (
    <div>
      <label className="field-label">Emotion</label>
      <div className="grid grid-cols-5 gap-2">
        {EMOTIONS.map((emotion: EmotionOption) => {
          const isActive = value === emotion.value
          return (
            <button
              key={emotion.value}
              id={`emotion-${emotion.value}`}
              type="button"
              onClick={() => onChange(emotion.value)}
              title={emotion.label}
              className={`
                flex flex-col items-center gap-1 px-2 py-2.5 rounded-xl text-xs font-medium
                transition-all duration-200 cursor-pointer border
                ${isActive
                  ? 'border-brand-500 bg-brand-500/20 text-white scale-105 shadow-lg'
                  : 'border-white/8 bg-white/4 text-slate-400 hover:bg-white/8 hover:text-white hover:border-white/15'
                }
              `}
              style={isActive ? { boxShadow: `0 0 16px ${emotion.color}40` } : {}}
            >
              <span className="text-lg leading-none">{emotion.emoji}</span>
              <span className="leading-none truncate w-full text-center">
                {emotion.label}
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

export default EmotionPicker
