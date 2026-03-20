from typing import Dict, Any

class Theme:
    LIGHT = 'light'
    DARK = 'dark'

    _themes: Dict[str, Dict[str, Any]] = {
        'light': {
            'bg': '#f5f5f5',
            'fg': '#212121',
            'card_bg': '#ffffff',
            'card_border': '#e0e0e0',
            'primary': '#2196f3',
            'primary_hover': '#1976d2',
            'success': '#4caf50',
            'warning': '#ff9800',
            'danger': '#f44336',
            'danger_hover': '#d32f2f',
            'completed': '#9e9e9e',
            'overdue': '#f44336',
            'high_priority': '#f44336',
            'medium_priority': '#ff9800',
            'low_priority': '#4caf50',
            'input_bg': '#ffffff',
            'input_border': '#bdbdbd',
            'scrollbar': '#bdbdbd',
            'scrollbar_track': '#f5f5f5',
        },
        'dark': {
            'bg': '#121212',
            'fg': '#e0e0e0',
            'card_bg': '#1e1e1e',
            'card_border': '#424242',
            'primary': '#64b5f6',
            'primary_hover': '#42a5f5',
            'success': '#81c784',
            'warning': '#ffb74d',
            'danger': '#e57373',
            'danger_hover': '#ef5350',
            'completed': '#757575',
            'overdue': '#e57373',
            'high_priority': '#e57373',
            'medium_priority': '#ffb74d',
            'low_priority': '#81c784',
            'input_bg': '#2d2d2d',
            'input_border': '#616161',
            'scrollbar': '#616161',
            'scrollbar_track': '#1e1e1e',
        }
    }

    _fonts: Dict[str, Any] = {
        'family': 'Microsoft YaHei UI',
        'size': {
            'small': 9,
            'normal': 10,
            'medium': 12,
            'large': 14,
            'title': 18,
        }
    }

    @classmethod
    def get_colors(cls, theme_name: str) -> Dict[str, str]:
        return cls._themes.get(theme_name, cls._themes['light']).copy()

    @classmethod
    def get_font(cls, size: str = 'normal', bold: bool = False) -> tuple:
        font_family = cls._fonts['family']
        font_size = cls._fonts['size'].get(size, 10)
        if bold:
            return (font_family, font_size, 'bold')
        return (font_family, font_size)

    @classmethod
    def get_priority_color(cls, colors: Dict[str, str], priority: str) -> str:
        priority_map = {
            '高': 'high_priority',
            '中': 'medium_priority',
            '低': 'low_priority'
        }
        return colors.get(priority_map.get(priority, 'medium_priority'), colors['warning'])

    @classmethod
    def get_themes(cls) -> list:
        return list(cls._themes.keys())