#!/usr/bin/env python3
"""Debug script to check trade data structure."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from src.simulator import TradingSimulator
from src.engine.price_oracle import PriceDataGenerator

# Run a short simulation
# Get the project root directory (parent of tests)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logs_dir = os.path.join(project_root, "logs")

# Create simulator with correct logs directory
simulator = TradingSimulator(logs_dir)
simulator.add_random_events(5)
results = simulator.run_simulation(2)

print("=== SIMULATION LOG DEBUG ===")
print(f"Total log entries: {len(results['simulation_log'])}")

for i, log_entry in enumerate(results['simulation_log'][:10]):  # Check first 10 entries
    print(f"\nEntry {i}:")
    print(f"  Event type: {log_entry.get('event_type', 'N/A')}")
    print(f"  Hour: {log_entry.get('hour', 'N/A')}")
    
    if 'data' in log_entry:
        data = log_entry['data']
        print(f"  Data keys: {list(data.keys())}")
        
        if 'result' in data:
            result = data['result']
            print(f"  Result keys: {list(result.keys())}")
            if 'trades' in result:
                print(f"  Trades: {result['trades']}")
            else:
                print(f"  No 'trades' key in result")
        else:
            print(f"  No 'result' key in data")

print("\n=== TRADE EXTRACTION TEST ===")
from main import ResultsExporter
trades = ResultsExporter._extract_trade_history(results)
print(f"Extracted trades: {len(trades)}")
if trades:
    print(f"First trade: {trades[0]}")
