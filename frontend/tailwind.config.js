/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'athena-bg': '#0f172a',
                'athena-card': '#1e293b',
                'athena-accent': '#38bdf8',
            },
        },
    },
    plugins: [],
}
