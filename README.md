# Mermaid to Draw.io Converter 🧩

Convert Mermaid diagrams (`graph TD` style) into fully styled, container-aware `.drawio` diagrams you can open in [draw.io](https://app.diagrams.net).

## 🚀 Features

✅ Converts Mermaid flowcharts to draw.io XML  
✅ Preserves node & edge styles (fill, stroke, width)  
✅ Parses edge labels like `-- Metrics -->`  
✅ Supports `subgraph` nesting and creates containers  
✅ CLI-friendly tool

---

## 📂 Project Structure

```bash
mermaid-to-drawio/
├── mermaid_to_drawio/
│   └── converter.py         # Copy-paste the full script here
├── examples/
│   └── sample_diagram.txt   # Sample Mermaid diagram
├── tests/
│   └── test_converter.py    # (Optional test placeholder)
├── README.md
├── requirements.txt
├── .gitignore

💻 Usage

1. Install Requirements:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

2. Run the Script
python mermaid_to_drawio/converter.py examples/sample_diagram.txt
# or with a custom output name:
python mermaid_to_drawio/converter.py examples/sample_diagram.txt -o my_diagram.drawio

3. 🧪 Testing

Example with pytest:

pip install pytest
pytest tests/
