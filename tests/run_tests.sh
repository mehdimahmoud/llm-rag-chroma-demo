#!/bin/bash
# Test runner script for running from tests directory
# This provides an alternative to root-level commands

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Test Runner (from tests directory)${NC}"
echo "=================================="

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Function to list available data directories
list_data_directories() {
    local tests_data_dir="tests/data"
    if [ ! -d "$tests_data_dir" ]; then
        echo -e "${YELLOW}No tests/data directory found.${NC}"
        return
    fi
    
    echo -e "${BLUE}Available data directories:${NC}"
    for item in "$tests_data_dir"/*; do
        if [ -d "$item" ]; then
            echo "  - $item"
        fi
    done
}

# Function to run tests
run_tests() {
    local test_type=$1
    local marker=$2
    
    echo -e "${YELLOW}Running $test_type tests...${NC}"
    
    if [ -n "$marker" ]; then
        python -m pytest -m "$marker" --cov=src --cov-report=term-missing
    else
        python -m pytest --cov=src --cov-report=term-missing
    fi
}

# Function to run specific test file
run_specific_test() {
    local test_file=$1
    echo -e "${YELLOW}Running specific test: $test_file${NC}"
    python -m pytest "tests/$test_file" -v
}

# Function to run menu tests with specific data directory
run_menu_with_data() {
    local data_dir=$1
    echo -e "${YELLOW}Running menu tests with data directory: $data_dir${NC}"
    
    # Check if the data directory exists
    if [ ! -d "$data_dir" ]; then
        echo -e "${RED}Error: Data directory not found: $data_dir${NC}"
        return 1
    fi
    
    # Run the menu tests with the specified data directory
    python -c "
import sys
sys.path.insert(0, 'tests')
from test_menu_functionality import run_tests_with_data_directory
success = run_tests_with_data_directory('$data_dir')
sys.exit(0 if success else 1)
"
}

# Function to run all data directory tests
run_all_data_tests() {
    local tests_data_dir="tests/data"
    if [ ! -d "$tests_data_dir" ]; then
        echo -e "${YELLOW}No tests/data directory found.${NC}"
        return
    fi
    
    local all_passed=true
    
    echo -e "${BLUE}Testing with all available data directories:${NC}"
    for data_dir in "$tests_data_dir"/*; do
        if [ -d "$data_dir" ]; then
            echo -e "\n${BLUE}========================================${NC}"
            echo -e "${BLUE}TESTING WITH DATA DIRECTORY: $data_dir${NC}"
            echo -e "${BLUE}========================================${NC}"
            
            if run_menu_with_data "$data_dir"; then
                echo -e "${GREEN}✅ PASSED${NC}"
            else
                echo -e "${RED}❌ FAILED${NC}"
                all_passed=false
            fi
        fi
    done
    
    if [ "$all_passed" = true ]; then
        echo -e "\n${GREEN}🎯 ALL DATA DIRECTORY TESTS PASSED${NC}"
    else
        echo -e "\n${RED}🎯 SOME DATA DIRECTORY TESTS FAILED${NC}"
        return 1
    fi
}

# Parse command line arguments
case "${1:-all}" in
    "all")
        run_tests "all"
        ;;
    "unit")
        run_tests "unit" "unit"
        ;;
    "integration")
        run_tests "integration" "integration"
        ;;
    "e2e")
        run_tests "end-to-end" "e2e"
        ;;
    "menu")
        run_specific_test "test_menu_functionality.py"
        ;;
    "menu-data")
        if [ -n "$2" ]; then
            run_menu_with_data "$2"
        else
            echo -e "${RED}Error: Please specify a data directory${NC}"
            echo "Usage: ./tests/run_tests.sh menu-data <data_directory>"
            exit 1
        fi
        ;;
    "hr-policy")
        run_menu_with_data "tests/data/hr_policy"
        ;;
    "data-all")
        run_all_data_tests
        ;;
    "data-list")
        list_data_directories
        ;;
    "coverage")
        echo -e "${YELLOW}Generating coverage report...${NC}"
        python -m pytest --cov=src --cov-report=html:htmlcov --cov-report=xml:coverage.xml
        echo -e "${GREEN}Coverage report generated in htmlcov/${NC}"
        ;;
    "fast")
        echo -e "${YELLOW}Running tests without coverage (fast)...${NC}"
        python -m pytest --no-cov
        ;;
    "clean")
        echo -e "${YELLOW}Cleaning test artifacts...${NC}"
        rm -rf htmlcov/ .coverage coverage.xml .pytest_cache/
        echo -e "${GREEN}Cleanup complete!${NC}"
        ;;
    "help"|"-h"|"--help")
        echo -e "${BLUE}Available commands:${NC}"
        echo "  all         - Run all tests with coverage"
        echo "  unit        - Run unit tests only"
        echo "  integration - Run integration tests only"
        echo "  e2e         - Run end-to-end tests only"
        echo "  menu        - Run menu functionality tests"
        echo "  menu-data   - Run menu tests with specific data directory"
        echo "  hr-policy   - Run tests with HR policy data"
        echo "  data-all    - Run tests with all available data directories"
        echo "  data-list   - List all available data directories"
        echo "  coverage    - Generate coverage report"
        echo "  fast        - Run tests without coverage"
        echo "  clean       - Clean test artifacts"
        echo "  help        - Show this help"
        echo ""
        echo -e "${YELLOW}Usage:${NC}"
        echo "  ./tests/run_tests.sh [command] [options]"
        echo ""
        echo -e "${YELLOW}Examples:${NC}"
        echo "  ./tests/run_tests.sh all"
        echo "  ./tests/run_tests.sh e2e"
        echo "  ./tests/run_tests.sh hr-policy"
        echo "  ./tests/run_tests.sh menu-data tests/data/research_papers"
        echo "  ./tests/run_tests.sh data-all"
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo "Run './tests/run_tests.sh help' for available commands"
        exit 1
        ;;
esac

echo -e "${GREEN}✅ Test execution complete!${NC}" 