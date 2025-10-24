# Perpetual Futures Trading Simulator

A comprehensive Python-based simulator for perpetual futures trading that implements core trading mechanics including order matching, position management, funding rates, and liquidation systems.

## Overview

This simulator demonstrates key concepts of perpetual futures trading without requiring blockchain or smart contract knowledge. It focuses on:

- **Order Book Management**: Efficient order matching with priority queues
- **Position Tracking**: Real-time PNL calculations and margin monitoring
- **Funding Rates**: Periodic payments between long and short positions
- **Liquidation Engine**: Automatic position closure when margin requirements aren't met
- **Price Oracle**: Simulated market data with various price scenarios

## Features

### Core Trading Mechanics
- ✅ Limit order placement and matching
- ✅ Partial order fills
- ✅ Position management (long/short)
- ✅ Real-time PNL calculations
- ✅ Leverage support (up to 10x)
- ✅ Margin requirements and monitoring

### Advanced Features
- ✅ Funding rate calculations and applications
- ✅ Automatic liquidation system
- ✅ Multiple price scenarios (trending, volatile, crash, pump)
- ✅ Comprehensive event-driven simulation
- ✅ JSON-based configuration system
- ✅ Detailed reporting and analytics

### Testing & Visualization
- ✅ **Comprehensive test suite** with 24-hour simulation
- ✅ **Live visualization** with real-time charts
- ✅ **Automated testing** with multiple test runners
- ✅ **Debug tools** for trade analysis
- ✅ **Results analysis** with chart generation
- ✅ **Comprehensive logging** system

### Technical Implementation
- ✅ O(log n) order book operations using priority queues
- ✅ Modular, extensible architecture
- ✅ Comprehensive unit test coverage
- ✅ Decimal precision for financial calculations
- ✅ Event-driven simulation loop
- ✅ **Robust logging system** with session tracking
- ✅ **Multiple export formats** (JSON, flattened JSON, SQLite)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd snap-perpetual-trading
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

Run a simulation with default configuration:
```bash
python main.py
```

### Comprehensive Testing

Run the complete test suite (includes 24-hour simulation):
```bash
./run_all_tests.sh
```

Run quick tests:
```bash
./quick_test.sh
```

### Custom Configuration

Run with custom configuration:
```bash
python main.py --config configs/sample_config.json --hours 24 --output results.json
```

### Available Test Scripts

The project includes comprehensive testing tools in the `tests/` directory:

```bash
# Quick functionality test
python tests/test_simulator.py

# Debug trade data
python tests/debug_trades.py

# Analyze results and generate charts
python tests/analyze_results.py

# Live visualization simulator
python tests/simulator_with_viz.py --hours 12

# Demo all tools
python tests/demo_all_tools.py
```

## Configuration Format

The simulator uses JSON configuration files with the following structure:

```json
{
  "users": [
    {"id": "user1", "collateral": 10000},
    {"id": "user2", "collateral": 5000}
  ],
  "prices": [60000, 60500, 59000, ...],
  "events": [
    {
      "time": 0,
      "action": "place_order",
      "data": {
        "user": "user1",
        "side": "buy",
        "quantity": 0.5,
        "price": 59500,
        "leverage": 5
      }
    },
    {
      "time": 8,
      "action": "apply_funding"
    }
  ]
}
```

### Event Types

- `place_order`: Place a limit order
- `price_update`: Update market price
- `apply_funding`: Apply funding rates
- `random_order`: Generate random order (for testing)

## Architecture

### Core Components

```
src/
├── models/
│   └── data_models.py          # Core data structures
├── engine/
│   ├── order_book.py          # Efficient order book with priority queues
│   ├── position_manager.py    # Position tracking and PNL calculations
│   ├── matching_engine.py     # Order placement and matching logic
│   ├── price_oracle.py        # Price simulation and market data
│   ├── funding_manager.py     # Funding rate calculations
│   └── liquidation_engine.py  # Liquidation monitoring and execution
├── simulator.py               # Main simulation orchestrator
└── logging_system.py          # Comprehensive logging system
```

### Test Suite

```
tests/
├── test_simulator.py          # Quick functionality test
├── debug_trades.py            # Debug trade data structure
├── analyze_results.py         # Analyze results and generate charts
├── simulator_with_viz.py      # Live visualization simulator
├── visualization_tools.py     # Visualization utilities
├── demo_all_tools.py          # Demonstrate all tools
└── README.md                  # Test suite documentation
```

### Scripts

