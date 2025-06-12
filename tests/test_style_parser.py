from mermaid_to_drawio.style_parser import StyleParser

def test_style_parsing():
    # Named colors
    assert StyleParser.parse("fill:red") == "fill=#ff0000"
    assert StyleParser.parse("stroke:green") == "stroke=#00ff00"
    
    # Hex colors
    assert StyleParser.parse("fill:#123456") == "fill=#123456"
    
    # RGB colors
    assert StyleParser.parse("color:rgb(255,0,0)") == "color=#ff0000"
    assert StyleParser.parse("color:rgba(0,255,0,0.5)") == "color=#00ff00"
    
    # Stroke properties
    assert StyleParser.parse("stroke-width:2px") == "strokeWidth=2"
    assert StyleParser.parse("stroke-dasharray:5") == "dashed=1"
    
    # Multiple properties
    result = StyleParser.parse("fill:blue; stroke:orange; stroke-width:3px")
    assert "fill=#0000ff" in result
    assert "stroke=#ffa500" in result
    assert "strokeWidth=3" in result