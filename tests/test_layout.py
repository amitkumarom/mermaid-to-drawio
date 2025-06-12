import pytest
from mermaid_to_drawio.layout_manager import LayoutManager

def test_node_positioning():
    layout = LayoutManager()
    layout.add_node("A")
    layout.add_node("B")
    layout.add_node("C")
    
    pos_a = layout.get_position("A")
    pos_b = layout.get_position("B")
    pos_c = layout.get_position("C")
    
    assert pos_a == (60, 60)
    assert pos_b == (60, 140)
    assert pos_c == (60, 220)

def test_group_bbox():
    layout = LayoutManager()
    layout.add_node_to_group("G1", "A", 100, 100, 180, 60)
    layout.add_node_to_group("G1", "B", 200, 200, 180, 60)
    layout.add_node_to_group("G1", "C", 150, 300, 180, 60)
    
    bbox = layout.get_group_bbox("G1")
    assert bbox == [80, 80, 220, 260]  # With padding

def test_group_with_single_node():
    layout = LayoutManager()
    layout.add_node_to_group("G1", "A", 100, 100, 180, 60)
    bbox = layout.get_group_bbox("G1")
    assert bbox == [80, 80, 140, 100]  # (100-20, 100-20, 180+40, 60+40)

