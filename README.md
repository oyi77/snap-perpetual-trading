# Perpetual Futures Trading Simulator

I built this simulator to understand how perpetual futures trading actually works under the hood. After getting confused by all the DeFi jargon and complex smart contracts, I decided to create a simple Python simulator that focuses on the core mechanics.

## What This Does

Ever wondered how perpetual futures actually work? This simulator breaks down the key components:

- **Order matching** - How buy and sell orders get paired up
- **Position tracking** - Real-time profit/loss calculations  
- **Funding rates** - Those periodic payments between longs and shorts
- **Liquidations** - What happens when you're over-leveraged
- **Price movements** - Simulated market data for testing

## What's Included

### The Basics
- Order placement and matching (limit orders)
- Partial fills when orders don't match completely
- Long and short position management
- Real-time profit/loss calculations
- Leverage up to 10x (be careful!)
- Margin monitoring and requirements

### The Advanced Stuff
- Funding rate calculations (every 8 hours)
- Automatic liquidations when you're underwater
- Different market scenarios (bull runs, crashes, sideways)
- Event-driven simulation (realistic timing)
- JSON configs for custom scenarios
- Detailed reports and analytics

### Testing & Debugging
- Full test suite including 24-hour simulations
- Live charts during simulation
- Automated test runners
- Debug tools to see what's happening
- Chart generation for analysis
- Comprehensive logging (because debugging is hard)

### Under the Hood
- Fast order book using priority queues
- Modular design (easy to extend)
- Lots of unit tests
- Decimal precision (no floating point errors)
- Event-driven simulation
- Session-based logging
- Multiple export formats

## Getting Started

First, grab the code:
```bash
git clone <repository-url>
cd snap-perpetual-trading
```

Then install what you need:
```bash
pip install -r requirements.txt
```

You'll need:
- `pytest` - For running tests
- `matplotlib` - For charts (optional but recommended)
- `pandas` - For data analysis

## Running Simulations

### Quick Test
Want to see it in action? Just run:
```bash
python main.py
```

### Full Test Suite
For the complete experience (this takes a few minutes):
```bash
./run_all_tests.sh
```

This runs everything including a 24-hour simulation. Grab some coffee.

### Custom Scenarios
You can create different market conditions:
```bash
# Market crash simulation
python main.py --generate-config configs/crash_config.json --scenario crash

# Bull run simulation  
python main.py --generate-config configs/pump_config.json --scenario pump

# Custom hours
python main.py --config configs/sample_config.json --hours 24
```

### Quick Tests
For faster development cycles:
```bash
./quick_test.sh
```

## How to Configure

Everything is controlled through JSON config files. Here's the basic structure:

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

### What You Can Do

- `place_order` - Put in a buy/sell order
- `price_update` - Change the market price
- `apply_funding` - Apply those funding payments
- `random_order` - Generate random orders (for testing chaos)

## How It's Built

### The Main Parts

```
src/
├── models/
│   └── data_models.py          # All the data structures
├── engine/
│   ├── order_book.py          # Where orders live and get matched
│   ├── position_manager.py    # Tracks your positions and PNL
│   ├── matching_engine.py     # Actually matches buy/sell orders
│   ├── price_oracle.py        # Generates fake market data
│   ├── funding_manager.py     # Calculates funding payments
│   └── liquidation_engine.py  # Liquidates you when you're broke
├── simulator.py               # Runs the whole show
└── logging_system.py          # Keeps track of everything
```

### Testing Stuff

```
tests/
├── test_simulator.py          # Quick smoke test
├── debug_trades.py            # Debug what went wrong
├── analyze_results.py         # Generate charts
├── simulator_with_viz.py      # Live charts during simulation
├── visualization_tools.py     # Chart utilities
├── demo_all_tools.py          # Shows off all features
└── README.md                  # Test documentation
```

### Scripts

