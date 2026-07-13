import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import VoiceDesignPage from './pages/VoiceDesignPage'
import VoiceClonePage from './pages/VoiceClonePage'

// Background orbs for ambient depth
const BackgroundOrbs: React.FC = () => (
  <div className="fixed inset-0 pointer-events-none overflow-hidden" style={{ zIndex: 0 }}>
    {/* Top-left orb */}
    <div
      className="absolute -top-[20%] -left-[10%] w-[50vw] h-[50vw] rounded-full opacity-30 animate-float"
      style={{
        background: 'radial-gradient(circle, #3b64f8 0%, transparent 70%)',
        filter: 'blur(80px)',
        animationDelay: '0s',
      }}
    />
    {/* Top-right orb */}
    <div
      className="absolute -top-[10%] -right-[10%] w-[40vw] h-[40vw] rounded-full opacity-20 animate-float"
      style={{
        background: 'radial-gradient(circle, #8b5cf6 0%, transparent 70%)',
        filter: 'blur(80px)',
        animationDelay: '2s',
      }}
    />
    {/* Bottom-center orb */}
    <div
      className="absolute -bottom-[20%] left-1/2 -translate-x-1/2 w-[80vw] h-[40vw] opacity-15 animate-float"
      style={{
        background: 'radial-gradient(ellipse, #3b64f8 0%, transparent 70%)',
        filter: 'blur(100px)',
        animationDelay: '4s',
      }}
    />
  </div>
)

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <div className="relative min-h-screen noise-overlay">
        <BackgroundOrbs />
        <div className="relative" style={{ zIndex: 1 }}>
          <Navbar />
          <Routes>
            <Route path="/"      element={<VoiceDesignPage />} />
            <Route path="/clone" element={<VoiceClonePage />} />
            {/* Fallback */}
            <Route path="*" element={<VoiceDesignPage />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
