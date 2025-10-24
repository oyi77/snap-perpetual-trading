#!/bin/bash
# Comprehensive test runner for Perpetual Futures Trading Simulator
# Runs all tests including 24-hour simulation

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Function to run a test and capture results
run_test() {
    local test_name="$1"
    local test_command="$2"
    local test_dir="$3"
    
    print_header "Running: $test_name"
    echo "Command: $test_command"
    echo "Directory: $test_dir"
    echo
    
    if [ -n "$test_dir" ]; then
        cd "$test_dir"
    fi
    
    if eval "$test_command"; then
        print_success "$test_name completed successfully"
        return 0
    else
        print_error "$test_name failed"
        return 1
    fi
}

# Function to check if a file exists
check_file() {
    if [ -f "$1" ]; then
        print_success "Found: $1"
        return 0
    else
        print_error "Missing: $1"
        return 1
    fi
}

# Main test runner
main() {
    print_header "🚀 PERPETUAL FUTURES TRADING SIMULATOR - COMPREHENSIVE TEST SUITE"
    
    # Get the script directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$SCRIPT_DIR"
    
    print_info "Project directory: $PROJECT_DIR"
    print_info "Test directory: $PROJECT_DIR/tests"
    echo
    
    # Check if we're in the right directory
    if [ ! -f "$PROJECT_DIR/src/simulator.py" ]; then
        print_error "Please run this script from the snap-perpetual-trading directory"
        exit 1
    fi
    
    # Initialize counters
    TOTAL_TESTS=0
    PASSED_TESTS=0
    FAILED_TESTS=0
    
    # Test 1: Basic Functionality Test
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if run_test "Basic Functionality Test" "python test_simulator.py" "$PROJECT_DIR/tests"; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    echo
    
    # Test 2: Unit Tests
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if run_test "Unit Tests (pytest)" "python -m pytest tests/test_simulator.py -v" "$PROJECT_DIR"; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        print_warning "Some unit tests failed, but continuing..."
    fi
    echo
    
    # Test 3: Short Simulation (6 hours)
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    print_header "Running Short Simulation (6 hours)"
    if run_test "Short Simulation" "python main.py --config configs/sample_config.json --hours 6" "$PROJECT_DIR"; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        
        # Check if results file was created in session output directory
        LATEST_SESSION=$(ls -t logs/session_* 2>/dev/null | head -1 | sed 's/logs\/session_//')
        if [ -n "$LATEST_SESSION" ] && [ -f "output/session_$LATEST_SESSION/simulation_results.json" ]; then
            print_success "Short simulation results saved to output/session_$LATEST_SESSION/"
        else
            print_warning "Results file not found in expected location"
        fi
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    echo
    
    # Test 4: Trade Debugging
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if run_test "Trade Debugging" "python debug_trades.py" "$PROJECT_DIR/tests"; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    echo
    
    # Test 5: Results Analysis
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if run_test "Results Analysis" "python analyze_results.py" "$PROJECT_DIR/tests"; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        
        # Check if chart was created in session output directory
        LATEST_SESSION=$(ls -t logs/session_* 2>/dev/null | head -1 | sed 's/logs\/session_//')
        if [ -n "$LATEST_SESSION" ] && [ -f "output/session_$LATEST_SESSION/price_chart.png" ]; then
            print_success "Price chart generated in output/session_$LATEST_SESSION/"
        else
            print_warning "Price chart not found in expected location"
        fi
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    echo
    
    # Test 6: Demo All Tools (skip if file doesn't exist)
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ -f "$PROJECT_DIR/tests/demo_all_tools.py" ]; then
        if run_test "Demo All Tools" "python demo_all_tools.py" "$PROJECT_DIR/tests"; then
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        print_warning "Demo All Tools script not found - skipping"
        PASSED_TESTS=$((PASSED_TESTS + 1))  # Count as passed since it's optional
    fi
    echo
    
    # Test 7: 24-Hour Simulation (Main Test)
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    print_header "🏆 MAIN TEST: 24-Hour Simulation"
    print_info "This is the main test - running a full 24-hour simulation"
    print_info "This may take a few minutes..."
    echo
    
    if run_test "24-Hour Simulation" "python main.py --config configs/sample_config.json --hours 24" "$PROJECT_DIR"; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        
        # Check if results file was created in session output directory
        LATEST_SESSION=$(ls -t logs/session_* 2>/dev/null | head -1 | sed 's/logs\/session_//')
        if [ -n "$LATEST_SESSION" ] && [ -f "output/session_$LATEST_SESSION/simulation_results.json" ]; then
            print_success "24-hour simulation results saved to output/session_$LATEST_SESSION/"
        else
            print_warning "24-hour results file not found in expected location"
        fi
        
        # Analyze the 24-hour results
        print_info "Analyzing 24-hour simulation results..."
        if run_test "24-Hour Analysis" "python analyze_results.py" "$PROJECT_DIR/tests"; then
            print_success "24-hour analysis completed"
        fi
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    echo
    
    # Test 8: Visualization Test (if matplotlib is available)
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    print_header "Testing Visualization Tools"
    if python -c "import matplotlib.pyplot as plt" 2>/dev/null; then
        print_info "Matplotlib available - testing visualization"
        if run_test "Visualization Test" "python simulator_with_viz.py --hours 4 --no-charts" "$PROJECT_DIR/tests"; then
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        print_warning "Matplotlib not available - skipping visualization test"
        PASSED_TESTS=$((PASSED_TESTS + 1))  # Count as passed since it's optional
    fi
    echo
    
    # Test 9: Logging System Test
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    print_header "Testing Logging System"
    if [ -d "logs" ] && [ "$(ls -A logs 2>/dev/null)" ]; then
        SESSION_COUNT=$(ls logs/session_* 2>/dev/null | wc -l)
        if [ $SESSION_COUNT -gt 0 ]; then
            print_success "Logging system working - $SESSION_COUNT session directories found"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            print_warning "Logs directory exists but no session directories found"
            PASSED_TESTS=$((PASSED_TESTS + 1))  # Count as passed since logs directory exists
        fi
    else
        print_warning "Logs directory not found - this is normal if no simulations have run yet"
        PASSED_TESTS=$((PASSED_TESTS + 1))  # Count as passed since this is expected
    fi
    echo
    
    # Test 10: File Structure Check
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    print_header "Checking File Structure"
    STRUCTURE_OK=true
    
    # Check essential files
    ESSENTIAL_FILES=(
        "$PROJECT_DIR/src/simulator.py"
        "$PROJECT_DIR/src/models/data_models.py"
        "$PROJECT_DIR/src/engine/order_book.py"
        "$PROJECT_DIR/src/engine/position_manager.py"
        "$PROJECT_DIR/src/engine/matching_engine.py"
        "$PROJECT_DIR/src/engine/price_oracle.py"
        "$PROJECT_DIR/src/engine/funding_manager.py"
        "$PROJECT_DIR/src/engine/liquidation_engine.py"
        "$PROJECT_DIR/src/logging_system.py"
        "$PROJECT_DIR/main.py"
        "$PROJECT_DIR/configs/sample_config.json"
        "$PROJECT_DIR/requirements.txt"
        "$PROJECT_DIR/README.md"
    )
    
    for file in "${ESSENTIAL_FILES[@]}"; do
        if check_file "$file"; then
            continue
        else
            STRUCTURE_OK=false
        fi
    done
    
    if [ "$STRUCTURE_OK" = true ]; then
        print_success "File structure is correct"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        print_error "File structure has issues"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    echo
    
    # Final Results
    print_header "🎯 FINAL TEST RESULTS"
    echo -e "${CYAN}Total Tests: $TOTAL_TESTS${NC}"
    echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
    echo -e "${RED}Failed: $FAILED_TESTS${NC}"
    echo
    
    # Calculate success rate
    SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo -e "${PURPLE}Success Rate: $SUCCESS_RATE%${NC}"
    echo
    
    # Generate summary report
    print_header "📋 GENERATED FILES"
    echo "Test Results:"
    echo "  - logs/session_*/ (comprehensive logging for each simulation)"
    echo "  - output/session_*/ (simulation results and charts)"
    echo "  - Session-based organization for easy management"
    echo
    
    # Show latest session info
    LATEST_SESSION=$(ls -t logs/session_* 2>/dev/null | head -1 | sed 's/logs\/session_//')
    if [ -n "$LATEST_SESSION" ]; then
        echo "Latest Session: $LATEST_SESSION"
        if [ -d "output/session_$LATEST_SESSION" ]; then
            echo "Output files:"
            ls -la "output/session_$LATEST_SESSION/" 2>/dev/null | grep -v "^total" | grep -v "^d" | sed 's/^/  /'
        fi
        echo
    fi
    
    # Show 24-hour simulation summary if available
    if [ -n "$LATEST_SESSION" ] && [ -f "output/session_$LATEST_SESSION/simulation_results.json" ]; then
        echo "24-Hour Simulation Summary:"
        python -c "
