"""
Philippine Statistics Authority (PSA) - Custom Loading Screen Component.
Renders an animated PSA emblem logo and modern Philippine-brand loading bar
during initial Dash application bootstrapping before React mounts.
"""
import base64
from pathlib import Path

_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
_SEAL_PATH = _ASSETS_DIR / "psa_seal_clean.png"

def get_seal_data_uri() -> str:
    """Return base64 data URI of the official PSA seal for instantaneous rendering."""
    try:
        if _SEAL_PATH.exists():
            encoded = base64.b64encode(_SEAL_PATH.read_bytes()).decode("utf-8")
            return f"data:image/png;base64,{encoded}"
    except Exception:
        pass
    return "/assets/psa_seal_clean.png"

def get_loading_screen_css() -> str:
    """Return critical inline CSS for the PSA animated loading screen."""
    return """
/* ==========================================================================
   PHILIPPINE STATISTICS AUTHORITY - BRANDED PRELOADER & LOADING BAR
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
    background: radial-gradient(circle at 50% 42%, #ffffff 0%, #f1f7fd 55%, #e1effa 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 999999;
    user-select: none;
    padding: 24px;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #0f172a;
    animation: psaScreenFadeIn 0.35s ease-out;
}

.psa-loading-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    max-width: 500px;
    width: 100%;
}

/* --------------------------------------------------------------------------
   ANIMATED PSA EMBLEM LOGO
   -------------------------------------------------------------------------- */
.psa-logo-container {
    position: relative;
    width: 170px;
    height: 170px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 22px;
}

/* Ambient Radial Glow */
.psa-logo-glow {
    position: absolute;
    width: 170px;
    height: 170px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(15, 82, 186, 0.22) 0%, rgba(252, 209, 22, 0.16) 45%, rgba(255, 255, 255, 0) 72%);
    animation: psaGlowPulse 2.8s ease-in-out infinite alternate;
    pointer-events: none;
}

/* Concentric Orbit Accent Ring */
.psa-orbit-ring {
    position: absolute;
    width: 154px;
    height: 154px;
    border-radius: 50%;
    border: 2px dashed rgba(11, 79, 156, 0.25);
    animation: psaSpinRing 15s linear infinite;
    pointer-events: none;
}

.psa-orbit-ring::after {
    content: '';
    position: absolute;
    top: -4.5px;
    left: 50%;
    transform: translateX(-50%);
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #0f52ba;
    box-shadow: 0 0 10px #0f52ba, 0 0 4px #fcd116;
}

/* The Animated Seal Emblem */
.psa-logo-img {
    position: relative;
    width: 114px;
    height: 114px;
    object-fit: contain;
    image-rendering: high-quality;
    image-rendering: -webkit-optimize-contrast;
    filter: drop-shadow(0 10px 24px rgba(0, 43, 92, 0.18));
    animation: psaFloat 3.2s ease-in-out infinite;
    z-index: 2;
    display: block;
}

/* --------------------------------------------------------------------------
   OFFICIAL TYPOGRAPHY LOCKUP
   -------------------------------------------------------------------------- */
.psa-loading-titles {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 26px;
}

.psa-loading-agency {
    font-family: 'Cinzel', 'Times New Roman', Times, Georgia, serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: #002b5c;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    line-height: 1.3;
    margin-bottom: 5px;
}

.psa-loading-tagline {
    font-size: 0.78rem;
    font-weight: 600;
    color: #54607c;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.psa-loading-brand-line {
    width: 60px;
    height: 2.5px;
    border-radius: 2px;
    background: linear-gradient(90deg, #0038a8 0%, #fcd116 50%, #ce1126 100%);
    margin-bottom: 14px;
}

.psa-loading-subtitle {
    font-size: 0.86rem;
    font-weight: 600;
    color: #0f52ba;
    background: rgba(15, 82, 186, 0.07);
    border: 1px solid rgba(15, 82, 186, 0.16);
    padding: 6px 18px;
    border-radius: 999px;
    display: inline-block;
}

/* --------------------------------------------------------------------------
   ANIMATED LOADING BAR
   -------------------------------------------------------------------------- */
.psa-progress-wrapper {
    width: 340px;
    max-width: 86vw;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
}

.psa-progress-track {
    position: relative;
    width: 100%;
    height: 8px;
    background: #e0ecf7;
    border: 1px solid rgba(15, 82, 186, 0.12);
    border-radius: 999px;
    overflow: hidden;
    box-shadow: inset 0 1px 3px rgba(0, 43, 92, 0.10);
}

.psa-progress-bar {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    width: 42%;
    background: linear-gradient(90deg, #0038a8 0%, #0f52ba 35%, #fcd116 70%, #ce1126 100%);
    background-size: 200% 100%;
    border-radius: 999px;
    box-shadow: 0 0 14px rgba(15, 82, 186, 0.5);
    animation: psaBarSlide 2.1s cubic-bezier(0.4, 0, 0.2, 1) infinite, psaGradientShift 3.5s ease infinite;
}

.psa-progress-label {
    font-size: 0.84rem;
    font-weight: 500;
    color: #54607c;
    letter-spacing: 0.02em;
    display: flex;
    align-items: center;
    gap: 6px;
}

.psa-loading-dots {
    display: inline-flex;
    gap: 3.5px;
}

.psa-loading-dot {
    width: 4.5px;
    height: 4.5px;
    border-radius: 50%;
    background: #0f52ba;
    animation: psaDotBounce 1.4s infinite ease-in-out both;
}

.psa-loading-dot:nth-child(1) { animation-delay: -0.32s; }
.psa-loading-dot:nth-child(2) { animation-delay: -0.16s; }
.psa-loading-dot:nth-child(3) { animation-delay: 0s; }

/* --------------------------------------------------------------------------
   KEYFRAME ANIMATIONS
   -------------------------------------------------------------------------- */
@keyframes psaScreenFadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

@keyframes psaFloat {
    0%, 100% {
        transform: translateY(0px) scale(1);
    }
    50% {
        transform: translateY(-6px) scale(1.025);
    }
}

@keyframes psaGlowPulse {
    0% {
        transform: scale(0.9);
        opacity: 0.45;
    }
    100% {
        transform: scale(1.22);
        opacity: 0.85;
    }
}

@keyframes psaSpinRing {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

@keyframes psaBarSlide {
    0% {
        left: -40%;
        width: 30%;
    }
    50% {
        left: 30%;
        width: 55%;
    }
    100% {
        left: 100%;
        width: 30%;
    }
}

@keyframes psaGradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes psaDotBounce {
    0%, 80%, 100% {
        transform: scale(0);
        opacity: 0.25;
    }
    40% {
        transform: scale(1);
        opacity: 1;
    }
}
"""

