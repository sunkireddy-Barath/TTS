import React from 'react'
import { EXPRESSIONS } from '../constants'


interface ExpressionPickerProps {
  value: string
  onChange: (val: string) => void
}



const ExpressionPicker: React.FC<ExpressionPickerProps> = ({
  value,
  onChange,
}) => {
  return (
    <div>
      <label className="field-label flex items-center gap-1.5">
        Expression
        <span className="ml-auto text-slate-600 normal-case tracking-normal font-normal text-xs">
          (appended automatically)
        </span>
      </label>
      <div className="flex flex-wrap gap-2">
        {EXPRESSIONS.map((expr) => {
          const active = value === expr.value
          return (
            <button
              key={expr.value}
              id={`expression-${expr.value}`}
              type="button"
              onClick={() => onChange(expr.value)}
              className={`
                flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium
                transition-all duration-200 border
                ${active
                  ? 'border-accent-500 bg-accent-500/20 text-white'
                  : 'border-white/8 bg-white/4 text-slate-400 hover:bg-white/8 hover:text-white'
                }
              `}
            >
              <span className="px-1">{expr.label}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

export default ExpressionPicker
