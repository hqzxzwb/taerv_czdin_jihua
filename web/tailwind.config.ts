import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './lib/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        paper: '#FBF6EC',
        ink: '#2A2420',
        muted: '#7A6F66',
        line: '#EADFCB',
        brand: { DEFAULT: '#E4572E', deep: '#C2411C', soft: '#FDE9E1' },
        ok: { DEFAULT: '#2E9E6B', soft: '#E1F4EB' },
        bad: { DEFAULT: '#D64545', soft: '#FBE4E4' },
      },
      fontFamily: {
        sans: ['"Noto Sans SC"', '"PingFang SC"', '"Microsoft YaHei"', '"Source Han Sans SC"', 'system-ui', 'sans-serif'],
        mono: ['ui-monospace', '"SF Mono"', 'Menlo', 'Consolas', 'monospace'],
      },
      boxShadow: {
        card: '0 1px 0 rgba(42,36,32,0.04), 0 6px 20px -8px rgba(42,36,32,0.12)',
        press: '0 4px 0 0 #C2411C',
      },
      keyframes: {
        pop: { '0%': { transform: 'scale(.9)', opacity: '0' }, '100%': { transform: 'scale(1)', opacity: '1' } },
        shake: { '0%,100%': { transform: 'translateX(0)' }, '25%': { transform: 'translateX(-6px)' }, '75%': { transform: 'translateX(6px)' } },
      },
      animation: { pop: 'pop .22s ease-out', shake: 'shake .28s ease-in-out' },
    },
  },
  plugins: [],
};

export default config;