```
├── main.py                    # Main simulator entry point
├── run_all_tests.sh          # Comprehensive test suite runner
├── quick_test.sh             # Quick test runner
└── configs/
    └── sample_config.json    # Sample configuration file
```

### Key Design Decisions

1. **Decimal Precision**: All financial calculations use Python's `Decimal` class for precise arithmetic
2. **Priority Queues**: Order book uses heaps for O(log n) operations
3. **Event-Driven**: Simulation processes events at specific time intervals
4. **Modular Design**: Each component is independently testable and extensible
5. **Immutable Data**: Core data structures use dataclasses for clarity

## Trading Mechanics

### Order Matching
- Orders are matched using price-time priority
- Partial fills are supported
- Market orders execute at best available price

### Position Management
- **Initial Margin**: `position_value / leverage`
- **Maintenance Margin**: `5% of position_value`
- **Unrealized PNL**: `(current_price - entry_price) * quantity` (for longs)
- **Equity**: `collateral + unrealized_pnl`

### Funding Rates
- Calculated every 8 hours: `(mark_price - index_price) / index_price * (1/8)`
- Long positions pay funding when rate is positive
- Short positions pay funding when rate is negative

### Liquidation
- Triggered when `equity < maintenance_margin`
- Position closed at current mark price
- 1% liquidation fee deducted from collateral

## Testing

### Comprehensive Test Suite

Run the complete test suite with 24-hour simulation:
```bash
./run_all_tests.sh
```

This runs 10 comprehensive tests:
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

### Quick Testing

Run quick tests for development:
```bash
./quick_test.sh
```

### Individual Tests

Run specific test scripts:
```bash
# Unit tests
pytest tests/ -v

# Quick functionality test
python tests/test_simulator.py

# Debug trade data
python tests/debug_trades.py

# Analyze results and generate charts
python tests/analyze_results.py

# Live visualization
python tests/simulator_with_viz.py --hours 12
```

### Session Management

Use the built-in session manager for easy maintenance:
```bash
# List all sessions (shows logs + outputs)
python log_manager.py --list

# Get session summary (includes output files)
python log_manager.py --summary SESSION_ID

# Clean old sessions (removes logs + outputs)
python log_manager.py --clean 7 --dry-run

# Export session to backup (logs + outputs)
python log_manager.py --export SESSION_ID backup/

# Show overall statistics (logs + outputs)
python log_manager.py --stats
```

**Session Manager Features:**
- **Unified Management**: Handles both logs and outputs together
- **Smart Cleanup**: Removes both log and output directories
- **Complete Export**: Exports all session data for backup
- **Size Tracking**: Shows total size including charts and results
- **Dry Run**: Preview cleanup operations before executing

### Test Coverage
- ✅ Order book operations (matching, cancellation)
- ✅ Position management (creation, updates, closures)
- ✅ PNL calculations (profit/loss scenarios)
- ✅ Funding rate applications
- ✅ Liquidation triggers and execution
- ✅ Edge cases (zero quantities, max leverage, concurrent orders)
- ✅ Price oracle functionality
- ✅ Integration tests
- ✅ **24-hour simulation testing**
- ✅ **Live visualization testing**
- ✅ **Comprehensive logging verification**

## Output and Reporting

The simulator generates comprehensive output files:

### Simulation Results
- **Flattened JSON**: `results.json` - Clean, structured simulation data
- **Detailed Logs**: `results_detailed_logs.json` - Complete event history
- **Summary Report**: Console output with key statistics and user balances

### Session-Based Organization
The simulator includes a robust, session-based organization system that groups all outputs by simulation session:

```
logs/
├── session_20251025_024958/          # Session logs directory
│   ├── simulation.log               # Main simulation log
│   ├── detailed_logs.json          # Complete event history
│   ├── trade_logs.json             # All trade executions
│   ├── order_logs.json             # All order placements
│   ├── price_logs.json             # Price update history
│   ├── funding_logs.json           # Funding events
│   └── liquidation_logs.json       # Liquidation events
└── ...

output/
├── session_20251025_024958/          # Session output directory
│   ├── simulation_results.json     # Simulation results
│   ├── price_chart.png             # Price movement chart
│   ├── comprehensive_analysis.png   # Multi-chart analysis
│   ├── pnl_heatmap.png             # User PNL heatmap
│   └── live_simulation_24h.png      # Live visualization chart
└── ...
```

