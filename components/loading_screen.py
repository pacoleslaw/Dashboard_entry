"""
Philippine Statistics Authority (PSA) - Animated Loading Screen Component.
Enforces an official animated vector PSA emblem sequence during initial dashboard
bootstrapping, and automatically re-activates if data loading is long (>400ms).
"""
from pathlib import Path

_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
_ANIMATED_SVG_PATH = _ASSETS_DIR / "psa_logo_animated.svg"

_CACHED_SVG = None

def get_animated_psa_svg() -> str:
    """Return the optimized inline animated SVG of the official PSA emblem."""
    global _CACHED_SVG
    if _CACHED_SVG is None:
        try:
            if _ANIMATED_SVG_PATH.exists():
                _CACHED_SVG = _ANIMATED_SVG_PATH.read_text(encoding="utf-8")
        except Exception:
            pass
        if not _CACHED_SVG:
            _CACHED_SVG = """<svg class="psa-animated-svg-emblem" viewBox="0 0 270 262" role="img" aria-label="Philippine Statistics Authority"><circle cx="135" cy="131" r="110" fill="#ffffff" stroke="#0038a8" stroke-width="4"/></svg>"""
    return _CACHED_SVG

def get_loading_screen_css() -> str:
    """Return critical inline CSS for the PSA animated loading screen."""
    return """
/* ==========================================================================
   PHILIPPINE STATISTICS AUTHORITY - ANIMATED EMBLEM LOADING SCREEN
   ========================================================================== */

/* Hide Dash default unstyled text */
._dash-loading {
    margin: 0;
    padding: 0;
    color: transparent;
}

.psa-loading-screen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.98) 0%, rgba(244, 248, 253, 0.98) 45%, rgba(229, 240, 250, 0.98) 100%);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 9999999;
    user-select: none;
    padding: 24px;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #0f172a;
    opacity: 1;
    transform: scale(1);
    visibility: visible;
    transition: opacity 0.4s cubic-bezier(0.16, 1, 0.3, 1), transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), visibility 0.4s ease;
}

.psa-loading-screen-hidden {
    opacity: 0 !important;
    transform: scale(1.02) !important;
    pointer-events: none !important;
    visibility: hidden !important;
}

/* Subtle statistical/cartographic pattern overlay */
.psa-loading-screen::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image: 
        radial-gradient(rgba(0, 43, 92, 0.06) 1.2px, transparent 1.2px),
        linear-gradient(to right, rgba(0, 43, 92, 0.02) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(0, 43, 92, 0.02) 1px, transparent 1px);
    background-size: 32px 32px, 64px 64px, 64px 64px;
    pointer-events: none;
    opacity: 0.85;
}

.psa-loading-card {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    z-index: 2;
}

/* --------------------------------------------------------------------------
   ANIMATED PSA EMBLEM CONTAINER & ORBIT RINGS
   -------------------------------------------------------------------------- */
.psa-logo-container {
    position: relative;
    width: 260px;
    height: 260px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0;
}

/* Multi-spectrum Ambient Aura */
.psa-logo-glow {
    position: absolute;
    width: 290px;
    height: 290px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0, 56, 168, 0.25) 0%, rgba(252, 209, 22, 0.19) 42%, rgba(206, 17, 38, 0.12) 64%, rgba(255, 255, 255, 0) 74%);
    animation: psaGlowBreathing 4s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 1;
}

/* Outer Precision Astronomical Orbit Ring */
.psa-orbit-outer {
    position: absolute;
    width: 250px;
    height: 250px;
    border-radius: 50%;
    border: 1.5px dashed rgba(0, 56, 168, 0.26);
    animation: psaSpinClockwise 28s linear infinite;
    pointer-events: none;
    z-index: 2;
}

/* Satellite node 1: Philippine Blue */
.psa-orbit-outer::before {
    content: '';
    position: absolute;
    top: -6px;
    left: 50%;
    transform: translateX(-50%);
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #0038a8;
    box-shadow: 0 0 16px #0038a8, 0 0 4px #ffffff;
}

/* Satellite node 2: Philippine Red */
.psa-orbit-outer::after {
    content: '';
    position: absolute;
    bottom: -6px;
    left: 50%;
    transform: translateX(-50%);
    width: 11px;
    height: 11px;
    border-radius: 50%;
    background: #ce1126;
    box-shadow: 0 0 14px #ce1126, 0 0 4px #ffffff;
}

/* Inner Fast Orbit Ring: Golden Sun */
.psa-orbit-inner {
    position: absolute;
    width: 218px;
    height: 218px;
    border-radius: 50%;
    border: 1.2px solid rgba(252, 209, 22, 0.45);
    animation: psaSpinCounterClockwise 16s linear infinite;
    pointer-events: none;
    z-index: 2;
}

.psa-orbit-inner::after {
    content: '';
    position: absolute;
    top: 50%;
    right: -5.5px;
    transform: translateY(-50%);
    width: 11px;
    height: 11px;
    border-radius: 50%;
    background: #fcd116;
    box-shadow: 0 0 14px #fcd116, 0 0 5px #fff2a8;
}

/* --------------------------------------------------------------------------
   THE ANIMATED SVG EMBLEM
   -------------------------------------------------------------------------- */
.psa-emblem-wrapper {
    position: relative;
    width: 180px;
    height: 180px;
    z-index: 3;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    box-shadow: 
        0 18px 42px -6px rgba(0, 43, 92, 0.25),
        0 8px 18px rgba(0, 43, 92, 0.12);
    animation: psaSealFloat 4s ease-in-out infinite;
}

.psa-animated-svg-emblem {
    width: 100%;
    height: 100%;
    display: block;
    overflow: visible;
}

/* Base white disc */
.psa-seal-base {
    filter: drop-shadow(0 2px 5px rgba(0, 0, 0, 0.08));
}

/* Animated Globe Coordinate Lines */
.psa-globe-line {
    transition: all 0.3s ease;
    animation: psaGlobeGaze 4.5s ease-in-out infinite alternate;
}

/* Dynamic Ribbon Wave Surges */
.psa-ribbon {
    transform-origin: 102px 165px;
    transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 1. Philippine Blue Ribbon */
.psa-ribbon-blue {
    animation: psaRibbonSurgeBlue 3.4s ease-in-out infinite;
    filter: drop-shadow(0 2px 8px rgba(0, 56, 168, 0.65));
}

/* 2. Golden Yellow Ribbon */
.psa-ribbon-yellow {
    animation: psaRibbonSurgeYellow 3.4s ease-in-out infinite;
    animation-delay: 0.22s;
    filter: drop-shadow(0 2px 10px rgba(252, 209, 22, 0.85));
}

/* 3. Philippine Red Ribbon */
.psa-ribbon-red {
    animation: psaRibbonSurgeRed 3.4s ease-in-out infinite;
    animation-delay: 0.44s;
    filter: drop-shadow(0 2px 8px rgba(206, 17, 38, 0.65));
}

/* --------------------------------------------------------------------------
   KEYFRAME ANIMATIONS
   -------------------------------------------------------------------------- */
@keyframes psaScreenFadeIn {
    from { opacity: 0; transform: scale(0.97); }
    to { opacity: 1; transform: scale(1); }
}

@keyframes psaSealFloat {
    0%, 100% {
        transform: translateY(0px) rotate(0deg);
    }
    50% {
        transform: translateY(-9px) rotate(0.4deg);
    }
}

@keyframes psaGlowBreathing {
    0% {
        transform: scale(0.92);
        opacity: 0.55;
    }
    100% {
        transform: scale(1.18);
        opacity: 0.95;
    }
}

@keyframes psaSpinClockwise {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

@keyframes psaSpinCounterClockwise {
    from { transform: rotate(360deg); }
    to { transform: rotate(0deg); }
}

/* Ribbon Wave / Surges */
@keyframes psaRibbonSurgeBlue {
    0%, 100% {
        transform: translateY(0) scale(1);
        filter: drop-shadow(0 2px 7px rgba(0, 56, 168, 0.5));
    }
    50% {
        transform: translateY(-2px) scale(1.03);
        filter: drop-shadow(0 4px 15px rgba(0, 56, 168, 0.85));
    }
}

@keyframes psaRibbonSurgeYellow {
    0%, 100% {
        transform: translateY(0) scale(1);
        filter: drop-shadow(0 2px 8px rgba(252, 209, 22, 0.65));
    }
    50% {
        transform: translateY(-2.5px) scale(1.04);
        filter: drop-shadow(0 5px 18px rgba(252, 209, 22, 0.95));
    }
}

@keyframes psaRibbonSurgeRed {
    0%, 100% {
        transform: translateY(0) scale(1);
        filter: drop-shadow(0 2px 7px rgba(206, 17, 38, 0.5));
    }
    50% {
        transform: translateY(-2px) scale(1.03);
        filter: drop-shadow(0 4px 15px rgba(206, 17, 38, 0.85));
    }
}

@keyframes psaGlobeGaze {
    0% {
        opacity: 0.72;
        filter: drop-shadow(0 0 0px rgba(0, 56, 168, 0));
    }
    100% {
        opacity: 1;
        filter: drop-shadow(0 0 3px rgba(0, 56, 168, 0.4));
    }
}
"""

