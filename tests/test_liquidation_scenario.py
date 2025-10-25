#!/usr/bin/env python3
"""
Test script to demonstrate liquidation events in the perpetual futures simulator.
This creates a scenario where liquidations actually occur.
"""

import sys
import os
import json
from decimal import Decimal
from datetime import datetime

# Add project root to path (go up one level from tests folder)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.simulator import TradingSimulator

def create_liquidation_test_config():
    """Create a configuration that will trigger liquidations."""
    config = {
        "hours": 8,
        "users": [
            {"id": "user1", "collateral": 10000},  # High collateral user
            {"id": "user2", "collateral": 10000},  # Medium collateral user - will get liquidated
            {"id": "user3", "collateral": 8000}     # Medium collateral user - will get liquidated
        ],
        "initial_price": 50000,
        "prices": [50000, 48000, 46000, 42000, 40000, 38000, 36000, 35000],
        "events": [
            # Hour 0: Place high leverage orders that will get liquidated
            {
                "time": 0,
                "action": "place_order",
                "data": {
                    "user": "user2",
                    "side": "buy",
                    "quantity": 2.0,  # $100,000 position
                    "price": 50000,
                    "leverage": 10  # Requires $10,000 collateral (user has $10,000)
                }
            },
            {
                "time": 0,
                "action": "place_order", 
                "data": {
                    "user": "user3",
                    "side": "sell",
                    "quantity": 1.6,  # $80,000 position
                    "price": 50000,
                    "leverage": 10   # Requires $8,000 collateral (user has $8,000)
                }
            },
            # Hour 1: Place a safe order for user1
            {
                "time": 1,
                "action": "place_order",
                "data": {
                    "user": "user1",
                    "side": "buy",
                    "quantity": 0.2,
                    "price": 50000,
                    "leverage": 2  # Safe leverage
                }
            },
            # Hour 2: Price starts dropping (triggers liquidations)
            {
                "time": 2,
                "action": "price_update",
                "data": {"price": 48000}  # 4% drop
            },
            # Hour 3: More price drop
            {
                "time": 3,
                "action": "price_update", 
                "data": {"price": 46000}  # 8% drop total
            },
            # Hour 4: Big drop - should trigger liquidations
            {
                "time": 4,
                "action": "price_update",
                "data": {"price": 42000}  # 16% drop - liquidation territory
            },
            # Hour 5: Apply funding (to show funding works)
            {
                "time": 5,
                "action": "apply_funding"
            },
            # Hour 6: More price movement
            {
                "time": 6,
                "action": "price_update",
                "data": {"price": 40000}  # 20% drop
            },
            # Hour 7: Another big drop
            {
                "time": 7,
                "action": "price_update",
                "data": {"price": 38000}  # 24% drop
            },
            # Hour 8: Final drop - should definitely trigger liquidations
            {
                "time": 8,
                "action": "price_update",
                "data": {"price": 36000}  # 28% drop
            }
        ]
    }
    return config

def run_liquidation_test():
    """Run the liquidation test scenario."""
    print("🔥 LIQUIDATION TEST SCENARIO")
    print("=" * 50)
    print("This test creates a scenario where liquidations actually occur.")
    print("We'll use high leverage positions and significant price drops.")
    print()
    
    # Create test configuration
    config = create_liquidation_test_config()
    
    # Save config for reference
    config_path = os.path.join(os.path.dirname(__file__), 'liquidation_test_config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print("📋 Test configuration saved to: tests/liquidation_test_config.json")
    
    # Run simulation
    print("\n🚀 Starting liquidation test simulation...")
    simulator = TradingSimulator()
    
    # Load the configuration first
    config_path = os.path.join(os.path.dirname(__file__), 'liquidation_test_config.json')
    config_result = simulator.load_simulation_config(config_path)
    if not config_result["success"]:
        print(f"❌ Error loading config: {config_result['message']}")
        return None
    
    # Run simulation for the configured hours
    results = simulator.run_simulation(config['hours'])
    
    # Display results
    print("\n📊 SIMULATION RESULTS:")
    print("=" * 30)
    
    summary = results['simulation_summary']
    print(f"Duration: {summary['total_hours']} hours")
    print(f"Final Price: ${summary['final_price']:,.2f}")
    print(f"Price Change: {summary['price_change_percent']:.2f}%")
    print(f"Total Trades: {summary['total_trades']}")
    print(f"Total Volume: ${summary['total_volume']:,.2f}")
    print(f"Total Liquidations: {summary['total_liquidations']}")
    print(f"Total Funding Paid: ${summary['total_funding_paid']:,.2f}")
    
    # Show liquidation details
    liquidation_stats = results['liquidation_statistics']
    if liquidation_stats['total_liquidations'] > 0:
        print(f"\n💥 LIQUIDATION DETAILS:")
        print(f"Total Liquidations: {liquidation_stats['total_liquidations']}")
        print(f"Total Liquidation Fees: ${liquidation_stats['total_liquidation_fees']:,.2f}")
        print(f"Total Collateral Lost: ${liquidation_stats['total_collateral_lost']:,.2f}")
        print(f"Average Liquidation Size: ${liquidation_stats['average_liquidation_size']:,.2f}")
        
        # Show liquidation events
        if 'liquidation_events' in results:
            print(f"\n📋 LIQUIDATION EVENTS:")
            for i, event in enumerate(results['liquidation_events'], 1):
                print(f"  {i}. Hour {event['hour']}: {event['user_id']} liquidated")
                print(f"     Position: {event['position_side']} {event['quantity']} BTC")
                print(f"     Entry Price: ${event['entry_price']:,.2f}")
                print(f"     Liquidation Price: ${event['liquidation_price']:,.2f}")
                print(f"     Fee: ${event['fee']:,.2f}")
                print(f"     Collateral Lost: ${event['collateral_lost']:,.2f}")
                print()
    else:
        print("\n❌ No liquidations occurred!")
        print("The price drop wasn't severe enough to trigger liquidations.")
        print("Try increasing leverage or making the price drop more severe.")
    
    # Show final user balances
    print(f"\n👥 FINAL USER BALANCES:")
    for user_id, balance in results['final_user_balances'].items():
        status = "LIQUIDATED" if balance['collateral'] < 100 else "ACTIVE"
        print(f"  {user_id}: ${balance['collateral']:,.2f} ({status})")
    
    # Save results (avoid circular references)
    try:
        # Create a simplified results dict without circular references
        simplified_results = {
            'simulation_summary': results['simulation_summary'],
            'liquidation_statistics': results['liquidation_statistics'],
            'final_user_balances': results['final_user_balances']
        }
        
        results_path = os.path.join(os.path.dirname(__file__), 'liquidation_test_results.json')
        with open(results_path, 'w') as f:
            json.dump(simplified_results, f, indent=2, default=str)
        print(f"\n💾 Results saved to: tests/liquidation_test_results.json")
    except Exception as e:
        print(f"\n⚠️  Could not save results: {e}")
    
    return results

if __name__ == "__main__":
    try:
        results = run_liquidation_test()
        
        # Check if liquidations occurred
        if results['simulation_summary']['total_liquidations'] > 0:
            print("\n✅ SUCCESS: Liquidations were triggered!")
            print("The simulator correctly handles liquidation events.")
        else:
            print("\n⚠️  WARNING: No liquidations occurred.")
            print("The test scenario needs adjustment to trigger liquidations.")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