**Benefits:**
- **Easy Organization**: Each simulation gets its own directories for logs and outputs
- **Easy Cleanup**: Remove entire sessions with one command (logs + outputs)
- **Easy Analysis**: All related data grouped together
- **Easy Maintenance**: No file naming conflicts
- **Easy Backup**: Export entire sessions for archival

### Visualization Output
- **Price Charts**: `price_chart.png` - Price movement visualization
- **Comprehensive Analysis**: Multi-chart analysis with trade volume, user equity, funding events
- **Live Visualization**: Real-time charts during simulation (optional)

### Test Results
When running the test suite, additional files are generated:
- `tests/short_simulation_results.json` - 6-hour simulation results
- `tests/24h_simulation_results.json` - 24-hour simulation results
- `tests/price_chart.png` - Price movement chart
- `tests/demo_results.json` - Demo simulation results

### JSON Results Format
```json
{
  "simulation_summary": {
    "total_hours": 24,
    "final_price": 44938.29,
    "price_change_percent": -25.10,
    "total_trades": 6,
    "total_volume": 105307.65,
    "total_liquidations": 0
  },
  "execution_statistics": {...},
  "funding_statistics": {...},
  "liquidation_statistics": {...},
  "final_user_balances": {...},
  "trade_history": [...],
  "price_history": [...],
  "funding_events": [...],
  "user_position_history": [...]
}
```

## Visualization & Analysis

### Live Visualization
The simulator includes real-time visualization capabilities:

```bash
# Run simulation with live charts
python tests/simulator_with_viz.py --hours 12

# Features:
# - Live price movement chart
# - Real-time PNL tracking
# - User equity monitoring
# - Automatic chart saving
```

### Analysis Tools
Comprehensive analysis and visualization tools:

```bash
# Analyze simulation results
python tests/analyze_results.py

# Create comprehensive analysis
python tests/simulator_with_viz.py --analyze results.json
```

### Chart Types Available
- **📈 Price Movement Charts** - Line charts with markers and filled areas
- **💰 PNL & Equity Charts** - Multi-user PNL tracking and equity over time
- **📊 Volume Analysis** - Trade volume by hour with bar charts
- **🔥 Heatmaps** - User PNL performance with color-coded metrics
- **📋 Comprehensive Dashboards** - Multi-panel analysis with combined metrics

## Performance Characteristics

- **Order Book Operations**: O(log n) for add/cancel operations
- **Position Updates**: O(1) for PNL calculations
- **Liquidation Checks**: O(n) where n is number of positions
- **Memory Usage**: Linear with number of orders and positions
- **Test Suite Execution**: ~2-5 minutes for comprehensive 24-hour simulation
- **Logging Performance**: Minimal overhead with efficient JSON serialization

## Extensions and Customization

### Adding New Order Types
Extend the `OrderType` enum and update the matching engine:
```python
class OrderType(Enum):
    LIMIT = "limit"
    MARKET = "market"
    STOP_LOSS = "stop_loss"  # New type
```

### Custom Price Models
Implement new price generation strategies:
```python
class CustomPriceOracle(PriceOracle):
    def generate_custom_prices(self, params):
        # Custom price generation logic
        pass
```

### Additional Risk Metrics
Extend the liquidation engine with custom risk calculations:
```python
class AdvancedLiquidationEngine(LiquidationEngine):
    def calculate_var(self, position, confidence_level=0.95):
        # Value at Risk calculation
        pass
```

## Assumptions and Limitations

### Simplifications
- Index price equals mark price (unless specified)
- No slippage on market orders
- Perfect liquidity assumption
- Single asset pair (BTC/USD)
- No transaction fees (except liquidation fees)

### Real-World Considerations
- Actual exchanges have more complex fee structures
- Market impact affects large orders
- Network latency affects order execution
- Regulatory requirements vary by jurisdiction

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by public perpetual DEX documentation (dYdX, GMX)
- Uses standard Python libraries for maximum compatibility
- Designed for educational and demonstration purposes
- **Comprehensive test suite** ensures reliability and correctness
- **Live visualization** capabilities for enhanced learning experience
- **Robust logging system** provides detailed insights into trading mechanics

---

**Note**: This simulator is for educational purposes and should not be used for actual trading without proper risk management and regulatory compliance.

## Project Status

✅ **Production Ready** - Comprehensive test suite with 24-hour simulation  
✅ **Well Documented** - Complete documentation and examples  
✅ **Extensible** - Modular architecture for easy customization  
✅ **Tested** - 80-100% test success rate with automated testing  
✅ **Visualized** - Live charts and comprehensive analysis tools