```
├── main.py                    # Main entry point
├── run_all_tests.sh          # Runs everything
├── quick_test.sh             # Quick tests
└── configs/
    └── sample_config.json    # Example config
```

### Why It's Built This Way

1. **Decimal math** - No floating point errors with money
2. **Priority queues** - Fast order matching
3. **Event-driven** - Realistic timing
4. **Modular** - Easy to change parts
5. **Immutable data** - Less bugs, easier debugging

## What Assumed (And Why)

### The Simplifications Made

**Market Stuff:**
- **Only BTC/USD** - Adding more pairs gets messy fast
- **Perfect liquidity** - No slippage, orders always fill at the price you want
- **Instant execution** - No network delays or confirmation times
- **No trading fees** - Except liquidation fees (1%) because those are important

**Price Stuff:**
- **Mark price = Index price** - Makes funding calculations simpler
- **No market impact** - Your big orders don't move the market
- **Fake price data** - Mathematical models instead of real market chaos

**Risk Stuff:**
- **5% maintenance margin** - Fixed across all conditions (real exchanges vary this)
- **Instant liquidations** - No grace period when you're underwater
- **Full position closure** - No partial liquidations
- **No insurance fund** - Perfect counterparty risk (ha!)

### Why Built It This Way

This is designed to be **educational first**. I prioritized making the core concepts clear over production complexity. The event-driven approach lets you see exactly when things happen, and using immutable data structures means fewer weird bugs.

The testing philosophy is different too - instead of just unit tests, i included 24-hour simulations and visualization tools. This helps you understand how everything works together in realistic scenarios, not just in isolation. The modular design means you can easily add new order types or risk models without breaking everything else.

## How Trading Actually Works

### Order Matching
- First come, first served at the same price
- Partial fills happen when orders don't match completely
- Market orders grab the best available price

### Position Math
- **Initial Margin**: `position_value / leverage` (how much you need to open)
- **Maintenance Margin**: `5% of position_value` (minimum to stay open)
- **Unrealized PNL**: `(current_price - entry_price) * quantity` (for longs)
- **Equity**: `collateral + unrealized_pnl` (your total value)

### Funding Payments
- Calculated every 8 hours: `(mark_price - index_price) / index_price * (1/8)`
- Longs pay when rate is positive (market is bullish)
- Shorts pay when rate is negative (market is bearish)

### Getting Liquidated
- Happens when `equity < maintenance_margin`
- Position gets closed at current market price
- You lose 1% as a liquidation fee

## Testing Everything

### The Full Monty
Want to see everything in action? Run the complete test suite:
```bash
./run_all_tests.sh
```

This runs 12 different tests including a 24-hour simulation and liquidation events. It takes a few minutes but shows you everything working together.

### Quick Tests
For faster development:
```bash
./quick_test.sh
```

### Individual Tests
Want to test specific parts?
```bash
# All unit tests
pytest tests/ -v

# Quick smoke test
python tests/test_simulator.py

# Debug what went wrong
python tests/debug_trades.py

# Generate charts from results
python tests/analyze_results.py

# Live charts during simulation
python tests/simulator_with_viz.py --hours 12

# See all tools in action
python tests/demo_all_tools.py

# Test liquidation events
python tests/test_liquidation_scenario.py
```

