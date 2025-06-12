from setuptools import setup

setup(
    name="mermaid-to-drawio",
    version="0.1.0",
    description="Convert Mermaid diagrams to Draw.io XML",
    author="Your Name",
    packages=["mermaid_to_drawio"],
    entry_points={
        "console_scripts": [
            "mermaid2drawio=mermaid_to_drawio.converter:main"
        ]
    },
    python_requires='>=3.7',
)
