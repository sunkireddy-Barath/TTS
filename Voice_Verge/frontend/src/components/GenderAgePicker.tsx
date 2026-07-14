import React from 'react'
import { GENDERS } from '../constants'

interface GenderAgePickerProps {
  gender: string
  age: number
  onGenderChange: (val: string) => void
  onAgeChange: (val: number) => void
  disabledGender?: boolean
}

const GenderAgePicker: React.FC<GenderAgePickerProps> = ({
  gender,
  age,
  onGenderChange,
  onAgeChange,
  disabledGender = false,
}) => {
  return (
    <div className="grid grid-cols-2 gap-4">
      {/* Gender */}
      <div>
        <label className="field-label">Gender</label>
        <div className="flex gap-2">
          {GENDERS.map((g) => {
            const active = gender === g.value
            return (
              <button
                key={g.value}
                id={`gender-${g.value}`}
                disabled={disabledGender}
                onClick={() => !disabledGender && onGenderChange(g.value)}
                className={`
                  flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl text-xs font-semibold
                  transition-all duration-200 border
                  ${disabledGender ? 'opacity-50 cursor-not-allowed' : ''}
                  ${active
                    ? 'border-brand-500 bg-brand-500/20 text-white'
                    : 'border-white/8 bg-white/4 text-slate-400 hover:bg-white/8 hover:text-white'
                  }
                `}
              >
                {g.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Age */}
      <div>
        <label htmlFor="age-input" className="field-label flex items-center justify-between">
          <span>Age</span>
          <span
            className="text-brand-400 font-bold text-sm normal-case tracking-normal"
            style={{ fontVariantNumeric: 'tabular-nums' }}
          >
            {age}
          </span>
        </label>
        <div className="relative mt-1">
          <input
            id="age-input"
            type="range"
            min={10}
            max={90}
            step={1}
            value={age}
            onChange={(e) => onAgeChange(Number(e.target.value))}
            className="w-full appearance-none h-2 rounded-full outline-none cursor-pointer"
            style={{
              background: `linear-gradient(to right, #3b64f8 0%, #8b5cf6 ${((age - 10) / 80) * 100}%, rgba(255,255,255,0.1) ${((age - 10) / 80) * 100}%, rgba(255,255,255,0.1) 100%)`,
            }}
          />
          <div className="flex justify-between mt-1 text-xs text-slate-600">
            <span>10</span>
            <span>90</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default GenderAgePicker
