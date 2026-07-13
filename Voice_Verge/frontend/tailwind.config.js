/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Sora', 'Inter', 'sans-serif'],
      },
      colors: {
        brand: {
          50:  '#e6fffe',
          100: '#ccfdfc',
          200: '#99fbfa',
          300: '#66f8f7',
          400: '#33f4f4',
          500: '#00E1D9', // Neon Cyan
          600: '#00b3ad',
          700: '#008581',
          800: '#005a57',
          900: '#002d2b',
          950: '#001716',
        },
        accent: {
          400: '#339cff',
          500: '#007BFF', // Electric Blue
          600: '#0062cc',
        },
        surface: {
          900: '#050505',
          800: '#0d0d0d',
          700: '#141414',
          600: '#1a1a1a',
          500: '#262626',
        },
      },
      backgroundImage: {
        'hero-gradient':
          'radial-gradient(ellipse 80% 60% at 50% -10%, rgba(0, 225, 217, 0.25) 0%, transparent 70%), radial-gradient(ellipse 60% 50% at 80% 80%, rgba(0, 123, 255, 0.15) 0%, transparent 70%)',
        'card-gradient':
          'linear-gradient(135deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 100%)',
        'button-gradient':
          'linear-gradient(135deg, #00E1D9 0%, #007BFF 100%)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4,0,0.6,1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'wave': 'wave 1.5s ease-in-out infinite',
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-12px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        wave: {
          '0%, 100%': { transform: 'scaleY(0.5)' },
          '50%': { transform: 'scaleY(1.5)' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        slideUp: {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
