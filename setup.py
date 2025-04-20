#!/usr/bin/env python
from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README.md
long_description = (Path(__file__).parent / "README.md").read_text()

# PDF dependencies note
pdf_dependencies_note = """
# PDF Generation Dependencies Note:
# The PDF generation feature requires additional dependencies which may need system libraries.
# - On macOS: brew install cairo pango libffi
# - On Ubuntu/Debian: apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
# - On Windows: See WeasyPrint documentation: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows
"""

# Add the note to the long description
long_description += "\n" + pdf_dependencies_note

setup(
    name="crew_automation_evaluation_for_land_listing_opportunities",
    version="0.1.0",
    description="A CrewAI workflow for evaluating land listing opportunities by analyzing property data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="you@example.com",
    url="https://github.com/yourusername/land-listing-opportunities",
    python_requires=">=3.10,<3.13",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    scripts=["main.py"],
    install_requires=[
        "crewai[tools]>=0.114.0,<1.0.0",
        "pandas>=2.0.0",
        "python-dotenv>=1.0.0",
        "pathlib>=1.0.1",
        "numpy>=1.22.0",
        "openai>=1.0.0",
        "tiktoken>=0.6.0",
        "cryptography>=41.0.0",
        "pydantic>=2.0.0",
        "tabulate>=0.9.0",
        "colorama>=0.4.6",
        "psutil>=5.9.5",
    ],
    extras_require={
        # PDF report generation dependencies as an optional feature
        "pdf": [
            "markdown>=3.5.1",
            "weasyprint>=60.2",
            "mdformat>=0.7.17",
        ],
        # Full installation with all features
        "full": [
            "markdown>=3.5.1",
            "weasyprint>=60.2",
            "mdformat>=0.7.17",
        ],
    },
    entry_points={
        "console_scripts": [
            "crew_automation=src.crew_automation_evaluation_for_land_listing_opportunities.data_processor:main",
            "process_data=src.crew_automation_evaluation_for_land_listing_opportunities.data_processor:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
) 