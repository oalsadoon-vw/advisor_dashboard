"""
Monthly theme registry for the Advisor Satisfaction Dashboard.

Each theme is a self-contained "skin": full color palette, fonts, icon set,
decorative background, and hero banner text. Swapping the ACTIVE_THEME
value (or the THEME_NAME env var) changes the entire look of the dashboard
without touching any data logic in streamlit_app.py.

To add next month's theme: copy a THEME dict below, tweak values, add its
key to THEMES, and set ACTIVE_THEME (or THEME_NAME env var) to that key.
"""

import os

# ============================================================================
# THEME DEFINITIONS
# ============================================================================

THEMES = {
    "default": {
        "label": "Classic",
        "banner_title": "Advisor Satisfaction Dashboard",
        "banner_icon": "📊",
        "bg_gradient": "linear-gradient(160deg, #FFFFFF, #F9FAFB)",
        "bg0": "#FFFFFF",
        "bg1": "#F9FAFB",
        "card": "#F3F4F6",
        "line": "#E5E7EB",
        "text": "#111827",
        "muted": "#6B7280",
        "gold": "#F59E0B",
        "silver": "#9CA3AF",
        "bronze": "#D97706",
        "good": "#10B981",
        "bad": "#EF4444",
        "accent": "#3B82F6",
        "card_gradient": "linear-gradient(180deg, #FFFFFF, #F9FAFB)",
        "font_import": "",
        "font_family": "inherit",
        "rank_icons": {1: "🥇", 2: "🥈", 3: "🥉"},
        "decoration_css": "",
        "decoration_html": "",
    },
    "july_4th": {
        "label": "4th of July",
        "banner_title": "Independence Day Service Rankings",
        "banner_icon": "🎆",
        "bg_gradient": "linear-gradient(160deg, #0B1F3A 0%, #13294B 55%, #0B1F3A 100%)",
        "bg0": "#0F2645",
        "bg1": "#132E52",
        "card": "#152F55",
        "line": "#3A5A8C",
        "text": "#F5F8FF",
        "muted": "#AFC2E8",
        "gold": "#FFD700",
        "silver": "#E8ECF5",
        "bronze": "#FF6B6B",
        "good": "#3ED17A",
        "bad": "#FF5A5F",
        "accent": "#FF3B47",
        "card_gradient": "linear-gradient(180deg, #16336099, #0F264599)",
        "font_import": "@import url('https://fonts.googleapis.com/css2?family=Rye&family=Inter:wght@400;700;800;950&display=swap');",
        "font_family": "'Inter', sans-serif",
        "display_font_family": "'Rye', serif",
        "rank_icons": {1: "🥇", 2: "🥈", 3: "🥉"},
        # Twinkling stars + soft firework bursts, pure CSS, no external images
        "decoration_css": """
        @keyframes twinkle {
            0%, 100% { opacity: 0.15; transform: scale(0.8); }
            50% { opacity: 0.9; transform: scale(1.15); }
        }
        @keyframes drift {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-8px); }
            100% { transform: translateY(0px); }
        }
        .theme-star {
            position: fixed;
            color: #FFFFFF;
            font-size: 14px;
            animation: twinkle 3.5s ease-in-out infinite;
            pointer-events: none;
            z-index: 0;
            opacity: 0.6;
        }
        .theme-firework {
            position: fixed;
            font-size: 34px;
            animation: drift 6s ease-in-out infinite;
            pointer-events: none;
            z-index: 0;
            opacity: 0.85;
        }
        .theme-banner {
            border-radius: 16px;
            padding: 18px 26px;
            margin-bottom: 14px;
            background: linear-gradient(120deg, #B22234 0%, #16335f 45%, #0B1F3A 100%);
            box-shadow: 0 6px 22px rgba(0,0,0,0.35);
            border: 1px solid #3A5A8C;
            position: relative;
            overflow: hidden;
        }
        .theme-banner::after {
            content: '';
            position: absolute;
            inset: 0;
            background-image: radial-gradient(circle, rgba(255,255,255,0.12) 1px, transparent 1px);
            background-size: 14px 14px;
        }
        .theme-banner-title {
            font-family: 'Rye', serif;
            font-size: clamp(24px, 3vw, 40px);
            color: #FFFFFF;
            text-shadow: 0 2px 10px rgba(0,0,0,0.5);
            position: relative;
            z-index: 1;
            letter-spacing: 0.5px;
        }
        """,
        "decoration_html": """
        <div class="theme-star" style="top:6%; left:8%;">✦</div>
        <div class="theme-star" style="top:14%; left:22%; animation-delay:1s;">✦</div>
        <div class="theme-star" style="top:9%; left:41%; animation-delay:2s;">✦</div>
        <div class="theme-star" style="top:18%; left:63%; animation-delay:0.5s;">✦</div>
        <div class="theme-star" style="top:7%; left:80%; animation-delay:1.5s;">✦</div>
        <div class="theme-star" style="top:22%; left:92%; animation-delay:2.5s;">✦</div>
        <div class="theme-firework" style="top:2%; left:3%;">🎇</div>
        <div class="theme-firework" style="top:3%; right:4%; animation-delay:2s;">🎆</div>
        """,
    },
}

# Active theme is chosen by env var so the monthly cron job can flip it
# without editing code: THEME_NAME=july_4th streamlit run streamlit_app.py
ACTIVE_THEME_KEY = os.environ.get("THEME_NAME", "july_4th")
ACTIVE_THEME = THEMES.get(ACTIVE_THEME_KEY, THEMES["default"])


def get_theme():
    """Return the active theme dict (falls back to default if key unknown)."""
    return ACTIVE_THEME


def rank_icon(rank, theme=None):
    theme = theme or ACTIVE_THEME
    icons = theme.get("rank_icons", {})
    return icons.get(rank, "")