### Managing Your Sessions
The simulator creates separate directories for each run (so you don't lose data). You can manage them:

```bash
# See all your sessions
python log_manager.py --list

# Get details about a specific session
python log_manager.py --summary SESSION_ID

# Clean up old sessions (dry run first!)
python log_manager.py --clean 7 --dry-run

# Backup a session
python log_manager.py --export SESSION_ID backup/

# Overall stats
python log_manager.py --stats
```

**What this gives you:**
- **Easy cleanup** - Remove old sessions without losing important ones
- **Complete backups** - Export everything for a session
- **Size tracking** - See how much space you're using
- **Session format** - `YYYYMMDD_HHMMSS` (like `20251025_143022`)

### What Gets Tested
- Order book operations (matching, cancellation)
- Position management (creation, updates, closures)
- PNL calculations (profit/loss scenarios)
- Funding rate applications
- Liquidation triggers and execution
- Edge cases (zero quantities, max leverage, concurrent orders)
- Price oracle functionality
- Integration tests
- 24-hour simulation testing
- Live visualization testing
- Comprehensive logging verification

## What You Get

The simulator spits out a bunch of files to help you understand what happened:

### The Main Results
- **JSON results** - Clean, structured data about your simulation
- **Detailed logs** - Every single event that happened
- **Console summary** - Key stats and final balances printed to screen

### Session-Based Organization
The simulator creates separate directories for each run (so you don't lose data). Here's how it organizes everything:

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

**Why this is useful:**
- **No confusion** - Each simulation gets its own folder
- **Easy cleanup** - Delete old sessions without losing important ones
- **Everything together** - All related data in one place
- **No naming conflicts** - Each session has a unique timestamp
- **Easy backups** - Export entire sessions for safekeeping

### Charts and Visualizations
- **Price charts** - See how prices moved over time
- **PNL tracking** - Watch profits and losses evolve
- **Trade volume** - See when the action happened
- **Live charts** - Real-time updates during simulation (optional)

### JSON Results Format
Here's what the output looks like:
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

## Charts and Analysis

### Live Charts
Want to watch the simulation in real-time? The simulator can show live charts:

```bash
# Run simulation with live charts
python tests/simulator_with_viz.py --hours 12

# Analyze existing results
python tests/simulator_with_viz.py --analyze results.json
```

This gives you:
- Live price movement charts
- Real-time PNL tracking
- User equity monitoring
- Automatic chart saving

### Analysis Tools
Got some results you want to dig into?

```bash
# Analyze the most recent simulation
python tests/analyze_results.py

# Analyze a specific file
python tests/analyze_results.py path/to/results.json
```

### What Charts You Get
- **Price charts** - Line charts showing price movements
- **PNL charts** - Track profits and losses over time
- **Volume charts** - See when trades happened
- **Heatmaps** - Color-coded performance metrics
- **Dashboard views** - Multiple charts in one view

## Performance Notes

Here's how fast things run:
- **Order book** - O(log n) for adding/canceling orders
- **Position updates** - O(1) for PNL calculations  
- **Liquidation checks** - O(n) where n is number of positions
- **Memory usage** - Grows linearly with orders and positions
- **Test suite** - Takes about 2-5 minutes for a full 24-hour simulation
- **Logging** - Minimal overhead, efficient JSON serialization

## Extending the Simulator

Want to add your own features? The modular design makes it pretty easy:

### New Order Types
Add stop-loss orders or whatever you want:
```python
class OrderType(Enum):
    LIMIT = "limit"
    MARKET = "market"
    STOP_LOSS = "stop_loss"  # Your new type here
```

### Custom Price Models
Implement your own price generation:
```python
class CustomPriceOracle(PriceOracle):
    def generate_custom_prices(self, params):
        # Your custom logic here
        pass
```

### Advanced Risk Metrics
Add Value at Risk or other fancy stuff:
```python
class AdvancedLiquidationEngine(LiquidationEngine):
    def calculate_var(self, position, confidence_level=0.95):
        # VaR calculation here
        pass
```

## What's Missing (Real World Stuff)

This simulator simplifies a lot of things to focus on the core mechanics. In the real world:

### What Simplified
- Index price = mark price (makes funding easier to understand)
- No slippage (orders always fill at the price you want)
- Perfect liquidity (infinite market depth)
- Only BTC/USD (adding more pairs gets complicated)
- No trading fees (except liquidation fees)

### Real Exchanges Are More Complex
- Fee structures are way more complicated
- Large orders actually move the market
- Network delays affect execution
- Different countries have different rules
- Insurance funds protect against bad debt
- Partial liquidations are common
- Maintenance margins change based on volatility


---