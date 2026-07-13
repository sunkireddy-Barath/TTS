import React from 'react'
import { NavLink } from 'react-router-dom'
import { Mic2, GitMerge, Cpu } from 'lucide-react'

const NAV_LINKS = [
  { to: '/',      label: 'Voice Design',  Icon: Mic2,     id: 'nav-voice-design' },
  { to: '/clone', label: 'Voice Cloning', Icon: GitMerge, id: 'nav-voice-clone'  },
]

const Navbar: React.FC = () => {
  return (
    <header className="sticky top-0 z-50" style={{ background: 'rgba(10,11,26,0.85)', backdropFilter: 'blur(20px)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
      <div className="w-full px-6 lg:px-12 h-16 flex items-center justify-between">

        {/* Logo */}
        <div className="flex items-center gap-3">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{ background: 'linear-gradient(135deg, #3b64f8, #8b5cf6)', boxShadow: '0 4px 14px rgba(59,100,248,0.4)' }}
          >
            <Cpu size={18} className="text-white" />
          </div>
          <div>
            <span className="font-display font-bold text-white text-lg leading-none">
              VoiceX
            </span>
            <span className="block text-xs text-slate-500 leading-none mt-0.5">Studio</span>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex gap-1 p-1 rounded-xl" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)' }}>
          {NAV_LINKS.map(({ to, label, Icon, id }) => (
            <NavLink
              key={to}
              to={to}
              end
              id={id}
              className={({ isActive }) =>
                `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-brand-600 to-accent-600 text-white shadow-lg'
                    : 'text-slate-400 hover:text-white'
                }`
              }
            >
              <Icon size={15} />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Status dot */}
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse-slow" />
          VoiceX
        </div>

      </div>
    </header>
  )
}

export default Navbar