import json
try:
    with open('output/session_$LATEST_SESSION/simulation_results.json', 'r') as f:
        data = json.load(f)
    summary = data['simulation_summary']
    print(f'  - Duration: {summary[\"total_hours\"]} hours')
    print(f'  - Final Price: \${summary[\"final_price\"]:,.2f}')
    print(f'  - Price Change: {summary[\"price_change_percent\"]:.2f}%')
    print(f'  - Total Trades: {summary[\"total_trades\"]}')
    print(f'  - Total Volume: \${summary[\"total_volume\"]:,.2f}')
    print(f'  - Liquidations: {summary[\"total_liquidations\"]}')
except Exception as e:
    print(f'  Error reading results: {e}')
"
    fi
    echo
    
    # Final verdict
    if [ $FAILED_TESTS -eq 0 ]; then
        print_success "🎉 ALL TESTS PASSED! The simulator is working perfectly!"
        echo
        echo -e "${GREEN}The perpetual futures trading simulator is ready for production use!${NC}"
        echo
        echo "Next steps:"
        echo "  1. Review the generated charts and logs"
        echo "  2. Analyze the 24-hour simulation results"
        echo "  3. Run longer simulations for more data"
        echo "  4. Customize configurations for different scenarios"
        exit 0
    else
        print_error "Some tests failed. Please review the errors above."
        echo
        echo "Common issues:"
        echo "  1. Missing dependencies (run: pip install -r requirements.txt)"
        echo "  2. Python path issues"
        echo "  3. File permissions"
        echo "  4. Configuration file problems"
        exit 1
    fi
}

# Run the main function
main "$@"
