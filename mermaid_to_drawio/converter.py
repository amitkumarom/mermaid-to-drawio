import xml.etree.ElementTree as ET
import xml.dom.minidom
import argparse
import re
import uuid

class MermaidToDrawIOConverter:
    def __init__(self, input_file, output_file=None):
        self.input_file = input_file
        self.output_file = output_file or input_file.rsplit(".", 1)[0] + ".drawio"
        self.nodes = {}
        self.edges = []  # (src, tgt, label)
        self.styles = {}
        self.groups = {}  # group_id: group_name
        self.node_to_group = {}  # node_id: group_id
        self.group_stack = []  # subgraph nesting
        self.positions = {}
        self.counter = 0
        self.x_gap, self.y_gap = 220, 80
        self.x_offset, self.y_offset = 60, 60

        # XML init
        self.mxfile = ET.Element("mxfile", host="app.diagrams.net")
        self.diagram = ET.SubElement(self.mxfile, "diagram", name="Mermaid Diagram")
        self.graph_model = ET.SubElement(self.diagram, "mxGraphModel")
        self.root = ET.SubElement(self.graph_model, "root")
        ET.SubElement(self.root, "mxCell", id="0")
        ET.SubElement(self.root, "mxCell", id="1", parent="0")

    def generate_group_id(self):
        return "group_" + str(uuid.uuid4()).replace("-", "")[:8]

    def parse_mermaid(self):
        with open(self.input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith("direction"):
                continue

            # Start of subgraph
            if line.startswith("subgraph"):
                group_name = line[len("subgraph"):].strip()
                group_id = self.generate_group_id()
                self.groups[group_id] = group_name
                self.group_stack.append(group_id)
                continue

            # End of subgraph
            if line == "end":
                if self.group_stack:
                    self.group_stack.pop()
                continue

            # Node declaration
            match_node = re.match(r"(\w+)\[(.+?)\]", line)
            if match_node:
                nid, label = match_node.groups()
                self.nodes[nid] = label
                if self.group_stack:
                    self.node_to_group[nid] = self.group_stack[-1]
                continue

            # Style line
            match_style = re.match(r"style\s+(\w+)\s+(.*)", line)
            if match_style:
                nid, style_str = match_style.groups()
                style_map = {}
                style_str = style_str.replace(",", ";")
                for part in style_str.split(";"):
                    if ":" in part:
                        k, v = part.split(":", 1)
                        style_map[k.strip()] = v.strip()
                style = "shape=rectangle"
                if "fill" in style_map:
                    style += f";fillColor={style_map['fill']}"
                if "stroke" in style_map:
                    style += f";strokeColor={style_map['stroke']}"
                if "stroke-width" in style_map:
                    style += f";strokeWidth={style_map['stroke-width'].replace('px', '')}"
                self.styles[nid] = style
                continue

            # Edge with label
            match_edge = re.match(r"(\w+)\s*--\s*(.*?)\s*-->\s*(\w+)", line)
            if match_edge:
                src, label, tgt = match_edge.groups()
                self.edges.append((src, tgt, label.strip()))
                self.nodes.setdefault(src, src)
                self.nodes.setdefault(tgt, tgt)
                continue

            # Simple edge
            match_edge_simple = re.match(r"(\w+)\s*-->\s*(\w+)", line)
            if match_edge_simple:
                src, tgt = match_edge_simple.groups()
                self.edges.append((src, tgt, ""))
                self.nodes.setdefault(src, src)
                self.nodes.setdefault(tgt, tgt)
                continue

            # Bidirectional edge
            match_edge_bi = re.match(r"(\w+)\s*<-->\s*(\w+)", line)
            if match_edge_bi:
                src, tgt = match_edge_bi.groups()
                self.edges.append((src, tgt, ""))
                self.edges.append((tgt, src, ""))
                self.nodes.setdefault(src, src)
                self.nodes.setdefault(tgt, tgt)
                continue

    def get_position(self, nid):
        if nid in self.positions:
            return self.positions[nid]
        x = self.x_offset + (self.counter // 20) * self.x_gap
        y = self.y_offset + (self.counter % 20) * self.y_gap
        self.positions[nid] = (x, y)
        self.counter += 1
        return x, y

    def add_group(self, gid, label):
        group_cell = ET.SubElement(self.root, "mxCell", {
            "id": gid,
            "value": label,
            "style": "swimlane;collapsible=0;",
            "vertex": "1",
            "parent": "1"
        })
        ET.SubElement(group_cell, "mxGeometry", {
            "x": str(50 + len(self.groups) * 20),
            "y": str(50 + len(self.groups) * 20),
            "width": "1600",
            "height": "1200",
            "as": "geometry"
        })

    def add_node(self, nid, label, parent=None):
        style = self.styles.get(nid, "shape=rectangle;fillColor=#ffffff;strokeColor=#333;strokeWidth=1")
        x, y = self.get_position(nid)
        attr = {
            "id": nid,
            "value": label,
            "style": style,
            "vertex": "1",
            "parent": parent if parent else "1"
        }
        cell = ET.SubElement(self.root, "mxCell", attr)
        ET.SubElement(cell, "mxGeometry", {
            "x": str(x),
            "y": str(y),
            "width": "180",
            "height": "60",
            "as": "geometry"
        })

    def add_edge(self, src, tgt, label):
        edge = ET.SubElement(self.root, "mxCell", {
            "value": label,
            "style": "endArrow=block;",
            "edge": "1",
            "source": src,
            "target": tgt,
            "parent": "1"
        })
        ET.SubElement(edge, "mxGeometry", {"relative": "1", "as": "geometry"})

    def build(self):
        for gid, label in self.groups.items():
            self.add_group(gid, label)

        for nid, label in self.nodes.items():
            parent = self.node_to_group.get(nid)
            self.add_node(nid, label, parent)

        for src, tgt, label in self.edges:
            self.add_edge(src, tgt, label)

    def save(self):
        xml_str = ET.tostring(self.mxfile, encoding="utf-8")
        pretty = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="  ")
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(pretty)
        print(f"✅ Draw.io file saved to: {self.output_file}")

def main():
    parser = argparse.ArgumentParser(description="Convert Mermaid diagram to draw.io with full grouping and styles")
    parser.add_argument("input", help="Path to Mermaid .txt file")
    parser.add_argument("-o", "--output", help="Optional output file name (.drawio)")
    args = parser.parse_args()

    converter = MermaidToDrawIOConverter(args.input, args.output)
    converter.parse_mermaid()
    converter.build()
    converter.save()

if __name__ == "__main__":
    main()
