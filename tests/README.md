# Tests Directory

This directory contains all test scripts and tools for the Perpetual Futures Trading Simulator.

## 📋 Available Test Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `test_simulator.py` | Quick functionality test | `python test_simulator.py` |
| `debug_trades.py` | Debug trade data structure | `python debug_trades.py` |
| `analyze_results.py` | Analyze simulation results + charts | `python analyze_results.py` |
| `simulator_with_viz.py` | Live visualization simulator | `python simulator_with_viz.py --hours 12` |
| `visualization_tools.py` | Visualization utilities | Import and use classes |
| `demo_all_tools.py` | Demonstrate all tools | `python demo_all_tools.py` |

## 🚀 Running Tests

### Quick Test
```bash
# From project root
./quick_test.sh
```

### Comprehensive Test Suite
```bash
# From project root
./run_all_tests.sh
```

### Individual Tests
```bash
# From tests directory
cd tests
python test_simulator.py
python debug_trades.py
python analyze_results.py
```

## 📊 Generated Files

After running tests, you'll find:

- `short_simulation_results.json` - 6-hour simulation results
- `24h_simulation_results.json` - 24-hour simulation results  
- `price_chart.png` - Price movement chart
- `demo_results.json` - Demo simulation results
- `logs/` folder - Comprehensive logging

## 🎯 Test Results

The comprehensive test suite runs:
1. ✅ Basic functionality test
2. ✅ Unit tests (pytest)
3. ✅ Short simulation (6 hours)
4. ✅ Trade debugging
5. ✅ Results analysis
6. ✅ Demo all tools
7. ✅ **24-hour simulation** (main test)
8. ✅ Visualization test
9. ✅ Logging system test
10. ✅ File structure check

**Expected Success Rate: 80-100%**

## 🔧 Troubleshooting

If tests fail:
1. Ensure you're in the project root directory
2. Install dependencies: `pip install -r requirements.txt`
3. Check Python path issues
4. Verify file permissions
5. Review configuration files

## 📈 Visualization Features

- **Live price charts** during simulation
- **Real-time PNL tracking** for all users
- **User equity monitoring** over time
- **Comprehensive analysis** with multiple charts
- **PNL heatmaps** showing performance
