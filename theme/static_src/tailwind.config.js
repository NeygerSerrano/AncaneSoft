/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
    content: [
        '../templates/**/*.html',
        '../../templates/**/*.html',
        '../../**/templates/**/*.html',
    ],
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                "brand-primary": "var(--color-primary, #1d8797)",
                "brand-secondary": "var(--color-secondary, #0f3856)",
                "secondary-container": "#e50066",
                "secondary-fixed-dim": "#ffb1c1",
                "primary-fixed-dim": "#a5d0b9",
                "on-tertiary-fixed-variant": "#454748",
                "surface-variant": "#d9e3f4",
                "surface-container-lowest": "#ffffff",
                "secondary": "#b70050",
                "outline-variant": "#c1c8c2",
                "on-secondary-fixed-variant": "#90003e",
                "surface-container-highest": "#d9e3f4",
                "outline": "#717973",
                "surface": "#f8f9ff",
                "secondary-fixed": "#ffd9df",
                "on-background": "#121c28",
                "surface-tint": "#3f6653",
                "inverse-surface": "#27313e",
                "on-surface-variant": "#414844",
                "tertiary-fixed-dim": "#c5c7c8",
                "on-tertiary-container": "#a5a6a7",
                "primary-container": "#1b4332",
                "surface-bright": "#f8f9ff",
                "surface-container-high": "#dfe9fa",
                "primary": "#012d1d",
                "on-primary-fixed": "#002114",
                "inverse-on-surface": "#eaf1ff",
                "tertiary-fixed": "#e1e3e4",
                "surface-container-low": "#eef4ff",
                "on-primary": "#ffffff",
                "inverse-primary": "#a5d0b9",
                "on-secondary": "#ffffff",
                "surface-container": "#e5eeff",
                "primary-fixed": "#c1ecd4",
                "on-primary-fixed-variant": "#274e3d",
                "on-tertiary": "#ffffff",
                "on-error": "#ffffff",
                "background": "#f8f9ff",
                "surface-dim": "#d1dbec",
                "on-surface": "#121c28",
                "on-secondary-fixed": "#3f0017",
                "on-error-container": "#93000a",
                "error-container": "#ffdad6",
                "tertiary": "#242628",
                "error": "#ba1a1a",
                "on-tertiary-fixed": "#191c1d",
                "on-secondary-container": "#fffbff",
                "tertiary-container": "#393c3d",
                "on-primary-container": "#86af99"
            },
            borderRadius: {
                "DEFAULT": "0.25rem",
                "lg": "0.5rem",
                "xl": "0.75rem",
                "full": "9999px"
            },
            spacing: {
                "margin-desktop": "32px",
                "margin-mobile": "16px",
                "base": "4px",
                "gutter": "24px",
                "container-max": "1440px"
            },
            fontFamily: {
                "headline-md": ["Inter"],
                "headline-lg": ["Inter"],
                "headline-sm": ["Inter"],
                "body-lg": ["Inter"],
                "label-sm": ["Inter"],
                "headline-lg-mobile": ["Inter"],
                "body-md": ["Inter"],
                "label-md": ["Inter"]
            },
            fontSize: {
                "headline-md": ["24px", { lineHeight: "32px", fontWeight: "600" }],
                "headline-lg": ["32px", { lineHeight: "40px", letterSpacing: "-0.02em", fontWeight: "700" }],
                "headline-sm": ["20px", { lineHeight: "28px", fontWeight: "600" }],
                "body-lg": ["16px", { lineHeight: "24px", fontWeight: "400" }],
                "label-sm": ["12px", { lineHeight: "16px", fontWeight: "500" }],
                "headline-lg-mobile": ["24px", { lineHeight: "32px", fontWeight: "700" }],
                "body-md": ["14px", { lineHeight: "20px", fontWeight: "400" }],
                "label-md": ["14px", { lineHeight: "20px", letterSpacing: "0.01em", fontWeight: "600" }]
            }
        },
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
        require('@tailwindcss/container-queries'),
    ],
}
