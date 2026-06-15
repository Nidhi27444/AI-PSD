BG = "#050B16"
PANEL = "#0B1322"
BORDER = "#23324A"
TEXT = "#F5F7FA"
MUTED = "#9FB0C8"
ACCENT = "#00A3FF"
ACCENT_2 = "#39B8FF"
GOOD = "#18C37E"
WARN = "#FFB020"
BAD = "#FF5A5F"

BLUE_DARK = "#0066CC"
BLUE_MEDIUM = "#3399FF"
BLUE_LIGHT = "#99CCFF"

GREEN_DARK = "#0F2B9D"
GREEN_MEDIUM = "#18C37E"
GREEN_LIGHT = "#7EE2B8"

RED_DARK = "#CC2B2B"
RED_MEDIUM = "#FF5A5F"
RED_LIGHT = "#FF9999"

PLOTLY_CHART_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    "toImageButtonOptions": {
        "format": "png",
        "filename": "parking_spot_chart",
        "height": 700,
        "width": 1200,
        "scale": 2,
    },
}

SPOT_ORDER = [
    "LongSpotLeft",
    "PerpSpotLeft",
    "DiagSpotLeft",
    "LongSpotRight",
    "PerpSpotRight",
    "DiagSpotRight",
]

SPOT_LABELS = {
    "LongSpotLeft": "LongSpot (Left)",
    "PerpSpotLeft": "Perpendicular (Left)",
    "DiagSpotLeft": "Diagonal (Left)",
    "LongSpotRight": "LongSpot (Right)",
    "PerpSpotRight": "Perpendicular (Right)",
    "DiagSpotRight": "Diagonal (Right)",
}