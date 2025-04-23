# Soar - Land Listing Opportunities Evaluation

**Description**: An agentic workflow that conducts comprehensive analysis of land that we are considering for development.

## Quick Start Guide

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/yourusername/Soar.git
cd Soar

# Setup on macOS (recommended)
./setup.sh

# OR manually set up with venv (all platforms)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e ".[pdf]"

# Run the evaluation
./land_eval run  # Or: python main.py run
```

**Requirements**:
- Python 3.10 or higher
- An OpenAI API key added to your `.env` file
- For PDF generation on macOS: brew with cairo, pango, gdk-pixbuf, libffi

## How it Works

1. The Soar system will first ask the user to choose a stock number that it would like a report on. Then it will go into the database folder where the master.csv file is located and it will create a folder named "cork" within the database folder. This folder is where all of the csvs that get generated will go.

2. The next step is to segment the data in the master csv. We would like to create csvs that have only the data that each specific agent will need. What this does is compartimentalizes the data so that the AI agent does not get distracted or use additional compute to find the specific data that pertains to the agents focus. Our first step in this is going to be isolating the user specified stock number form the 'StockNumber' column. Here is a list of the various CSVs that should be created with the exact column names that they should be getting the data from...

    Property (property.csv)
    Data Points: Property Address, City, State, Zip

    Environmental (enviornmental.csv)
    Data Points: In SFHA, Fema Flood Zone, FEMA Map Date, Floodplain Area

    Growth Trends (growthTrends.csv)
    Data Points: % Pop Grwth 2020-2024(5m), % Pop Grwth 2024-2029(5m), % Pop Grwth 2020-2024(10m), % Pop Grwth 2024-2029(10m), % HU Grwth 2020-2024(5m), % HU Grwth 2020-2024(10m)

    Housing Units and Occupancy (housingUnitsAndOccupancy.csv)
    Data Points: TotHUs_5, OccHUs_5, OwnerOcc_5, RenterOcc_5, AvgOwnerHHSize_5, AvgRenterHHSize_5, VacHUs_5, VacantForSale_5, VacantForRent_5, VacantSeasonal_5, MobileHomes_5, MobileHomesPerK_5, TotHUs_10, OccHUs_10, OwnerOcc_10, RenterOcc_10, AvgOwnerHHSize_10, AvgRenterHHSize_10, VacHUs_10, VacantForSale_10, VacantForRent_10, VacantSeasonal_10, MobileHomes_10, MobileHomesPerK_10

    Demographics (demographics.csv)
    Data Points: TotPop_5, Age0_4_5, Age5_9_5, Age10_14_5, Age15_19_5, Age20_24_5, Age25_34_5, Age35_44_5, Age45_54_5, Age55_59_5, Age60_64_5, Age65_74_5, Age75_84_5, Over85_5, TotHHs_5, MedianHHInc_5, AvgHHInc_5, InKindergarten_5, InElementary_5, InHighSchool_5, InCollege_5, Disabled_5, DisabledUnder18_5, NonInst18_64_5, Disabled18_64_5, NonInstOver65_5, DisabledElder_5, TotPop_10, Age0_4_10, Age5_9_10, Age10_14_10, Age15_19_10, Age20_24_10, Age25_34_10, Age35_44_10, Age45_54_10, Age55_59_10, Age60_64_10, Age65_74_10, Age75_84_10, Over85_10, TotHHs_10, MedianHHInc_10, AvgHHInc_10, InKindergarten_10, InElementary_10, InHighSchool_10, InCollege_10, Disabled_10, DisabledUnder18_10, NonInst18_64_10, Disabled18_64_10, NonInstOver65_10, DisabledElder_10

    Affordability (affordability.csv) - This data is now included in demographics.csv
    Data Points: HvalUnder50_5, Hval50_5, Hval100_5, Hval150_5, Hval200_5, Hval300_5, Hval500_5, HvalOverMillion_5, HvalOver2Million_5, MedianHValue_5, MedianGrossRent_5, AvgGrossRent_5, HvalUnder50_10, Hval50_10, Hval100_10, Hval150_10, Hval200_10, Hval300_10, Hval500_10, HvalOverMillion_10, HvalOver2Million_10, MedianHValue_10, MedianGrossRent_10, AvgGrossRent_10, MedianHHInc_5, MedianHHInc_10, AvgHHInc_5, AvgHHInc_10

All of these newly created CSVs should be saved to the cork folder. 

3. Run the crew of agents using the csv files that are in the cork folder.

4. After the analysis and report are completed, all temporary CSV files are automatically deleted from the cork folder to clean up the workspace.

5. The vector embedding database (chroma_vectordb) is also cleaned between runs to ensure that previous analyses don't affect new evaluations.

6. A professional PDF report is automatically generated in the `reports` directory, containing the full land evaluation analysis ready for presentation to stakeholders.

## Database Setup

**Important**: This project requires setting up a database with a `master.csv` file. Due to the sensitive nature of property data, this file is not included in the repository and is excluded from version control via `.gitignore`.

The database directory should contain a single file called `master.csv` with the property listing data. This file should include all the columns mentioned in the "How it Works" section above. The system will create a `cork` folder within the database directory to temporarily store segmented CSV files during processing.

## Installation

This project uses Python's virtual environment (venv) for dependency management. Ensure you have Python 3.10+ installed on your system.

### Option 1: macOS Bash Setup Script (Recommended for macOS)

For macOS users, we've created a simple bash script that handles all the setup automatically:

```bash
./setup.sh
```

This script will:
- Check if you're running macOS
- Install Homebrew if needed
- Install Python 3.10+ if needed
- Install all system dependencies for WeasyPrint (cairo, pango, gdk-pixbuf, libffi)
- Create necessary symbolic links for WeasyPrint libraries
- Set up a Python virtual environment (venv)
- Install all Python dependencies including PDF generation capabilities
- Create a `./land_eval` executable script for easy access

After running the script, you can use the application with:
```bash
# Make sure your virtual environment is activated
source venv/bin/activate  # This is done automatically by the land_eval script

