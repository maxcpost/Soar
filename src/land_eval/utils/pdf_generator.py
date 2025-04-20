#!/usr/bin/env python
import os
import logging
import platform
import subprocess
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("pdf_generator")

# CSS style for the PDF output
PDF_STYLE = """
@page {
    size: letter;
    margin: 1.5cm;
}
body {
    font-family: Arial, sans-serif;
    line-height: 1.5;
    margin: 0;
    font-size: 10pt;
}
h1 {
    color: #2c3e50;
    font-size: 18pt;
    margin-bottom: 15px;
    border-bottom: 1px solid #eee;
    padding-bottom: 8px;
    page-break-after: avoid;
}
h2 {
    color: #34495e;
    font-size: 14pt;
    margin-top: 20px;
    margin-bottom: 10px;
    border-bottom: 1px solid #eee;
    padding-bottom: 5px;
    page-break-after: avoid;
}
h3 {
    color: #7f8c8d;
    font-size: 12pt;
    margin-top: 15px;
    page-break-after: avoid;
}
h4 {
    font-size: 11pt;
    margin-top: 12px;
    page-break-after: avoid;
}
ul, ol {
    margin-bottom: 10px;
    margin-top: 5px;
}
li {
    margin-bottom: 3px;
}
p {
    margin-bottom: 8px;
    margin-top: 0;
}
blockquote {
    border-left: 3px solid #ccc;
    margin-left: 0;
    padding-left: 10px;
    color: #555;
}
code {
    background-color: #f9f9f9;
    padding: 1px 3px;
    border-radius: 3px;
    font-family: monospace;
    font-size: 9pt;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 15px 0;
    font-size: 9pt;
}
th, td {
    border: 1px solid #ddd;
    padding: 6px;
    text-align: left;
}
th {
    background-color: #f2f2f2;
    font-weight: bold;
}
tr:nth-child(even) {
    background-color: #f9f9f9;
}
.company-name {
    font-weight: bold;
    color: #2980b9;
}
.company-details {
    margin-left: 15px;
    border-left: 2px solid #3498db;
    padding-left: 10px;
    margin-bottom: 15px;
}
.growth-section {
    page-break-inside: avoid;
}
"""

