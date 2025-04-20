#!/usr/bin/env python
import sys
import os
import logging
import shutil
import warnings
from pathlib import Path
from dotenv import load_dotenv

# Suppress specific deprecation and user warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="paramiko")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

# Update imports to use the src module
from src.crew_automation_evaluation_for_land_listing_opportunities.crew import CrewAutomationEvaluationForLandListingOpportunitiesCrew
from src.crew_automation_evaluation_for_land_listing_opportunities.data_processor import create_cork_folder, get_stock_number, process_master_csv

# Try importing PDF generator, but continue even if it fails
try:
    # Only import the module name, not the actual function
    import src.crew_automation_evaluation_for_land_listing_opportunities.utils.pdf_generator as pdf_generator
    PDF_GENERATION_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger("main")
    # Create a dummy module with the same interface
    class DummyPDFGenerator:
        @staticmethod
        def generate_pdf_report(markdown_content, output_path=None, listing_id="unknown"):
            logger.warning("PDF generation module not available. To enable PDF report generation, install with: pip install -e .[pdf]")
            print("\nPDF generation module is not available. To enable this feature, install the required dependencies:")
            print("pip install -e .[pdf]")
            
            # Create a fallback markdown file
            from pathlib import Path
            from datetime import datetime
            reports_dir = Path('./reports')
            reports_dir.mkdir(exist_ok=True)
            
            # Generate filename with timestamp and listing ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            md_filename = f"Land_Evaluation_{listing_id}_{timestamp}.md"
            md_path = reports_dir / md_filename
            
            try:
                # Write content to file
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                    
                logger.info(f"Markdown report saved to: {md_path}")
                print(f"\nMarkdown report generated successfully: {md_path}")
                
                return str(md_path)
            except Exception as e:
                logger.error(f"Error saving markdown report: {e}")
                print(f"\nError saving markdown report: {e}")
                return None
    
    pdf_generator = DummyPDFGenerator()
    PDF_GENERATION_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("main")

# Load environment variables from .env file if it exists
env_path = Path('.') / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    logger.info("Loaded environment variables from .env file")
else:
    logger.warning("No .env file found. Make sure to set OPENAI_API_KEY environment variable.")

# Check if OpenAI API key is set
if not os.getenv("OPENAI_API_KEY"):
    logger.warning("OPENAI_API_KEY is not set. Crew might not function correctly.")
    print("\n⚠️  WARNING: OPENAI_API_KEY environment variable is not set!")
    print("Please set it in the .env file or as an environment variable.")

def cleanup_cork_folder(cork_path):
    """
    Delete all CSV files in the cork folder after the report is generated.
    
    Args:
        cork_path (str): Path to the cork folder
    """
    try:
        cork_dir = Path(cork_path)
        if cork_dir.exists() and cork_dir.is_dir():
            for csv_file in cork_dir.glob("*.csv"):
                csv_file.unlink()
                logger.info(f"Deleted {csv_file}")
            
            logger.info("Cleanup completed - all CSV files removed from cork folder")
            print("Cleanup completed - all temporary CSV files removed")
    except Exception as e:
        logger.error(f"Error cleaning up cork folder: {e}")
        print(f"Warning: Failed to clean up temporary files: {e}")

def cleanup_chroma_database():
    """
    Clean up the ChromaDB vector database to prevent previous analyses from affecting new runs.
    This removes all vector embeddings and database files from the chroma_vectordb directory.
    """
    try:
        # Path to the ChromaDB directory (changed from 'db' to 'chroma_vectordb')
        chroma_dir = Path('./chroma_vectordb')
        
        # Check if directory exists
        if chroma_dir.exists() and chroma_dir.is_dir():
            # Remove all files and subdirectories
            shutil.rmtree(chroma_dir)
            
            # Recreate the empty directory
            chroma_dir.mkdir(exist_ok=True)
            
            logger.info("ChromaDB database cleaned - all vector data removed")
            print("ChromaDB database cleaned - all previous analysis data removed")
        else:
            # Create the directory if it doesn't exist
            chroma_dir.mkdir(exist_ok=True)
            logger.info("ChromaDB directory created at chroma_vectordb")
    except Exception as e:
        logger.error(f"Error cleaning ChromaDB database: {e}")
        print(f"Warning: Failed to clean ChromaDB database: {e}")

def extract_report_from_result(result):
    """
    Extract the final report content from the crew execution result.
    
    Args:
        result: The result returned from the crew execution
        
    Returns:
        str: The markdown content of the final report
    """
    try:
        # The report is typically the final output from the narrative reporter
        if result and hasattr(result, 'raw'):
            for task_result in reversed(result.raw.get('task_results', [])):
                # Find the last task (narrative reporter)
                if task_result.get('status') == 'completed':
                    output = task_result.get('output', '')
                    if output and isinstance(output, str):
                        # Extract the 'Final Answer' part which contains the report
                        if 'Final Answer:' in output:
                            return output.split('Final Answer:', 1)[1].strip()
                        return output
        
        # If we can't find a structured result, return the string representation
        return str(result)
    except Exception as e:
        logger.error(f"Error extracting report content: {e}")
        return str(result)

