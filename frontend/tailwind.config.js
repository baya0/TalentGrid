/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary - Trust & Intelligence (navbar, main buttons, headings)
        primary: {
          DEFAULT: '#003833',
          50: '#E6EDEC',
          100: '#CCDBD9',
          200: '#99B7B3',
          300: '#66938D',
          400: '#336F67',
          500: '#003833',
          600: '#002D29',
          700: '#00221F',
          800: '#001614',
          900: '#000B0A',
        },
        // Headlines / Project name color
        headline: '#005347',
        // Secondary - Gold (scores, success states, highlights)
        secondary: {
          DEFAULT: '#CAA667',
          50: '#FAF6EF',
          100: '#F5EDDF',
          200: '#EBDBBF',
          300: '#E1C99F',
          400: '#D7B77F',
          500: '#CAA667',
          600: '#A28552',
          700: '#79643E',
          800: '#514229',
          900: '#282115',
        },
        // Gold alias for secondary
        gold: {
          DEFAULT: '#CAA667',
          100: '#F5EDDF',
          600: '#A28552',
          700: '#79643E',
        },
        // Dark Green (navbar, sidebar backgrounds)
        'dark-green': {
          DEFAULT: '#003833',
          600: '#002D29',
        },
        // Accent - Soft Orange (secondary CTAs, alerts)
        accent: {
          DEFAULT: '#C6B391',
          50: '#FAF8F4',
          100: '#F5F1E9',
          200: '#EBE3D3',
          300: '#E1D5BD',
          400: '#D7C7A7',
          500: '#C6B391',
          600: '#9E8F74',
          700: '#776B57',
          800: '#4F473A',
          900: '#28241D',
        },
        // Upload photo placeholder
        'upload-bg': '#D8E3E2',
        // Background - cream/off-white
        background: {
          DEFAULT: '#F4F2E4',
          light: '#F9F8F2',
        },
        // Text - dark
        text: {
          DEFAULT: '#16150D',
          primary: '#16150D',
          secondary: '#4A4A3F',
          muted: '#7A7A6F',
        },
        // Utility colors
        border: '#E5E5D9',
        success: '#2ECC71',
        error: '#E74C3C',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        display: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 2px 8px rgba(0, 0, 0, 0.08)',
        'card-hover': '0 4px 16px rgba(0, 0, 0, 0.12)',
        'dropdown': '0 4px 12px rgba(0, 0, 0, 0.15)',
      },
      borderRadius: {
        'card': '12px',
      },
    },
  },
  plugins: [],
}