def get_loading_screen_overlay_html() -> str:
    """
    Return the standalone HTML structure and intelligent controller script.
    Guarantees the animated PSA emblem displays during initial bootstrapping,
    and automatically shows during runtime only if data loading is long (>380ms).
    """
    psa_svg = get_animated_psa_svg()
    return f"""<div class="psa-loading-screen" id="psa-app-loading-screen">
    <div class="psa-loading-card">
        <!-- Animated PSA Emblem Logo with Orbiting Satellite Nodes -->
        <div class="psa-logo-container">
            <div class="psa-logo-glow"></div>
            <div class="psa-orbit-outer"></div>
            <div class="psa-orbit-inner"></div>
            <div class="psa-emblem-wrapper">
                {psa_svg}
            </div>
        </div>
    </div>
    <script>
        (function() {{
            const overlay = document.getElementById("psa-app-loading-screen");
            if (!overlay) return;

            let isInitialLoad = true;
            const initialLoadStartTime = Date.now();
            const MIN_INITIAL_DURATION_MS = 250; // Smooth intro settle time
            const LONG_DATA_THRESHOLD_MS = 380;  // Threshold for showing loading screen on long data loads
            let activeRequests = 0;
            let longLoadingTimer = null;
            let safetyTimer = null;

            function showLoadingScreen() {{
                if (longLoadingTimer) {{
                    clearTimeout(longLoadingTimer);
                    longLoadingTimer = null;
                }}
                overlay.classList.remove("psa-loading-screen-hidden");
                // Reset safety timer (auto-hide after 12s if network hangs)
                if (safetyTimer) clearTimeout(safetyTimer);
                safetyTimer = setTimeout(hideLoadingScreen, 12000);
            }}

            function hideLoadingScreen() {{
                if (safetyTimer) {{
                    clearTimeout(safetyTimer);
                    safetyTimer = null;
                }}
                overlay.classList.add("psa-loading-screen-hidden");
            }}

            // --- 1. Initial Data Load Sequence ---
            function checkInitialReady() {{
                const dashboard = document.querySelector(".dashboard-page-wrapper");
                const kpis = document.querySelector("#kpi-cards-container");
                const hasKpiData = kpis && kpis.children && kpis.children.length > 0;
                const elapsed = Date.now() - initialLoadStartTime;

                // Dismiss as soon as layout + initial data are ready, without artificial delay
                if (dashboard && hasKpiData && activeRequests === 0 && elapsed >= MIN_INITIAL_DURATION_MS) {{
                    isInitialLoad = false;
                    requestAnimationFrame(function() {{
                        hideLoadingScreen();
                    }});
                }} else if (elapsed > 8000) {{
                    // Fallback initial safety release
                    isInitialLoad = false;
                    hideLoadingScreen();
                }} else {{
                    // Keep loading screen active if data loading is taking long
                    setTimeout(checkInitialReady, 40);
                }}
            }}
            setTimeout(checkInitialReady, 60);

            // --- 2. Monitor Long Data Loading (Show only if data loading is long) ---
            function onDataRequestStart() {{
                activeRequests++;
                if (!isInitialLoad && activeRequests === 1) {{
                    if (longLoadingTimer) clearTimeout(longLoadingTimer);
                    // Only display the loading screen if the data load exceeds threshold
                    longLoadingTimer = setTimeout(function() {{
                        if (activeRequests > 0) {{
                            showLoadingScreen();
                        }}
                    }}, LONG_DATA_THRESHOLD_MS);
                }}
            }}

            function onDataRequestEnd() {{
                activeRequests = Math.max(0, activeRequests - 1);
                if (activeRequests === 0) {{
                    if (longLoadingTimer) {{
                        clearTimeout(longLoadingTimer);
                        longLoadingTimer = null;
                    }}
                    if (!isInitialLoad) {{
                        // Allow Dash and React to finish painting data before fading screen
                        requestAnimationFrame(function() {{
                            setTimeout(hideLoadingScreen, 60);
                        }});
                    }}
                }}
            }}

            // Intercept window.fetch for Dash callbacks and data queries
            if (window.fetch) {{
                const originalFetch = window.fetch;
                window.fetch = function() {{
                    let isDashData = false;
                    try {{
                        const url = (arguments[0] && typeof arguments[0] === 'string') 
                            ? arguments[0] 
                            : (arguments[0] && arguments[0].url) || '';
                        isDashData = url.indexOf('_dash-update-component') !== -1 || url.indexOf('_dash-dependencies') !== -1;
                    }} catch (e) {{}}

                    if (isDashData) {{
                        onDataRequestStart();
                    }}

                    return originalFetch.apply(this, arguments).then(function(res) {{
                        if (isDashData) onDataRequestEnd();
                        return res;
                    }}).catch(function(err) {{
                        if (isDashData) onDataRequestEnd();
                        throw err;
                    }});
                }};
            }}

            // Intercept XMLHttpRequest as fallback
            if (window.XMLHttpRequest) {{
                const origOpen = XMLHttpRequest.prototype.open;
                const origSend = XMLHttpRequest.prototype.send;
                
                XMLHttpRequest.prototype.open = function(method, url) {{
                    this._isDashData = url && typeof url === 'string' && (url.indexOf('_dash-update-component') !== -1);
                    return origOpen.apply(this, arguments);
                }};
                
                XMLHttpRequest.prototype.send = function() {{
                    if (this._isDashData) {{
                        onDataRequestStart();
                        this.addEventListener('loadend', function() {{
                            onDataRequestEnd();
                        }}, {{ once: true }});
                    }}
                    return origSend.apply(this, arguments);
                }};
            }}

            // MutationObserver to watch for Dash's internal [data-dash-is-loading="true"]
            let dashLoadingActive = false;
            const observer = new MutationObserver(function() {{
                const hasDashLoading = !!document.querySelector('[data-dash-is-loading="true"]');
                if (hasDashLoading && !dashLoadingActive) {{
                    dashLoadingActive = true;
                    onDataRequestStart();
                }} else if (!hasDashLoading && dashLoadingActive) {{
                    dashLoadingActive = false;
                    onDataRequestEnd();
                }}
            }});
            observer.observe(document.documentElement, {{
                attributes: true,
                subtree: true,
                attributeFilter: ['data-dash-is-loading']
            }});
        }})();
    </script>
</div>"""

def setup_loading_screen(app) -> None:
    """
    Configure Dash app to guarantee the animated PSA logo loading screen is rendered
    first before any main pages or dashboard components are displayed.
    """
    css_block = f"<style>{get_loading_screen_css()}</style>"
    loading_overlay = get_loading_screen_overlay_html()
    
    orig_interpolate = app.interpolate_index
    
    def custom_interpolate_index(**kwargs):
        # Inject critical CSS right at top of head for 0ms paint latency
        if 'css' in kwargs:
            kwargs['css'] = f"{css_block}\n{kwargs['css']}"
        else:
            kwargs['css'] = css_block
            
        # Mount point for React + persistent full-screen overlay that survives React mounting
        kwargs['app_entry'] = f"""<div id="react-entry-point">
    <div class="_dash-loading"></div>
</div>
{loading_overlay}"""
        return orig_interpolate(**kwargs)
        
    app.interpolate_index = custom_interpolate_index
