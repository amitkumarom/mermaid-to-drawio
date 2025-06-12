import re

class StyleParser:
    COLOR_MAP = {
        "red": "#ff0000",
        "green": "#00ff00",
        "blue": "#0000ff",
        "yellow": "#ffff00",
        "black": "#000000",
        "white": "#ffffff",
        "gray": "#808080",
        "grey": "#808080",
        "orange": "#ffa500",
        "purple": "#800080",
        "pink": "#ffc0cb",
        "brown": "#a52a2a",
        "cyan": "#00ffff",
        "magenta": "#ff00ff",
        "lime": "#00ff00",
        "maroon": "#800000",
        "olive": "#808000",
        "teal": "#008080",
        "navy": "#000080",
    }

    @staticmethod
    def parse(style_str):
        style_str = style_str.replace(",", ";")
        parts = style_str.split(";")
        style_parts = []
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            if ":" in part:
                key, value = part.split(":", 1)
                key = key.strip()
                value = value.strip()
                
                # Handle color names
                if key in ["fill", "stroke", "color"]:
                    value = StyleParser.resolve_color(value)
                
                # Convert CSS properties to Draw.io equivalents
                if key == "stroke-width":
                    key = "strokeWidth"
                    value = value.replace("px", "")
                elif key == "stroke-dasharray":
                    key = "dashed"
                    value = "1" if value != "0" else "0"
                
                style_parts.append(f"{key}={value}")
            else:
                style_parts.append(part)
                
        return ";".join(style_parts)
    
    @staticmethod
    def resolve_color(color):
        # Convert named colors to hex
        if color.lower() in StyleParser.COLOR_MAP:
            return StyleParser.COLOR_MAP[color.lower()]
        
        # Handle rgb/rgba formats
        if color.startswith("rgb"):
            return StyleParser.rgb_to_hex(color)
            
        return color
    
    @staticmethod
    def rgb_to_hex(rgb_str):
        match = re.match(r"rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*[\d.]+)?\)", rgb_str)
        if match:
            r, g, b = match.groups()[:3]
            return f"#{int(r):02x}{int(g):02x}{int(b):02x}"
        return rgb_str