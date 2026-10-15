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
    """Return critical inline CSS for the PSA simple loading screen."""
    return """
/* ==========================================================================
   PHILIPPINE STATISTICS AUTHORITY - SIMPLE LOADING SCREEN
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
    background: radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.98) 0%, rgba(246, 249, 253, 0.98) 100%);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 9999999;
    user-select: none;
    padding: 24px;
    opacity: 1;
    transform: scale(1);
    visibility: visible;
    transition: opacity 0.35s cubic-bezier(0.16, 1, 0.3, 1), transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), visibility 0.35s ease;
}

.psa-loading-screen-hidden {
    opacity: 0 !important;
    transform: scale(1.02) !important;
    pointer-events: none !important;
    visibility: hidden !important;
}

.psa-loading-card {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

/* Simple, clean centered PSA emblem */
.psa-simple-logo-wrapper {
    position: relative;
    width: 130px;
    height: 130px;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: psaSimplePulse 2.2s ease-in-out infinite alternate;
}

.psa-animated-svg-emblem {
    width: 100%;
    height: 100%;
    display: block;
    filter: drop-shadow(0 4px 14px rgba(0, 43, 92, 0.12));
}

@keyframes psaSimplePulse {
    0% {
        transform: scale(0.97);
        opacity: 0.88;
    }
    100% {
        transform: scale(1.03);
        opacity: 1;
    }
}
"""

def get_loading_screen_overlay_html() -> str:
    """
    Return the standalone HTML structure and intelligent controller script.
    Guarantees the simple PSA emblem displays during initial bootstrapping,
    and automatically shows during runtime only if data loading is long (>380ms).
    """
    psa_svg = get_animated_psa_svg()
    return f"""<div class="psa-loading-screen" id="psa-app-loading-screen">
    <div class="psa-loading-card">
        <!-- Clean, Simple Centered PSA Emblem Logo -->
        <div class="psa-simple-logo-wrapper">
            {psa_svg}
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
