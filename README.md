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
│   └── converter.py         # Conversion logic
├── examples/
│   └── sample_diagram.txt   # Mermaid sample
├── README.md
├── requirements.txt
