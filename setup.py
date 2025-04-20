#!/usr/bin/env python

import platform
from setuptools import setup, find_packages

# Long description with notes about PDF generation dependencies
long_description = """
# Land Evaluation Tool

A CrewAI-based system for evaluating land listing opportunities by analyzing property data, environmental factors, growth trends, housing occupancy, and socio-economic indicators.

## PDF Report Generation Dependencies

For PDF report generation functionality, additional dependencies are required:

### macOS:
1. Install WeasyPrint dependencies with Homebrew:
```
brew install cairo pango gdk-pixbuf libffi
```
2. Install the package with PDF extras:
```
pip install -e .[pdf]
```

### Linux (Ubuntu/Debian):
1. Install WeasyPrint dependencies:
```
apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```
2. Install the package with PDF extras:
```
pip install -e .[pdf]
```

### Windows:
```
pip install -e .[pdf]
```
See WeasyPrint documentation for additional system dependencies: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows
"""

# Base dependencies
install_requires = [
    "crewai>=0.28.4",
    "crewai_tools>=0.1.6",
    "pandas>=2.2.0",
    "tabulate>=0.9.0",
    "python-dotenv>=1.0.0",
    "numpy>=1.26.3",
    "openai>=1.12.0",
    "cryptography>=42.0.2",
    "langchain>=0.1.4",
    "langchain-community>=0.0.20",
    "chromadb>=0.4.22",
]

# PDF generation extras
pdf_requires = [
    "weasyprint>=60.2",
    "markdown>=3.5.2",
    "mdformat>=0.7.17",
    "jinja2>=3.1.3",
    "Pillow>=10.2.0",
]

# macOS specific message
if platform.system() == "Darwin":
    # Add macOS specific note to ensure user installs system dependencies
    print("\n*** macOS System Dependencies Notice ***")
    print("For PDF report generation, you'll need to install these dependencies:")
    print("  brew install cairo pango gdk-pixbuf libffi")
    print("Then install with: pip install -e .[pdf]\n")

setup(
    name="land_eval",
    version="1.0.0",
    description="A CrewAI-based system for evaluating land listing opportunities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ADLA Land Evaluation Team",
    author_email="",
    
    # Package configuration
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    
    # Dependencies
    install_requires=install_requires,
    
    # Optional features
    extras_require={
        "pdf": pdf_requires,
    },
    
    # Entry points for console scripts
    entry_points={
        "console_scripts": [
            "land_eval=main:run",
        ],
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Real Estate Professionals",
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
) 