def create_reports_folder():
    """
    Create a reports folder in the root directory if it doesn't exist.
    
    Returns:
        Path: The path to the reports folder
    """
    reports_dir = Path('./reports')
    reports_dir.mkdir(exist_ok=True)
    return reports_dir

def save_markdown_report(content, listing_id="unknown"):
    """
    Save the report content as a markdown file.
    This is a fallback when PDF generation is not available.
    
    Args:
        content (str): The markdown content to save
        listing_id (str): The listing ID to use in the filename
        
    Returns:
        str: The path to the generated markdown file
    """
    try:
        from datetime import datetime
        
        # Create reports folder
        reports_dir = create_reports_folder()
        
        # Generate filename with timestamp and listing ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        md_filename = f"Land_Evaluation_{listing_id}_{timestamp}.md"
        md_path = reports_dir / md_filename
        
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

def run():
    """
    Run the crew with processed data from a selected stock number.
    """
    cork_path = None
    try:
        # Clean up the ChromaDB database before running a new analysis
        cleanup_chroma_database()
        
        # Create cork folder and process data
        cork_path = create_cork_folder()
        stock_number = get_stock_number()
        inputs = process_master_csv(stock_number, cork_path)
        
        if not inputs:
            logger.error("Failed to process data. Exiting.")
            print("Failed to process data. Exiting.")
            return
        
        logger.info(f"Starting crew for listing {inputs['listing_id']} in {inputs['City']}, {inputs['State']}")
        print(f"\nStarting evaluation for listing {inputs['listing_id']} in {inputs['City']}, {inputs['State']}...")
        
        crew = CrewAutomationEvaluationForLandListingOpportunitiesCrew().crew()
        result = crew.kickoff(inputs=inputs)
        
        logger.info("Crew execution completed")
        
        # Clean up the cork folder after the report is generated
        cleanup_cork_folder(cork_path)
        
        # Extract report content from the result
        report_content = extract_report_from_result(result)
        
        # Generate report
        if report_content:
            # Create reports folder
            reports_dir = create_reports_folder()
            
            # Generate report with the listing ID
            listing_id = inputs.get('listing_id', 'unknown')
            
            # Generate PDF if available, otherwise save as markdown
            if PDF_GENERATION_AVAILABLE:
                pdf_generator.generate_pdf_report(
                    markdown_content=report_content,
                    output_path=reports_dir,
                    listing_id=listing_id
                )
            else:
                save_markdown_report(
                    content=report_content,
                    listing_id=listing_id
                )
        
        return result
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("\nProcess interrupted by user.")
    except Exception as e:
        logger.error(f"Error running crew: {e}")
        print(f"Error running crew: {e}")
    finally:
        # If we encountered an error before cleanup, don't delete files
        # as they might be needed for debugging
        pass


