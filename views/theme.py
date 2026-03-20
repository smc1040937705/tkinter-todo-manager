"""
主题配置模块 - 支持浅色/深色主题
"""


class Theme:
    """主题配置类"""

    # 浅色主题配色
    LIGHT = {
        "name": "light",
        "bg_primary": "#ffffff",           # 主背景
        "bg_secondary": "#f5f5f5",         # 次背景
        "bg_tertiary": "#e8e8e8",          # 第三层背景
        "fg_primary": "#212121",           # 主文字
        "fg_secondary": "#757575",         # 次文字
        "fg_disabled": "#bdbdbd",          # 禁用文字
        "accent": "#2196f3",               # 强调色
        "accent_hover": "#1976d2",         # 强调色悬停
        "success": "#4caf50",              # 成功
        "warning": "#ff9800",              # 警告
        "error": "#f44336",                # 错误
        "border": "#e0e0e0",               # 边框
        "border_focus": "#2196f3",         # 聚焦边框
        "priority_high": "#f44336",        # 高优先级
        "priority_medium": "#ff9800",      # 中优先级
        "priority_low": "#4caf50",         # 低优先级
        "category_work": "#2196f3",        # 工作分类
        "category_study": "#9c27b0",       # 学习分类
        "category_life": "#4caf50",        # 生活分类
    }

    # 深色主题配色
    DARK = {
        "name": "dark",
        "bg_primary": "#1e1e1e",           # 主背景
        "bg_secondary": "#2d2d2d",         # 次背景
        "bg_tertiary": "#3d3d3d",          # 第三层背景
        "fg_primary": "#ffffff",           # 主文字
        "fg_secondary": "#b0b0b0",         # 次文字
        "fg_disabled": "#666666",          # 禁用文字
        "accent": "#64b5f6",               # 强调色
        "accent_hover": "#42a5f5",         # 强调色悬停
        "success": "#81c784",              # 成功
        "warning": "#ffb74d",              # 警告
        "error": "#e57373",                # 错误
        "border": "#424242",               # 边框
        "border_focus": "#64b5f6",         # 聚焦边框
        "priority_high": "#e57373",        # 高优先级
        "priority_medium": "#ffb74d",      # 中优先级
        "priority_low": "#81c784",         # 低优先级
        "category_work": "#64b5f6",        # 工作分类
        "category_study": "#ba68c8",       # 学习分类
        "category_life": "#81c784",        # 生活分类
    }

    # 字体配置
    FONTS = {
        "family": "Microsoft YaHei UI",
        "family_mono": "Consolas",
        "size_small": 10,
        "size_normal": 11,
        "size_medium": 12,
        "size_large": 14,
        "size_xlarge": 16,
        "weight_normal": "normal",
        "weight_bold": "bold",
    }

    def __init__(self, theme_name="light"):
        self._theme = self.LIGHT if theme_name == "light" else self.DARK
        self._fonts = self.FONTS.copy()

    @property
    def colors(self):
        """获取当前主题颜色"""
        return self._theme

    @property
    def fonts(self):
        """获取字体配置"""
        return self._fonts

    def get_color(self, key):
        """获取指定颜色"""
        return self._theme.get(key, self._theme["fg_primary"])

    def get_font(self, size="normal", weight="normal", family="default"):
        """获取字体配置字符串"""
        font_family = self._fonts["family"] if family == "default" else self._fonts["family_mono"]
        font_size = self._fonts.get(f"size_{size}", self._fonts["size_normal"])
        font_weight = self._fonts.get(f"weight_{weight}", self._fonts["weight_normal"])
        return (font_family, font_size, font_weight)

    def set_theme(self, theme_name):
        """切换主题"""
        self._theme = self.LIGHT if theme_name == "light" else self.DARK

    def is_dark(self):
        """检查是否为深色主题"""
        return self._theme["name"] == "dark"

    def toggle(self):
        """切换主题"""
        self.set_theme("dark" if self._theme["name"] == "light" else "light")


# 全局主题实例
theme = Theme("light")


def get_theme():
    """获取全局主题实例"""
    return theme


def set_theme(theme_name):
    """设置全局主题"""
    global theme
    theme.set_theme(theme_name)


def toggle_theme():
    """切换全局主题"""
    global theme
    theme.toggle()
