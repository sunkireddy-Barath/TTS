import React from 'react'
import { LANGUAGE_GROUPS, type LanguageOption } from '../constants'

interface LanguageSelectorProps {
  value: string
  onChange: (val: string) => void
  id?: string
}

const LanguageSelector: React.FC<LanguageSelectorProps> = ({
  value,
  onChange,
  id = 'language-select',
}) => {
  return (
    <div>
      <label htmlFor={id} className="field-label">
        Language
      </label>
      <select
        id={id}
        className="field-select"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        {LANGUAGE_GROUPS.map((group) => (
          <optgroup key={group.group} label={`── ${group.group} ──`}>
            {group.languages.map((lang: LanguageOption) => (
              <option key={lang.value} value={lang.value}>
                {lang.label}
              </option>
            ))}
          </optgroup>
        ))}
      </select>
    </div>
  )
}

export default LanguageSelector