def train():
    """
    Train the crew for a given number of iterations using 
    processed data from a selected stock number.
    """
    cork_path = None
    try:
        if len(sys.argv) < 3:
            logger.error("Missing required arguments for training")
            print("Usage: train <n_iterations> <filename>")
            return
            
        n_iterations = int(sys.argv[2])
        filename = sys.argv[3]
        
        # Clean up the ChromaDB database before training
        cleanup_chroma_database()
        
        # Create cork folder and process data
        cork_path = create_cork_folder()
        stock_number = get_stock_number()
        inputs = process_master_csv(stock_number, cork_path)
        
        if not inputs:
            logger.error("Failed to process data. Exiting.")
            print("Failed to process data. Exiting.")
            return
            
        logger.info(f"Starting training crew for {n_iterations} iterations, saving to {filename}")
        print(f"\nStarting training for {n_iterations} iterations on listing {inputs['listing_id']}...")
        
        crew = CrewAutomationEvaluationForLandListingOpportunitiesCrew().crew()
        result = crew.train(n_iterations=n_iterations, filename=filename, inputs=inputs)
        
        logger.info(f"Training completed and saved to {filename}")
        
        # Clean up the cork folder after training is complete
        cleanup_cork_folder(cork_path)
        
        # Extract report content from the result if available
        report_content = extract_report_from_result(result)
        
        # Generate report if there's content
        if report_content:
            # Create reports folder
            reports_dir = create_reports_folder()
            
            # Generate report with the listing ID
            listing_id = inputs.get('listing_id', 'unknown')
            
            # Generate PDF if available, otherwise save as markdown
            if PDF_GENERATION_AVAILABLE:
                pdf_generator.generate_pdf_report(
                    markdown_content=report_content,
                    output_path=reports_dir,
                    listing_id=f"{listing_id}_training"
                )
            else:
                save_markdown_report(
                    content=report_content,
                    listing_id=f"{listing_id}_training"
                )
        
        return result
        
    except ValueError:
        logger.error("Invalid numeric value for n_iterations")
        print("Error: n_iterations must be a valid number")
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("\nProcess interrupted by user.")
    except Exception as e:
        logger.error(f"An error occurred while training the crew: {e}")
        print(f"Error: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        if len(sys.argv) < 3:
            logger.error("Missing required task_id argument for replay")
            print("Usage: replay <task_id>")
            return
            
        task_id = sys.argv[2]
        logger.info(f"Replaying crew execution from task {task_id}")
        print(f"\nReplaying crew execution from task {task_id}...")
        
        crew = CrewAutomationEvaluationForLandListingOpportunitiesCrew().crew()
        result = crew.replay(task_id=task_id)
        
        logger.info("Replay completed")
        
        # No cleanup needed for replay as it doesn't create new CSV files
        
        # Extract report content from the result if available
        report_content = extract_report_from_result(result)
        
        # Generate report if there's content
        if report_content:
            # Create reports folder
            reports_dir = create_reports_folder()
            
            # Generate report with the task ID as identifier
            if PDF_GENERATION_AVAILABLE:
                pdf_generator.generate_pdf_report(
                    markdown_content=report_content,
                    output_path=reports_dir,
                    listing_id=f"replay_{task_id}"
                )
            else:
                save_markdown_report(
                    content=report_content,
                    listing_id=f"replay_{task_id}"
                )
        
        return result
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("\nProcess interrupted by user.")
    except Exception as e:
        logger.error(f"An error occurred while replaying the crew: {e}")
        print(f"Error: {e}")

def test():
    """
    Test the crew execution with a specific OpenAI model 
    and return the results.
    """
    cork_path = None
    try:
        if len(sys.argv) < 4:
            logger.error("Missing required arguments for testing")
            print("Usage: test <n_iterations> <openai_model_name>")
            return
            
        n_iterations = int(sys.argv[2])
        openai_model_name = sys.argv[3]
        
        # Clean up the ChromaDB database before testing
        cleanup_chroma_database()
        
        # Create cork folder and process data
        cork_path = create_cork_folder()
        stock_number = get_stock_number()
        inputs = process_master_csv(stock_number, cork_path)
        
        if not inputs:
            logger.error("Failed to process data. Exiting.")
            print("Failed to process data. Exiting.")
            return
        
        logger.info(f"Testing crew for {n_iterations} iterations using model {openai_model_name}")
        print(f"\nTesting crew for {n_iterations} iterations using model {openai_model_name}...")
            
        crew = CrewAutomationEvaluationForLandListingOpportunitiesCrew().crew()
        result = crew.test(n_iterations=n_iterations, openai_model_name=openai_model_name, inputs=inputs)
        
        logger.info("Testing completed")
        
        # Clean up the cork folder after testing is complete
        cleanup_cork_folder(cork_path)
        
        # Extract report content from the result if available
        report_content = extract_report_from_result(result)
        
        # Generate report if there's content
        if report_content:
            # Create reports folder
            reports_dir = create_reports_folder()
            
            # Generate report with the listing ID and model name
            listing_id = inputs.get('listing_id', 'unknown')
            
            if PDF_GENERATION_AVAILABLE:
                pdf_generator.generate_pdf_report(
                    markdown_content=report_content,
                    output_path=reports_dir,
                    listing_id=f"{listing_id}_{openai_model_name}_test"
                )
            else:
                save_markdown_report(
                    content=report_content,
                    listing_id=f"{listing_id}_{openai_model_name}_test"
                )
        
        return result
        
    except ValueError:
        logger.error("Invalid numeric value for n_iterations")
        print("Error: n_iterations must be a valid number")
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("\nProcess interrupted by user.")
    except Exception as e:
        logger.error(f"An error occurred while testing the crew: {e}")
        print(f"Error: {e}")

def show_help():
    """
    Display help information for the available commands.
    """
    print("\nLand Listing Opportunities Evaluation - Available Commands:\n")
    print("run               Run the crew evaluation on a selected property")
    print("train <n> <file>  Train the crew for n iterations and save to file")
    print("replay <task_id>  Replay execution from a specific task ID")
    print("test <n> <model>  Test execution for n iterations with the specified model")
    print("help              Show this help message\n")
    print("Note: Reports are automatically generated in the './reports' directory")
    if not PDF_GENERATION_AVAILABLE:
        print("\nPDF generation is currently disabled. To enable this feature, install the required dependencies:")
        print("pip install -e .[pdf]")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: main.py <command> [<args>]")
        show_help()
        sys.exit(1)

    command = sys.argv[1]
    if command == "run":
        run()
    elif command == "train":
        train()
    elif command == "replay":
        replay()
    elif command == "test":
        test()
    elif command in ["help", "-h", "--help"]:
        show_help()
    else:
        print(f"Unknown command: {command}")
        show_help()
        sys.exit(1) 