# Then run the application
./land_eval run
```

### Option 2: Manual Setup with Venv (All Platforms)

For all platforms, you can manually set up the project with Python's venv:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e ".[pdf]"  # Installs optional PDF dependencies
```

### PDF Generation System Dependencies

For PDF report generation, WeasyPrint requires additional system dependencies:

- **On macOS**: 
  ```bash
  brew install cairo pango gdk-pixbuf libffi
  ```
  
  You may also need to create symbolic links if you encounter library errors:
  ```bash
  cd /usr/local/lib  # or /opt/homebrew/lib on Apple Silicon
  sudo ln -s libgobject-2.0.dylib libgobject-2.0-0
  sudo ln -s libpango-1.0.dylib libpango-1.0-0
  sudo ln -s libpangocairo-1.0.dylib libpangocairo-1.0-0
  ```
  
  Alternatively, just use the `setup.sh` script which handles all this automatically.

- **On Ubuntu/Debian**:
  ```bash
  apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
  ```

- **On Windows**: 
  Please refer to the [WeasyPrint documentation](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows).

### Environment Setup

**Add your `OPENAI_API_KEY` into the `.env` file**

Create a `.env` file in the root directory with your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

## Running the Project

To run the project, make sure your virtual environment is activated.

### Option 1: Run with the local executable

If you installed using the setup.sh script, you can use:

```bash
# This script automatically activates the venv
./land_eval run
```

### Option 2: Run with Python directly (in activated venv)

```bash
# Make sure your virtual environment is activated
source venv/bin/activate

# Then run the application
python main.py run
```

### Available Commands

The following commands are available:

- `run` - Run the standard workflow
- `train <iterations> <filename>` - Train the crew for a specified number of iterations
- `replay <task_id>` - Replay execution from a specific task ID
- `help` - Show the help message

Example:
```bash
./land_eval run
./land_eval help
```

## GitHub Repository

When deploying this project to GitHub:

- A comprehensive `.gitignore` file is included to prevent sensitive information from being committed
- The `database` directory and all CSV files within it are excluded from version control
- Environment variables (`.env`) containing API keys are also excluded

To set up a new deployment:
1. Clone the repository
2. Create a `database` directory and place your `master.csv` file there
3. Create your `.env` file with your API key
4. Run the setup script (or follow the manual installation steps)
5. Run the project

## Project Structure

The project has been structured with the main entry point in the root directory:

