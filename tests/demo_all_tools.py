#!/usr/bin/env python3
"""
Example usage of all trading simulator tools and visualizations.
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and show its output."""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}")
    print()
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def main():
    """Demonstrate all tools."""
    print("🚀 TRADING SIMULATOR TOOLS DEMONSTRATION")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("../src/simulator.py"):
        print("❌ Please run this script from the tests directory")
        sys.exit(1)
    
    print("📋 Available Tools:")
    print("1. test_simulator.py - Quick functionality test")
    print("2. debug_trades.py - Debug trade data")
    print("3. analyze_results.py - Analyze simulation results")
    print("4. simulator_with_viz.py - Live visualization simulator")
    print("5. main.py - Standard simulator")
    print("6. visualization_tools.py - Visualization utilities")
    print()
    
    # Test basic functionality
    if not run_command("python test_simulator.py", "Testing Basic Functionality"):
        print("❌ Basic functionality test failed")
        return
    
    # Run a short simulation
    if not run_command("python ../main.py --config ../configs/sample_config.json --hours 6", 
                      "Running Short Simulation"):
        print("❌ Simulation failed")
        return
    
    # Analyze the results
    if not run_command("python analyze_results.py", "Analyzing Results"):
        print("❌ Analysis failed")
        return
    
    # Debug trades
    if not run_command("python debug_trades.py", "Debugging Trade Data"):
        print("❌ Trade debugging failed")
        return
    
    print("\n🎉 All tools demonstrated successfully!")
    print("\n📊 Generated Files:")
    print("   - demo_results.json (simulation results)")
    print("   - demo_results_detailed_logs.json (detailed logs)")
    print("   - price_chart.png (price movement chart)")
    print("   - logs/ folder (comprehensive logging)")
    
    print("\n🚀 Next Steps:")
    print("1. Run longer simulation: python main.py --hours 24")
    print("2. Try live visualization: python simulator_with_viz.py --hours 12")
    print("3. Analyze specific results: python simulator_with_viz.py --analyze results.json")
    print("4. Run comprehensive tests: pytest tests/ -v")

if __name__ == "__main__":
    main()