def get_loading_screen_html() -> str:
    """Return the raw HTML structure for the custom loading screen inside react-entry-point."""
    seal_src = get_seal_data_uri()
    return f"""<div id="react-entry-point">
    <div class="_dash-loading psa-loading-screen" id="psa-app-loading-screen">
        <div class="psa-loading-card">
            <div class="psa-logo-container">
                <div class="psa-logo-glow"></div>
                <div class="psa-orbit-ring"></div>
                <img src="{seal_src}" alt="Philippine Statistics Authority" class="psa-logo-img" />
            </div>

            <div class="psa-loading-titles">
                <div class="psa-loading-agency">Philippine Statistics Authority</div>
                <div class="psa-loading-tagline">Solid &bull; Responsive &bull; World-class</div>
                <div class="psa-loading-brand-line"></div>
                <div class="psa-loading-subtitle">Population and Housing Statistics</div>
            </div>

            <div class="psa-progress-wrapper">
                <div class="psa-progress-track">
                    <div class="psa-progress-bar"></div>
                </div>
                <div class="psa-progress-label">
                    <span>Loading statistics dashboard</span>
                    <span class="psa-loading-dots">
                        <span class="psa-loading-dot"></span>
                        <span class="psa-loading-dot"></span>
                        <span class="psa-loading-dot"></span>
                    </span>
                </div>
            </div>
        </div>
    </div>
</div>"""

def setup_loading_screen(app) -> None:
    """
    Configure Dash app to render the animated PSA loading screen immediately
    on initial page request, before React mounts.
    """
    css_block = f"<style>{get_loading_screen_css()}</style>"
    entry_html = get_loading_screen_html()
    
    orig_interpolate = app.interpolate_index
    
    def custom_interpolate_index(**kwargs):
        # Inject critical CSS right at top of head for 0ms paint latency
        if 'css' in kwargs:
            kwargs['css'] = f"{css_block}\n{kwargs['css']}"
        else:
            kwargs['css'] = css_block
            
        # Replace default "Loading..." app_entry with animated PSA logo and loading bar
        kwargs['app_entry'] = entry_html
        return orig_interpolate(**kwargs)
        
    app.interpolate_index = custom_interpolate_index