```
/
├── main.py                  # Main entry point (in root)
├── setup.sh                 # macOS bash setup script
├── land_eval                # Local executable script
├── requirements.txt         # Package requirements
├── .env                     # Environment variables (not in version control)
├── .gitignore               # Git ignore file
├── .env.example             # Example environment file
├── pyproject.toml           # Project configuration
├── README.md                # Documentation
├── database/                # Data directory (not in version control)
│   ├── master.csv           # Master data file (not in version control)
│   └── cork/                # Generated CSV files (not in version control)
├── chroma_vectordb/         # Vector database for agent memory (not in version control)
├── reports/                 # Generated PDF reports (not in version control)
├── src/                     # Source code
│   └── land_eval/           # Main package directory
│       ├── __init__.py
│       ├── crew.py          # Crew definition with GPT-4o model
│       ├── data_processor.py # Data processing utilities
│       ├── config/          # Configuration directory
│       │   ├── agents.yaml  # Agent definitions
│       │   └── tasks.yaml   # Task definitions
│       ├── utils/           # Utility functions
│       │   └── pdf_generator.py # PDF report generator
│       └── tools/           # Custom tools
│           ├── __init__.py
│           └── research_tool.py # Company/economic research tool
```

## Project Improvements

This implementation includes several key improvements:

1. **Robust Error Handling**: Added comprehensive error handling throughout the codebase to gracefully handle exceptions.

2. **Data Validation**: Implemented validation for input data to ensure the required columns exist.

3. **Cross-Platform Compatibility**: Used pathlib for file path handling to work consistently across different operating systems.

4. **Logging**: Added proper logging for better debugging and monitoring.

5. **Environment Variables**: Support for environment variables including OpenAI API key via .env file.

6. **Improved Command Line Interface**: Enhanced CLI with better error messages and a help command.

7. **Better Documentation**: Improved inline comments and documentation.

8. **Simplified Setup Process**: Added setup.sh and requirements.txt for easy installation.

9. **Hard-coded Model**: Set all agents to use gpt-4o model for consistent performance.

10. **Restructured Project**: Moved main.py to root directory for easier execution.

11. **Data Protection**: Added .gitignore and documentation to protect sensitive data.

12. **Automatic Cleanup**: Added functionality to automatically delete temporary CSV files and vector database after report generation.

13. **Vector Database Management**: Improved management of the vector database to prevent cross-contamination between different property analyses.

14. **PDF Report Generation**: Added automatic PDF report generation with professional formatting for easy sharing with stakeholders.

15. **Virtual Environment Support**: Set up the project to use Python's venv for better dependency management and isolation.

## Understanding Your Crew

The Soar Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

### Agents in the System

- **Property Analyst**: Analyzes location details and housing market sentiment
- **Environmental Evaluator**: Assesses flood risks and environmental hazards
- **Growth Trends Expert**: Evaluates population growth and market expansion potential
- **Occupancy Expert**: Analyzes housing occupancy and vacancy trends
- **Socio-economic Analyst**: Examines demographics and affordability pressures
- **Integrated Evaluator**: Combines all analyses into a comprehensive assessment
- **Narrative Reporter**: Creates the final polished report

## Customizing

If you need to customize the project:

- Modify `src/land_eval/config/agents.yaml` to define your agents
- Modify `src/land_eval/config/tasks.yaml` to define your tasks
- Modify `src/land_eval/crew.py` to add your own logic, tools and specific args
- Modify `main.py` to add custom inputs for your agents and tasks

## Recent Improvements

The Land Evaluation report generation system has been enhanced with several new features:

### New Analysis Capabilities
- **Micro-Market Analysis**: Compares the subject property to properties in the immediate neighborhood (within a 1-mile radius) to provide hyper-local context
- **Workforce Assessment**: Analyzes local talent pools, educational institutions, and workforce development programs relevant to the property location

### Advanced Reasoning
- **Chain-of-Thought Prompting**: All agents now show detailed reasoning processes, making conclusions more transparent and defensible
- **Enhanced Environmental Risk Analysis**: More thorough flood risk assessment with detailed mitigation recommendations
- **Comprehensive Growth Trends Analysis**: Deeper analysis of economic development with reasoning about why specific companies choose the location

### Technology Upgrades
- **Claude 3.5 Sonnet LLM**: All agents now use the more powerful Claude 3.5 Sonnet for higher reasoning capabilities and more detailed analysis

## Setup Requirements

Before running the system, make sure to:

1. Set up your environment variables in the `.env` file:
   - `OPENAI_API_KEY`: Your OpenAI API key (for some supporting functions)
   - `ANTHROPIC_API_KEY`: Your Anthropic API key (required for Claude 3.5 Sonnet)

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```