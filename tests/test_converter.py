# test_converter.py
import pytest
import os
from mermaid_to_drawio.converter_1 import MermaidToDrawIOConverter
from mermaid_to_drawio.layout_manager import LayoutManager

SAMPLE_MMD = """
subgraph Outer
    subgraph Inner
        A[Node A]
    end
    B[Node B]
end
A --> B
style A fill:red,stroke:black,stroke-width:2px
style B fill:#00ff00
linkStyle 0 stroke:blue,stroke-width:3px
"""

def test_group_nesting(tmp_path):
    file = tmp_path / "test.mmd"
    file.write_text(SAMPLE_MMD)
    
    converter = MermaidToDrawIOConverter(str(file))
    converter.parse_mermaid()
    
    # Verify groups
    assert len(converter.groups) == 2
    outer_name = next(v[0] for v in converter.groups.values() if v[0] == "Outer")
    inner_name = next(v[0] for v in converter.groups.values() if v[0] == "Inner")
    assert outer_name and inner_name
    
    # Verify node-group mapping
    assert converter.node_to_group["A"] in converter.groups
    assert converter.node_to_group["B"] in converter.groups
    
    # Verify styles
    assert "fill=#ff0000" in converter.styles["A"]
    assert "stroke=#000000" in converter.styles["A"]
    assert "strokeWidth=2" in converter.styles["A"]
    assert "fill=#00ff00" in converter.styles["B"]
    
    # Verify edge style
    assert "stroke=#0000ff" in converter.edge_styles[0]
    assert "strokeWidth=3" in converter.edge_styles[0]

def test_build_and_save(tmp_path):
    file = tmp_path / "test.mmd"
    output = tmp_path / "output.drawio"
    file.write_text(SAMPLE_MMD)
    
    converter = MermaidToDrawIOConverter(str(file), str(output))
    converter.parse_mermaid()
    converter.build()
    result = converter.save()
    
    assert result is True
    assert os.path.exists(output)
    assert os.path.getsize(output) > 0

def test_theme_application():
    mmd = "A[Test Node]"
    converter = MermaidToDrawIOConverter("dummy", theme={
        "node": {"fillColor": "#123456", "strokeColor": "#789abc", "strokeWidth": "3"},
        "edge": {"strokeColor": "#def012", "strokeWidth": "4"}
    })
    converter.nodes = {"A": "Test Node"}
    converter.shape_styles = {"A": "shape=rectangle"}
    converter._create_node("A", "Test Node", None)
    
    # Verify theme styles
    root = converter.root
    cell = root.find(".//mxCell[@id='A']")
    assert cell is not None
    style = cell.get("style", "")
    assert "fillColor=#123456" in style
    assert "strokeColor=#789abc" in style
    assert "strokeWidth=3" in style

