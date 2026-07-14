import React from 'react'
import { type AppVersion } from '../constants'
import { Layers, Code2 } from 'lucide-react'

interface VersionBadgeProps {
  version: AppVersion
  onChange: (v: AppVersion) => void
}

const VERSION_CONFIG = [
  {
    v: 1 as AppVersion,
    icon: null,
    label: 'V1',
    desc: 'Basic',
  },
  {
    v: 2 as AppVersion,
    icon: null,
    label: 'V2',
    desc: 'Expressions',
  },
  {
    v: 3 as AppVersion,
    icon: null,
    label: 'V3',
    desc: 'Advanced',
  },
]

const VersionSwitcher: React.FC<VersionBadgeProps> = ({ version, onChange }) => {
  return (
    <div className="flex gap-1 p-1 rounded-xl" style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.06)' }}>
      {VERSION_CONFIG.map(({ v, icon, label, desc }) => {
        const active = version === v
        return (
          <button
            key={v}
            id={`version-${v}`}
            type="button"
            onClick={() => onChange(v)}
            className={`
              flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold
              transition-all duration-200
              ${active
                ? 'bg-gradient-to-r from-brand-600 to-accent-600 text-white shadow-lg'
                : 'text-slate-500 hover:text-slate-300'
              }
            `}
            title={desc}
          >
            <span>{label}</span>
          </button>
        )
      })}
    </div>
  )
}

export default VersionSwitcher
