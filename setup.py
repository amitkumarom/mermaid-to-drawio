from setuptools import setup, find_packages

setup(
    name='mermaid-to-drawio',
    version='0.1.0',
    description='Convert Mermaid diagrams to Draw.io XML format',
    author='Amit Kumar',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],
    entry_points={
        'console_scripts': [
            'mermaid2drawio=mermaid_to_drawio.converter:main'
        ]
    },
)

