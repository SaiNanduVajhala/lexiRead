(function() {
    if (window.lexiReadInitialized) return;
    window.lexiReadInitialized = true;

    let rulerDiv = null;
    let mouseMoveAttached = false;

    const applyGlobalSettings = () => {
        const theme = localStorage.getItem('lexiRead_theme') || 'soft_cream';
        const spacing = localStorage.getItem('lexiRead_lineSpacing') || 'relaxed';
        
        // 1. Theme
        if (theme === 'deep_slate') {
            document.documentElement.classList.add('dark');
            document.documentElement.classList.remove('light');
        } else {
            document.documentElement.classList.remove('dark');
            document.documentElement.classList.add('light');
        }

        // 2. Line spacing
        let lh = '1.8';
        if (spacing === 'standard') lh = '1.4';
        else if (spacing === 'loose') lh = '2.2';

        let globalStyle = document.getElementById('lexiRead-global-styles');
        if (!globalStyle) {
            globalStyle = document.createElement('style');
            globalStyle.id = 'lexiRead-global-styles';
            document.head.appendChild(globalStyle);
        }

        const darkModeCSS = `
            html.dark body { background-color: #1a1b2e !important; color: #e0e0e8 !important; }
            html.dark .bg-background, html.dark .bg-cream, html.dark .bg-surface { background-color: #1a1b2e !important; }
            html.dark .bg-card, html.dark .bg-surface-container-lowest { background-color: #12131f !important; }
            html.dark .bg-surface-container-low { background-color: #1e1f33 !important; }
            html.dark .bg-surface-container { background-color: #252640 !important; }
            html.dark .bg-surface-container-high { background-color: #2c2d4a !important; }
            html.dark .bg-surface-container-highest { background-color: #333456 !important; }
            html.dark .text-on-background, html.dark .text-on-surface, html.dark .text-charcoal { color: #e0e0e8 !important; }
            html.dark .text-on-surface-variant, html.dark .text-text-muted { color: #a0a4b8 !important; }
            html.dark .border-surface-variant, html.dark .border-border { border-color: rgba(160, 164, 184, 0.2) !important; }
            html.dark nav, html.dark header { background-color: #12131f !important; border-color: rgba(160, 164, 184, 0.2) !important; }
            html.dark input:not([type="checkbox"]):not([type="range"]), html.dark textarea, html.dark select {
                background-color: #12131f !important;
                color: #e0e0e8 !important;
                border-color: rgba(160, 164, 184, 0.3) !important;
            }
        `;

        // Exclude elements with data-preview-spacing from the global override
        // so settings page previews can show their own line-height
        globalStyle.textContent = `
            body, p:not([data-preview-spacing]), span, div:not([class*="material-symbols"]):not([data-preview-spacing]), li { 
                line-height: ${lh} !important; 
            }
            ${theme === 'deep_slate' ? darkModeCSS : ''}
        `;

        // 3. Ruler
        updateRuler();
    };

    const hexToRgba = (hex, alpha) => {
        if (!hex || !hex.startsWith('#')) return `rgba(181, 217, 156, ${alpha})`;
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    };

    const getHeightPx = (multiplier) => {
        // multiplier 1=small, 2=medium, 3=large  →  24px / 36px / 52px
        if (multiplier <= 1) return 24;
        if (multiplier >= 3) return 52;
        // linear interpolation between 24 and 52
        return Math.round(24 + (multiplier - 1) * 14);
    };

    const updateRuler = () => {
        const isRulerEnabled = localStorage.getItem('lexiRead_ruler') === 'true';
        const rulerColor = localStorage.getItem('lexiRead_rulerColor') || '#B5D99C';
        const rulerHeightMultiplier = parseFloat(localStorage.getItem('lexiRead_rulerHeight') || '2');
        const heightVal = getHeightPx(rulerHeightMultiplier);

        const isSettingsPage = window.location.pathname.endsWith('settings.html') || window.location.href.includes('settings.html');
        
        const existingRuler = document.getElementById('globalReadingRuler');
        if (existingRuler) {
            if (!isRulerEnabled || isSettingsPage) {
                existingRuler.remove();
                rulerDiv = null;
                return;
            }
            // Update existing ruler properties
            rulerDiv = existingRuler;
        }

        if (isRulerEnabled && !isSettingsPage) {
            if (!rulerDiv) {
                rulerDiv = document.createElement('div');
                rulerDiv.id = 'globalReadingRuler';
                rulerDiv.style.position = 'fixed';
                rulerDiv.style.left = '0';
                rulerDiv.style.right = '0';
                rulerDiv.style.pointerEvents = 'none';
                rulerDiv.style.zIndex = '999999';
                rulerDiv.style.top = '50%';
                rulerDiv.style.transition = 'height 0.2s ease';
                document.body.appendChild(rulerDiv);
                
                if (!mouseMoveAttached) {
                    mouseMoveAttached = true;
                    document.addEventListener('mousemove', (e) => {
                        if (rulerDiv && localStorage.getItem('lexiRead_ruler') === 'true') {
                            const currentHeight = parseFloat(rulerDiv.style.height) || 36;
                            rulerDiv.style.top = (e.clientY - (currentHeight / 2)) + 'px';
                        }
                    });
                }
            }
            rulerDiv.style.display = 'block';
            rulerDiv.style.height = heightVal + 'px';
            rulerDiv.style.backgroundColor = hexToRgba(rulerColor, 0.18);
            rulerDiv.style.borderTop = `2px solid ${hexToRgba(rulerColor, 0.5)}`;
            rulerDiv.style.borderBottom = `2px solid ${hexToRgba(rulerColor, 0.5)}`;
            rulerDiv.style.boxShadow = `0 0 20px ${hexToRgba(rulerColor, 0.1)}`;
        }
    };

    const applyBionic = (text) => {
        if (!text) return "";
        const isBionic = localStorage.getItem('lexiRead_bionic') === 'true';
        if (!isBionic) return text;
        
        return text.split(/\s+/).map(word => {
            if (word.length <= 1) return word;
            if (word.startsWith('<')) return word; 
            const boldLen = Math.ceil(word.length * 0.4);
            return `<b>${word.substring(0, boldLen)}</b>${word.substring(boldLen)}`;
        }).join(' ');
    };

    window.refreshAccessibility = applyGlobalSettings;
    window.applyBionic = applyBionic;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyGlobalSettings);
    } else {
        applyGlobalSettings();
    }

    window.addEventListener('storage', (e) => {
        const keysToWatch = ['lexiRead_ruler', 'lexiRead_theme', 'lexiRead_lineSpacing', 'lexiRead_bionic', 'lexiRead_rulerColor', 'lexiRead_rulerHeight'];
        if (keysToWatch.includes(e.key)) {
            applyGlobalSettings();
        }
    });
})();
