#!/usr/bin/env python
import os
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("pdf_generator")

# CSS style for the PDF output
PDF_STYLE = """
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 2cm;
    font-size: 11pt;
}
h1 {
    color: #2c3e50;
    font-size: 20pt;
    margin-bottom: 20px;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
}
h2 {
    color: #34495e;
    font-size: 16pt;
    margin-top: 25px;
    margin-bottom: 15px;
    border-bottom: 1px solid #eee;
    padding-bottom: 8px;
}
h3 {
    color: #7f8c8d;
    font-size: 14pt;
    margin-top: 20px;
}
ul, ol {
    margin-bottom: 15px;
}
li {
    margin-bottom: 5px;
}
p {
    margin-bottom: 10px;
}
blockquote {
    border-left: 4px solid #ccc;
    margin-left: 0;
    padding-left: 15px;
    color: #555;
}
code {
    background-color: #f9f9f9;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: monospace;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
}
th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}
th {
    background-color: #f2f2f2;
    font-weight: bold;
}
tr:nth-child(even) {
    background-color: #f9f9f9;
}
"""

def _import_pdf_dependencies():
    """
    Attempt to import required PDF generation libraries.
    Returns True if successful, False otherwise.
    """
    try:
        import markdown
        import mdformat
        from weasyprint import HTML, CSS
        return (markdown, mdformat, HTML, CSS)
    except ImportError as e:
        logger.warning(f"PDF generation dependencies not available: {e}")
        logger.warning("To enable PDF report generation, install with: pip install -e .[pdf]")
        return None
    except OSError as e:
        logger.warning(f"PDF generation system libraries missing: {e}")
        logger.warning("See WeasyPrint documentation for system dependencies: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html")
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
            
            # Convert markdown to HTML
            html_content = markdown_lib.markdown(
                formatted_markdown,
                extensions=['tables', 'fenced_code', 'nl2br']
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
            
            # Convert HTML to PDF
            HTML(string=html_document).write_pdf(
                pdf_path,
                stylesheets=[CSS(string=PDF_STYLE)]
            )
            
            logger.info(f"Generated PDF report saved to: {pdf_path}")
            print(f"\nPDF Report generated successfully: {pdf_path}")
            
            return str(pdf_path)
        
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            print(f"\nError generating PDF report, falling back to markdown: {e}")
            # Fall back to markdown if PDF generation fails
            return _save_markdown_fallback(markdown_content, output_path, listing_id)
    
    else:
        # If dependencies aren't available, save as markdown
        print("\nPDF generation dependencies not available. Saving as markdown instead.")
        print("To enable PDF generation, install with: pip install -e .[pdf]")
        print("\nSystem dependencies may also be required:")
        print("- macOS: brew install cairo pango libffi")
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