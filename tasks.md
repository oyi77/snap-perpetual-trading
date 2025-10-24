Perpetual Futures Trading Simulator Assignment
Overview
As a senior engineer candidate for our team building a Perpetual DEX (Perp DEX), we
want to assess your ability to implement core trading logic, handle financial
calculations, manage data structures e?iciently, and design modular systems. This
assignment focuses on simulating key mechanics of a perpetual futures exchange
without requiring blockchain or smart contract experience. The skills demonstrated
here (e.g., order matching, risk management, position tracking) are directly transferable
to integrating with on-chain components later.
Time Estimate: 4-8 hours. Language: Use Python, Go, or JavaScript (your choice—
select based on your strengths). Submission: Provide a GitHub repo or ZIP file with the
code, a README.md explaining how to run it, any assumptions, and a brief design
rationale (1-2 paragraphs). Include unit tests. Evaluation Criteria:
• Correctness: Accurate implementation of trading mechanics and calculations.
• Code Quality: Clean, modular code with proper error handling, documentation,
and e?iciency (e.g., O(1) or O(log n) operations where possible).
• Senior-Level Thinking: Scalable design, handling edge cases (e.g., high
volatility, concurrent operations), and performance considerations.
• Testing: Comprehensive unit tests covering normal and edge scenarios.
• Creativity/Insight: Any optimizations or extensions that show deep
understanding of trading systems.
Assignment Details
Build a console-based simulator for a simplified perpetual futures exchange. Focus on
one asset pair: BTC/USD perpetual contract. Use mock price data to simulate market
movements. The simulator should handle order placement, matching, position
updates, funding rates, and liquidations.
Key Concepts to Implement
• Leverage: Users can trade with up to 10x leverage (e.g., 1 BTC collateral for a 10
BTC position).
• Mark Price: The current fair price used for PNL and margin calculations
(simulate with provided or generated data).
• Funding Rate: A periodic payment (every 8 simulated hours) between long and
short positions to keep the perpetual price close to spot. Simplify as:
funding_rate = (mark_price - index_price) / index_price * (1/8), applied to position
value.
• Margins: Initial margin = position_value / leverage; Maintenance margin = 5% of
position_value.
• PNL: Unrealized PNL = (current_mark - entry_price) * quantity * multiplier (for
longs; reverse for shorts).
• Liquidation: Trigger if account equity (collateral + unrealized PNL) <
maintenance margin requirement.
Requirements
1. Data Structures and Setup:

o Implement an Order Book using e?icient structures (e.g., priority
queues/heaps for price levels, maps for quick lookups). Support limit
orders only (buy/sell at specific prices).
o Track User Positions: For at least 2-3 simulated users, store position
details: side (long/short), quantity, entry price, leverage, collateral,
unrealized PNL.
o Price Oracle Simulation: Generate or load mock mark prices over time
(e.g., from a list or random walk model). Assume index_price =
mark_price for simplicity unless you want to extend.
§ Example: Start with BTC at $60,000, simulate hourly fluctuations
(±1-5%).
2. Core Features:
o Order Placement and Matching:
§ Allow placing limit buy/sell orders: e.g., buy 1 BTC at $59,500 with
5x leverage.
§ Match orders immediately if possible (cross the book). Support
partial fills.
§ Update positions on matches: Calculate entry price (average if
multiple fills), adjust collateral.

o Position Management:
§ Real-time unrealized PNL calculation based on current mark price.
§ Handle position closes: Placing an opposite order reduces the
position.

o Funding Rate Application:
§ Simulate time passage (e.g., in a loop). Every 8 "hours," calculate
and apply funding: Debit/credit users' collateral based on position
side and rate.
o Liquidation Engine:
§ Continuously monitor positions during price updates.
§ If equity < maintenance margin, liquidate: Close position at current
mark price, apply fees (e.g., 1% liquidation fee deducted from
collateral).
o Simulation Loop:
§ Run a main loop simulating 24-48 "hours" of trading.
§ Include random or scripted events: e.g., price spikes, user orders
at intervals.
§ Log key events: trades, PNL updates, fundings, liquidations.

3. Input/Output:

o Input: Use a scriptable interface (e.g., read from a JSON file or command-
line args) for initial setup: users' collateral, mock price series, and a

sequence of orders/events.
§ Sample Input JSON:

text
{
"users": [
{"id": "user1", "collateral": 10000}, // USD
{"id": "user2", "collateral": 5000}
],
"prices": [60000, 60500, 59000, ...], // Hourly mark prices
"events": [
{"time": 0, "action": "place_order", "user": "user1", "side": "buy", "quantity": 0.5,
"price": 59500, "leverage": 5},
{"time": 8, "action": "apply_funding"},
...
]
}

o Output: Console logs and a final report (JSON or text) showing:
§ Trade executions (e.g., "Matched: user1 buys 0.5 BTC at $59,500
from user2").
§ Position summaries over time.
§ Liquidation events.
§ End-of-simulation user balances.

4. Testing:
o Write at least 5-10 unit tests (using pytest, Go's testing, or Jest). Cover:
§ Order matching (full/partial, no match).
§ PNL calculations (profit/loss scenarios).
§ Funding applications (positive/negative rates).
§ Liquidation triggers (e.g., price drop liquidates over-leveraged
position).
§ Edge cases: Zero quantity, max leverage, concurrent orders (use
threads/async if in language).
5. Extensions (Optional, for Bonus Points):
o Add market orders or stop-loss.
o Simulate concurrency (multi-threaded order processing).
o Basic risk metrics (e.g., Value at Risk).
o Visualize price/PNL charts (using matplotlib in Python).

Resources
• No external dependencies beyond standard libraries (or listed in the overview if
using Python).
• Reference perp mechanics from public docs (e.g., dYdX or GMX whitepapers) for
formulas, but implement from scratch.
• If stuck on financial logic, prioritize correctness over completeness—note
assumptions in README.