#!/usr/bin/env bash
# Land Eval macOS Setup Script
# This script sets up the Land Eval project environment on macOS

set -e  # Exit on error

# Colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================${NC}"
echo -e "${GREEN}Land Eval Setup for macOS${NC}"
echo -e "${BLUE}=================================${NC}"
echo

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo -e "${RED}This script is intended for macOS only.${NC}"
    echo "For other operating systems, please use pip install -e .[pdf]"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for brew and install if missing
if ! command_exists brew; then
    echo -e "${YELLOW}Homebrew not found. Installing Homebrew...${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add brew to PATH for Apple Silicon Macs if needed
    if [[ "$(uname -m)" == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
else
    echo -e "${GREEN}✓ Homebrew is installed${NC}"
fi

# Check for Python 3.10+ and install if needed
if ! command_exists python3 || [[ $(python3 -c 'import sys; print(sys.version_info >= (3, 10))') == "False" ]]; then
    echo -e "${YELLOW}Python 3.10+ not found. Installing Python...${NC}"
    brew install python@3.10
else
    echo -e "${GREEN}✓ Python 3.10+ is installed${NC}"
fi

# Check for and install system dependencies for WeasyPrint
echo -e "\n${BLUE}Installing system dependencies...${NC}"
brew install cairo pango gdk-pixbuf libffi

# Create symbolic links for WeasyPrint if they don't exist
echo -e "\n${BLUE}Setting up WeasyPrint symbolic links...${NC}"

# Determine lib paths to check (try both common locations)
LIB_PATHS=("/usr/local/lib" "/opt/homebrew/lib")

# Function to create symlinks with sudo if needed
create_symlink() {
    local source_lib=$1
    local target_link=$2
    local success=false
    
    # Try each lib path
    for LIB_PATH in "${LIB_PATHS[@]}"; do
        if [[ -f "$LIB_PATH/$source_lib" && ! -f "$LIB_PATH/$target_link" ]]; then
            echo "Creating symlink in $LIB_PATH: $target_link -> $source_lib"
            
            # Try without sudo first
            if ln -sf "$LIB_PATH/$source_lib" "$LIB_PATH/$target_link" 2>/dev/null; then
                echo -e "${GREEN}✓ Created symlink: $target_link${NC}"
                success=true
                break
            else
                echo -e "${YELLOW}⚠️ Need sudo permission to create symlink.${NC}"
                echo -e "Attempting with sudo (you may need to enter your password)..."
                
                if sudo ln -sf "$LIB_PATH/$source_lib" "$LIB_PATH/$target_link"; then
                    echo -e "${GREEN}✓ Created symlink with sudo: $target_link${NC}"
                    success=true
                    break
                else
                    echo -e "${RED}Failed to create symlink even with sudo!${NC}"
                fi
            fi
        elif [[ -f "$LIB_PATH/$target_link" ]]; then
            echo -e "${GREEN}✓ Symlink already exists in $LIB_PATH: $target_link${NC}"
            success=true
            break
        elif [[ -f "$LIB_PATH/$source_lib" ]]; then
            # Found source but no target yet
            continue
        fi
    done
    
    if [[ "$success" = false ]]; then
        echo -e "${YELLOW}⚠️ Could not create symlink: $target_link${NC}"
        echo -e "Source libraries were not found in standard locations."
        return 1
    fi
    
    return 0
}

# Create the necessary symlinks for WeasyPrint
echo -e "${BLUE}Creating symbolic links for WeasyPrint libraries...${NC}"

# Map of WeasyPrint expected names to actual library names on macOS
symlinks=(
    "libgobject-2.0.dylib:libgobject-2.0-0"
    "libpango-1.0.dylib:libpango-1.0-0"
    "libpangocairo-1.0.dylib:libpangocairo-1.0-0"
    "libglib-2.0.dylib:libglib-2.0-0"
    "libgdk_pixbuf-2.0.dylib:libgdk_pixbuf-2.0-0"
    "libcairo.2.dylib:libcairo.2"
)

symlink_failures=0
for symlink_pair in "${symlinks[@]}"; do
    source_lib="${symlink_pair%%:*}"
    target_link="${symlink_pair##*:}"
    
    if ! create_symlink "$source_lib" "$target_link"; then
        ((symlink_failures++))
    fi
done

if [[ $symlink_failures -gt 0 ]]; then
    echo -e "\n${YELLOW}⚠️ Some symlinks could not be created.${NC}"
    echo -e "You may need to manually create them later if PDF generation fails:"
    echo -e "Run these commands with sudo:"
    echo -e "  cd /usr/local/lib  (or /opt/homebrew/lib on Apple Silicon Macs)"
    echo -e "  sudo ln -s libgobject-2.0.dylib libgobject-2.0-0"
    echo -e "  sudo ln -s libpango-1.0.dylib libpango-1.0-0"
    echo -e "  sudo ln -s libpangocairo-1.0.dylib libpangocairo-1.0-0"
    echo -e "  sudo ln -s libglib-2.0.dylib libglib-2.0-0"
    echo -e "  sudo ln -s libgdk_pixbuf-2.0.dylib libgdk_pixbuf-2.0-0"
    echo -e "  sudo ln -s libcairo.2.dylib libcairo.2"
else
    echo -e "\n${GREEN}✓ All WeasyPrint symbolic links created successfully${NC}"
fi

# Check if virtualenv is installed, install if missing
if ! command_exists python3 -m venv; then
    echo -e "\n${YELLOW}Installing virtualenv...${NC}"
    pip3 install virtualenv
fi

# Create virtual environment if it doesn't exist
if [[ ! -d "venv" ]]; then
    echo -e "\n${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "\n${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "\n${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Install requirements
echo -e "\n${BLUE}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Install the package in development mode with PDF dependencies
echo -e "\n${BLUE}Installing package with PDF dependencies...${NC}"
pip install -e ".[pdf]"

# PDF dependencies are now included in requirements.txt
echo -e "\n${GREEN}✓ All dependencies including PDF generation installed${NC}"

# Create an executable command
echo -e "\n${BLUE}Setting up land_eval command...${NC}"

# Create the executable script content
SCRIPT_CONTENT="#!/usr/bin/env bash
# Wrapper script for Land Eval

# Path to the project directory
PROJECT_DIR=\"$(pwd)\"

# Activate the virtual environment and run the command
source \"\$PROJECT_DIR/venv/bin/activate\"
python \"\$PROJECT_DIR/main.py\" \"\$@\"
"

# Create a local executable version in the current directory
LOCAL_EXECUTABLE="./land_eval"
echo "$SCRIPT_CONTENT" > "$LOCAL_EXECUTABLE"
chmod +x "$LOCAL_EXECUTABLE"
echo -e "${GREEN}✓ Created executable at $LOCAL_EXECUTABLE${NC}"
echo -e "   You can use it with: ${YELLOW}./land_eval run${NC}"

echo -e "\n${GREEN}===============================================${NC}"
echo -e "${GREEN}Land Eval has been successfully set up!${NC}"
echo -e "${GREEN}===============================================${NC}"
echo -e "\nTo use Land Eval:"
echo -e "1. Activate the virtual environment: ${YELLOW}source venv/bin/activate${NC}"
echo -e "2. Run the application: ${YELLOW}./land_eval run${NC} or ${YELLOW}python main.py run${NC}"
echo -e "\nFor more commands:"
echo -e "   ${YELLOW}./land_eval help${NC}"
echo -e "\nHappy land evaluating!" 