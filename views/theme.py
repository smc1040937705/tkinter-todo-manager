from typing import Dict, Tuple


class Theme:
    LIGHT = "light"
    DARK = "dark"
    
    COLORS: Dict[str, Dict[str, str]] = {
        LIGHT: {
            "bg": "#f5f5f5",
            "fg": "#333333",
            "card_bg": "#ffffff",
            "accent": "#2196F3",
            "accent_hover": "#1976D2",
            "success": "#4CAF50",
            "warning": "#FF9800",
            "danger": "#F44336",
            "border": "#e0e0e0",
            "input_bg": "#ffffff",
            "disabled": "#9e9e9e",
            "priority_low": "#8BC34A",
            "priority_medium": "#FFC107",
            "priority_high": "#F44336",
            "completed_fg": "#9e9e9e",
            "overdue_fg": "#F44336"
        },
        DARK: {
            "bg": "#1e1e1e",
            "fg": "#e0e0e0",
            "card_bg": "#2d2d2d",
            "accent": "#64B5F6",
            "accent_hover": "#42A5F5",
            "success": "#81C784",
            "warning": "#FFB74D",
            "danger": "#E57373",
            "border": "#424242",
            "input_bg": "#3d3d3d",
            "disabled": "#616161",
            "priority_low": "#AED581",
            "priority_medium": "#FFD54F",
            "priority_high": "#E57373",
            "completed_fg": "#616161",
            "overdue_fg": "#E57373"
        }
    }
    
    FONTS: Dict[str, Tuple[str, int, str]] = {
        "title": ("Microsoft YaHei UI", 14, "bold"),
        "subtitle": ("Microsoft YaHei UI", 12, "bold"),
        "normal": ("Microsoft YaHei UI", 10, "normal"),
        "small": ("Microsoft YaHei UI", 9, "normal"),
        "button": ("Microsoft YaHei UI", 10, "bold"),
        "todo_title": ("Microsoft YaHei UI", 11, "normal"),
        "todo_detail": ("Microsoft YaHei UI", 9, "normal")
    }
    
    def __init__(self, mode: str = LIGHT):
        self._mode = mode
        self._colors = self.COLORS[mode]
    
    @property
    def mode(self) -> str:
        return self._mode
    
    def toggle(self) -> str:
        self._mode = self.DARK if self._mode == self.LIGHT else self.LIGHT
        self._colors = self.COLORS[self._mode]
        return self._mode
    
    def get_color(self, key: str) -> str:
        return self._colors.get(key, self._colors["fg"])
    
    def get_font(self, key: str) -> Tuple[str, int, str]:
        return self.FONTS.get(key, self.FONTS["normal"])
    
    def get_all_colors(self) -> Dict[str, str]:
        return self._colors.copy()
    
    def get_style_config(self) -> dict:
        return {
            "window": {
                "bg": self.get_color("bg")
            },
            "frame": {
                "bg": self.get_color("bg")
            },
            "card": {
                "bg": self.get_color("card_bg"),
                "relief": "solid",
                "bd": 1
            },
            "label": {
                "bg": self.get_color("bg"),
                "fg": self.get_color("fg"),
                "font": self.get_font("normal")
            },
            "button": {
                "bg": self.get_color("accent"),
                "fg": "white",
                "font": self.get_font("button"),
                "relief": "flat",
                "cursor": "hand2"
            },
            "entry": {
                "bg": self.get_color("input_bg"),
                "fg": self.get_color("fg"),
                "font": self.get_font("normal"),
                "relief": "solid",
                "bd": 1
            },
            "listbox": {
                "bg": self.get_color("card_bg"),
                "fg": self.get_color("fg"),
                "font": self.get_font("normal"),
                "selectbackground": self.get_color("accent"),
                "relief": "solid",
                "bd": 1
            }
        }