def check_macos_dependencies():
    """
    Check if the required system libraries for WeasyPrint are installed on macOS.
    Returns True if dependencies appear to be installed, False otherwise.
    """
    if platform.system() != "Darwin":  # Not macOS
        return True  # Assume dependencies are handled differently on other platforms
    
    try:
        # Check for Homebrew
        result = subprocess.run(['which', 'brew'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.warning("Homebrew not found. WeasyPrint requires system dependencies installed via Homebrew.")
            return False
        
        # Check for required packages
        dependencies = ['cairo', 'pango', 'gdk-pixbuf', 'libffi']
        missing = []
        
        for dep in dependencies:
            # Try to verify if the package is installed
            result = subprocess.run(['brew', 'list', dep], capture_output=True, text=True)
            if result.returncode != 0:
                missing.append(dep)
        
        if missing:
            logger.warning(f"Missing required dependencies for WeasyPrint: {', '.join(missing)}")
            logger.warning(f"Install them with: brew install {' '.join(missing)}")
            return False
        
        # Check for and create symbolic links for libraries
        try_create_macos_symlinks()
            
        return True
    
    except Exception as e:
        logger.warning(f"Error checking macOS dependencies: {e}")
        return False

def try_create_macos_symlinks():
    """
    Try to automatically create symbolic links for WeasyPrint libraries on macOS.
    This helps when libraries exist but have different names than what WeasyPrint expects.
    """
    try:
        # Common location for Homebrew libraries
        lib_dir = Path("/usr/local/lib")
        if not lib_dir.exists():
            lib_dir = Path("/opt/homebrew/lib")  # Apple Silicon location
            if not lib_dir.exists():
                return  # Can't find the library directory
        
        # Map of expected link names to actual library names
        symlinks = {
            "libgobject-2.0-0": "libgobject-2.0.dylib",
            "libpango-1.0-0": "libpango-1.0.dylib",
            "libpangocairo-1.0-0": "libpangocairo-1.0.dylib"
        }
        
        for link_name, lib_name in symlinks.items():
            link_path = lib_dir / link_name
            lib_path = lib_dir / lib_name
            
            # Check if the actual library exists
            if not lib_path.exists():
                continue
                
            # If the symlink doesn't exist, try to create it
            if not link_path.exists():
                try:
                    # Try to create the symlink as current user
                    os.symlink(lib_name, link_path)
                    logger.info(f"Created symlink: {link_path} -> {lib_name}")
                except PermissionError:
                    # If failed due to permissions, instruct the user
                    logger.warning(f"Could not create symlink: {link_path} -> {lib_name}")
                    logger.warning(f"Run: sudo ln -s {lib_name} {link_path}")
    
    except Exception as e:
        logger.warning(f"Error creating symlinks: {e}")
        logger.warning("You may need to create them manually:")
        logger.warning("  cd /usr/local/lib")
        logger.warning("  sudo ln -s libgobject-2.0.dylib libgobject-2.0-0")
        logger.warning("  sudo ln -s libpango-1.0.dylib libpango-1.0-0")
        logger.warning("  sudo ln -s libpangocairo-1.0.dylib libpangocairo-1.0-0")

def _import_pdf_dependencies():
    """
    Attempt to import required PDF generation libraries.
    Returns the imported modules if successful, None otherwise.
    """
    try:
        # On macOS, first check system dependencies
        if platform.system() == "Darwin" and not check_macos_dependencies():
            logger.warning("Install macOS dependencies with: brew install cairo pango gdk-pixbuf libffi")
            raise ImportError("Missing macOS system dependencies for WeasyPrint")
        
        # Try to import the required libraries
        import markdown
        import mdformat
        from weasyprint import HTML, CSS
        return (markdown, mdformat, HTML, CSS)
    
    except ImportError as e:
        logger.warning(f"PDF generation Python dependencies not available: {e}")
        logger.warning("To enable PDF report generation, install with: pip install -e .[pdf]")
        if platform.system() == "Darwin":
            logger.warning("Make sure you have the required system dependencies:")
            logger.warning("  brew install cairo pango gdk-pixbuf libffi")
        return None
    
    except OSError as e:
        logger.warning(f"PDF generation system libraries missing: {e}")
        if platform.system() == "Darwin":
            # Handle the specific libgobject-2.0-0 error
            if "libgobject-2.0-0" in str(e):
                logger.warning("On macOS, the library name is different than what WeasyPrint is trying to load.")
                logger.warning("Run these commands to create the necessary symlinks:")
                logger.warning("  cd /usr/local/lib")
                logger.warning("  sudo ln -s libgobject-2.0.dylib libgobject-2.0-0")
                logger.warning("  sudo ln -s libpango-1.0.dylib libpango-1.0-0")
                logger.warning("  sudo ln -s libpangocairo-1.0.dylib libpangocairo-1.0-0")
            else:
                logger.warning("On macOS, install the required dependencies with:")
                logger.warning("  brew install cairo pango gdk-pixbuf libffi")
                logger.warning("  brew reinstall cairo pango gdk-pixbuf libffi")
        else:
            logger.warning("See WeasyPrint documentation for system dependencies:")
            logger.warning("  https://doc.courtbouillon.org/weasyprint/stable/first_steps.html")
        return None
    
    except Exception as e:
        logger.warning(f"Unexpected error importing PDF dependencies: {e}")
        return None

def generate_pdf_report(markdown_content, output_path=None, listing_id="unknown"):
    """
    Convert markdown content to a PDF file and save it to the output path.
    Falls back to saving as markdown if PDF generation dependencies aren't available.
    
    Args:
        markdown_content (str): The markdown content to convert
        output_path (str, optional): The directory path to save the PDF. If None, saves to project root.
        listing_id (str, optional): The listing ID to use in the filename
        
    Returns:
        str: The path to the generated file (PDF or markdown)
    """
    # Try to import dependencies only when the function is called
    pdf_libs = _import_pdf_dependencies()
    
    if pdf_libs:
        # Unpack the libraries
        markdown_lib, mdformat_lib, HTML, CSS = pdf_libs
        
        try:
            # Format the markdown content with mdformat for consistency
            formatted_markdown = mdformat_lib.text(markdown_content)
            
            # Process formatted markdown to enhance company name formatting
            # This is a simple enhancement - a proper implementation would use regex
            lines = formatted_markdown.split('\n')
            enhanced_lines = []
            in_growth_section = False
            
            for line in lines:
                # Check if we're in the Growth Trends section
                if line.startswith('## Growth Trends') or line.startswith('# Growth Trends'):
                    in_growth_section = True
                    line = '<div class="growth-section">' + line
                elif in_growth_section and (line.startswith('## ') or line.startswith('# ')):
                    # We've left the Growth Trends section
                    in_growth_section = False
                    enhanced_lines.append('</div>')
                
                # Add special styling for company names in the Growth Trends section
                if in_growth_section and ':' in line and not line.startswith('#'):
                    if line.strip().endswith(':'):
                        # Likely a company name with a colon at the end
                        company_part = line.strip()[:-1]  # Remove the colon
                        line = f'<div class="company-name">{company_part}</div><div class="company-details">'
                    elif line.strip() and line.lstrip() == line:  # Not indented
                        # End the company details div when we hit a non-indented line that doesn't look like a company header
                        enhanced_lines.append('</div>')
                
                enhanced_lines.append(line)
            
            # Close any open growth section
            if in_growth_section:
                enhanced_lines.append('</div>')
                
            # Join the enhanced content
            enhanced_markdown = '\n'.join(enhanced_lines)
            
            # Convert markdown to HTML with extensions
            html_content = markdown_lib.markdown(
                enhanced_markdown,
                extensions=['tables', 'fenced_code', 'nl2br', 'sane_lists', 'attr_list']
            )
            
            # Wrap HTML content with proper structure and CSS
            html_document = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Land Listing Evaluation Report - {listing_id}</title>
                <style>
                    {PDF_STYLE}
                </style>
            </head>
            <body>
                <h1>Land Evaluation Report: {listing_id}</h1>
                <p class="date">Generated on {datetime.now().strftime("%B %d, %Y")}</p>
                {html_content}
            </body>
            </html>
            """
            
            # Create output path if not specified
            if not output_path:
                output_path = Path(".")
            else:
                output_path = Path(output_path)
                
            # Create output directory if it doesn't exist
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp and listing ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"Land_Evaluation_{listing_id}_{timestamp}.pdf"
            pdf_path = output_path / pdf_filename
            
            # Convert HTML to PDF with proper configuration for longer reports
            HTML(string=html_document).write_pdf(
                pdf_path,
                stylesheets=[CSS(string=PDF_STYLE)],
                presentational_hints=True
            )
            
            logger.info(f"Generated comprehensive PDF report saved to: {pdf_path}")
            print(f"\nComprehensive PDF Report generated successfully: {pdf_path}")
            
            return str(pdf_path)
        
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            print(f"\nError generating PDF report, falling back to markdown: {e}")
            # Fall back to markdown if PDF generation fails
            return _save_markdown_fallback(markdown_content, output_path, listing_id)
    
    else:
        # If dependencies aren't available, save as markdown
        print("\nPDF generation dependencies not available. Saving as markdown instead.")
        
        if platform.system() == "Darwin":  # macOS specific instructions
            print("\nFor macOS, install the required dependencies with:")
            print("brew install cairo pango gdk-pixbuf libffi")
            print("pip install -e .[pdf]")
        else:
            print("To enable PDF generation, install with: pip install -e .[pdf]")
            print("\nSystem dependencies may also be required:")
            print("- Ubuntu/Debian: apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info")
            print("- Windows: See WeasyPrint documentation\n")
        
        return _save_markdown_fallback(markdown_content, output_path, listing_id)

def _save_markdown_fallback(content, output_path=None, listing_id="unknown"):
    """
    Save content as a markdown file when PDF generation is not available.
    
    Args:
        content (str): The markdown content to save
        output_path (str, optional): The directory path to save the file. If None, saves to project root.
        listing_id (str, optional): The listing ID to use in the filename
        
    Returns:
        str: The path to the generated markdown file
    """
    try:
        # Create output path if not specified
        if not output_path:
            output_path = Path(".")
        else:
            output_path = Path(output_path)
        
        # Create directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp and listing ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        md_filename = f"Land_Evaluation_{listing_id}_{timestamp}.md"
        md_path = output_path / md_filename
        
        # Write content to file
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        logger.info(f"Markdown report saved to: {md_path}")
        print(f"\nMarkdown report generated successfully: {md_path}")
        
        return str(md_path)
    except Exception as e:
        logger.error(f"Error saving markdown report: {e}")
        print(f"\nError saving markdown report: {e}")
        return None 