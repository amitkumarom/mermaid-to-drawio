import argparse
import re
import uuid
import logging
import xml.etree.ElementTree as ET
import xml.dom.minidom
from mermaid_to_drawio.layout_manager import LayoutManager
from mermaid_to_drawio.style_parser import StyleParser

logger = logging.getLogger(__name__)

SHAPE_MAP = {
    "rectangle": "shape=rectangle",
    "rounded": "shape=rectangle;rounded=1",
    "ellipse": "shape=ellipse",
    "parallelogram": "shape=parallelogram",
    "rhombus": "shape=rhombus",
    "cylinder": "shape=cylinder",
    "circle": "shape=ellipse",  # Alias
    "hexagon": "shape=hexagon",
}

class MermaidToDrawIOConverter:
    def __init__(self, input_file, output_file=None, theme=None):
        self.input_file = input_file
        self.output_file = output_file or input_file.rsplit(".", 1)[0] + ".drawio"
        self.theme = theme or {
            "node": {"fillColor": "#ffffff", "strokeColor": "#333333", "strokeWidth": "1"},
            "edge": {"strokeColor": "#666666", "strokeWidth": "2"}
        }
        self.nodes = {}
        self.edges = []
        self.styles = {}
        self.shape_styles = {}
        self.groups = {}
        self.node_to_group = {}
        self.group_stack = []
        self.edge_styles = {}
        self.layout_manager = LayoutManager()
        
        self.mxfile = ET.Element("mxfile", host="app.diagrams.net")
        self.diagram = ET.SubElement(self.mxfile, "diagram", name="Mermaid Diagram")
        self.graph_model = ET.SubElement(self.diagram, "mxGraphModel")
        self.root = ET.SubElement(self.graph_model, "root")
        ET.SubElement(self.root, "mxCell", id="0")
        ET.SubElement(self.root, "mxCell", id="1", parent="0")

    def generate_id(self):
        return str(uuid.uuid4()).replace("-", "")[:10]

    def parse_mermaid(self):
        try:
            with open(self.input_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            edge_index = 0
            for line in lines:
                line = line.strip()
                if not line or line.startswith("%%") or line.startswith("direction"):
                    continue
                    
                # Handle subgraphs
                if line.startswith("subgraph"):
                    self._handle_subgraph(line)
                    continue
                    
                # Handle group end
                if line == "end":
                    if self.group_stack:
                        self.group_stack.pop()
                    continue
                    
                # Handle node declarations
                if self._parse_node(line):
                    continue
                    
                # Handle styles
                if self._parse_style(line):
                    continue
                    
                # Handle edges
                if self._parse_edge(line, edge_index):
                    edge_index += 1
                    continue
                    
                # Handle edge styles
                if self._parse_edge_style(line):
                    continue

        except Exception as e:
            logger.error(f"Error parsing Mermaid: {e}")
            raise

    def _handle_subgraph(self, line):
        group_name = line[len("subgraph"):].strip()
        group_id = self.generate_id()
        parent_id = self.group_stack[-1] if self.group_stack else None
        self.groups[group_id] = (group_name, parent_id)
        self.group_stack.append(group_id)

    def _parse_node(self, line):
        patterns = [
            (r"(\w+)\[(.+?)\]", "rectangle"),
            (r"(\w+)\((.+?)\)", "rounded"),
            (r"(\w+)\(\((.+?)\)\)", "ellipse"),
            (r"(\w+)>([^\]\[]+)\]", "parallelogram"),
            (r"(\w+)\{([^}]+)\}", "rhombus"),
            (r"(\w+)\[\[(.+?)\]\]", "cylinder"),
            (r"(\w+)\(\(\((.+?)\)\)\)", "hexagon"),
        ]
        
        for pattern, shape in patterns:
            match = re.match(pattern, line)
            if match:
                node_id, label = match.groups()
                self.nodes[node_id] = label
                self.shape_styles[node_id] = SHAPE_MAP[shape]
                if self.group_stack:
                    self.node_to_group[node_id] = self.group_stack[-1]
                self.layout_manager.add_node(node_id)
                return True
        return False

    def _parse_style(self, line):
        match = re.match(r"style\s+(\w+)\s+(.*)", line)
        if match:
            node_id, style_str = match.groups()
            self.styles[node_id] = StyleParser.parse(style_str)
            return True
        return False

    def _parse_edge(self, line, edge_index):
        patterns = [
            (r"(\w+)\s*--\s*(.*?)\s*-->\s*(\w+)", True),   # Labeled edge
            (r"(\w+)\s*-->\s*(\w+)", False),               # Simple edge
            (r"(\w+)\s*<-->\s*(\w+)", False)               # Bidirectional
        ]
        
        for pattern, has_label in patterns:
            match = re.match(pattern, line)
            if match:
                groups = match.groups()
                if has_label:
                    src, label, tgt = groups
                else:
                    src, tgt = groups
                    label = ""
                
                self._add_edge(src, tgt, label, edge_index)
                if " <--> " in line:  # Bidirectional
                    self._add_edge(tgt, src, "", edge_index + 1)
                    edge_index += 1
                return True
        return False

    def _parse_edge_style(self, line):
        match = re.match(r"linkStyle\s+(\d+)\s+(.*)", line)
        if match:
            idx, style_str = match.groups()
            self.edge_styles[int(idx)] = StyleParser.parse(style_str)
            return True
        return False

    def _add_edge(self, src, tgt, label, edge_index):
        self.edges.append((src, tgt, label, edge_index))
        self.nodes.setdefault(src, src)
        self.nodes.setdefault(tgt, tgt)
        self.layout_manager.add_node(src)
        self.layout_manager.add_node(tgt)

    def build(self):
        # Create groups
        group_elements = {}
        for gid, (name, parent_id) in self.groups.items():
            group_elements[gid] = self._create_group(gid, name, parent_id)
        
        # Create nodes
        for node_id, label in self.nodes.items():
            group_id = self.node_to_group.get(node_id)
            self._create_node(node_id, label, group_id)
        
        # Adjust group geometries
        for gid, (geom, _) in group_elements.items():
            bbox = self.layout_manager.get_group_bbox(gid)
            if bbox:
                geom.attrib.update({
                    "x": str(bbox[0]),
                    "y": str(bbox[1]),
                    "width": str(bbox[2]),
                    "height": str(bbox[3])
                })
        
        # Create edges
        for src, tgt, label, edge_idx in self.edges:
            self._create_edge(src, tgt, label, edge_idx)

    def _create_group(self, gid, name, parent_id=None):
        parent = parent_id or "1"
        cell = ET.SubElement(self.root, "mxCell", {
            "id": gid,
            "value": name,
            "style": "swimlane;collapsible=0;",
            "vertex": "1",
            "parent": parent
        })
        geom = ET.SubElement(cell, "mxGeometry", {
            "x": "0", "y": "0", "width": "100", "height": "100", "as": "geometry"
        })
        return geom, cell

    def _create_node(self, node_id, label, group_id=None):
        base_style = self.shape_styles.get(node_id, SHAPE_MAP["rectangle"])
        custom_style = self.styles.get(node_id, "")
        theme_style = f"fillColor={self.theme['node']['fillColor']};strokeColor={self.theme['node']['strokeColor']};strokeWidth={self.theme['node']['strokeWidth']}"
        style = f"{base_style};{theme_style};{custom_style}"
        
        x, y = self.layout_manager.get_position(node_id)
        parent = group_id or "1"
        
        cell = ET.SubElement(self.root, "mxCell", {
            "id": node_id,
            "value": label,
            "style": style,
            "vertex": "1",
            "parent": parent
        })
        ET.SubElement(cell, "mxGeometry", {
            "x": str(x), "y": str(y), "width": "180", "height": "60", "as": "geometry"
        })
        self.layout_manager.add_node_to_group(group_id, node_id, x, y, 180, 60)
        return cell

    def _create_edge(self, src, tgt, label, edge_idx):
        default_style = f"endArrow=block;strokeColor={self.theme['edge']['strokeColor']};strokeWidth={self.theme['edge']['strokeWidth']}"
        custom_style = self.edge_styles.get(edge_idx, "")
        style = f"{default_style};{custom_style}"
        
        edge = ET.SubElement(self.root, "mxCell", {
            "value": label,
            "style": style,
            "edge": "1",
            "source": src,
            "target": tgt,
            "parent": "1"
        })
        ET.SubElement(edge, "mxGeometry", {"relative": "1", "as": "geometry"})
        return edge

    def save(self):
        try:
            xml_str = ET.tostring(self.mxfile, encoding="utf-8")
            pretty = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="  ")
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(pretty)
            logger.info(f"Saved Draw.io file: {self.output_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Convert Mermaid to Draw.io")
    parser.add_argument("input", help="Mermaid input file")
    parser.add_argument("-o", "--output", help="Draw.io output file")
    parser.add_argument("--theme", choices=["light", "dark", "default"], default="light", help="Color theme")
    args = parser.parse_args()

    themes = {
        "light": {
            "node": {"fillColor": "#ffffff", "strokeColor": "#333333", "strokeWidth": "1"},
            "edge": {"strokeColor": "#666666", "strokeWidth": "2"}
        },
        "dark": {
            "node": {"fillColor": "#333333", "strokeColor": "#f0f0f0", "strokeWidth": "1"},
            "edge": {"strokeColor": "#aaaaaa", "strokeWidth": "2"}
        },
        "default": {
            "node": {"fillColor": "#DAE8FC", "strokeColor": "#333333", "strokeWidth": "1"},
            "edge": {"strokeColor": "#666666", "strokeWidth": "2"}
        }
        
    }

    converter = MermaidToDrawIOConverter(
        args.input, 
        args.output, 
        theme=themes[args.theme]
    )
    
    try:
        converter.parse_mermaid()
        converter.build()
        converter.save()
    except Exception as e:
        logger.error(f"Conversion failed: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()