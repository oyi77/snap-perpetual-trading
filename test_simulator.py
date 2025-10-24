#!/usr/bin/env python3
"""
Quick test script to verify the perpetual futures trading simulator works correctly.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.simulator import TradingSimulator
from src.engine.price_oracle import PriceDataGenerator
from decimal import Decimal
import json
import tempfile

def test_basic_functionality():
    """Test basic simulator functionality."""
    print("Testing Perpetual Futures Trading Simulator...")
    
    # Create simulator
    simulator = TradingSimulator()
    
    # Create sample configuration
    config = {
        "users": [
            {"id": "user1", "collateral": 10000},
            {"id": "user2", "collateral": 5000}
        ],
        "prices": [60000, 61000, 59000, 58000, 57000],
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
                "time": 1,
                "action": "place_order",
                "data": {
                    "user": "user2",
                    "side": "sell",
                    "quantity": 0.3,
                    "price": 60500,
                    "leverage": 3
                }
            }
        ]
    }
    
    # Save config to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        config_file = f.name
    
    try:
        # Load configuration
        result = simulator.load_simulation_config(config_file)
        if not result["success"]:
            print(f"❌ Failed to load config: {result['message']}")
            return False
        
        print("✅ Configuration loaded successfully")
        
        # Run short simulation
        results = simulator.run_simulation(5)
        
        if "simulation_summary" not in results:
            print("❌ Simulation failed to generate results")
            return False
        
        print("✅ Simulation completed successfully")
        
        # Check key results
        summary = results["simulation_summary"]
        print(f"   - Final Price: ${summary['final_price']:,.2f}")
        print(f"   - Total Trades: {summary['total_trades']}")
        print(f"   - Total Volume: ${summary['total_volume']:,.2f}")
        
        # Check user balances
        balances = results["final_user_balances"]
        print(f"   - Users: {len(balances)}")
        
        for user_id, balance in balances.items():
            print(f"     {user_id}: ${balance['total_equity']:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False
    finally:
        # Clean up
        os.unlink(config_file)

def test_price_generation():
    """Test price generation functionality."""
    print("\nTesting price generation...")
    
    try:
        # Test different price scenarios
        scenarios = [
            ("Volatile", PriceDataGenerator.generate_volatile_prices),
            ("Crash", PriceDataGenerator.generate_crash_scenario),
            ("Pump", PriceDataGenerator.generate_pump_scenario)
        ]
        
        for name, generator in scenarios:
            prices = generator(Decimal('60000'), 10)
            print(f"✅ {name} scenario: {len(prices)} prices generated")
            print(f"   Price range: ${min(prices):,.0f} - ${max(prices):,.0f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Price generation test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("PERPETUAL FUTURES TRADING SIMULATOR - QUICK TEST")
    print("=" * 60)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Price Generation", test_price_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The simulator is working correctly.")
        print("\nTo run a full simulation:")
        print("  python main.py --config configs/sample_config.json --hours 24")
        print("\nTo run tests:")
        print("  pytest tests/ -v")
    else:
        print("❌ Some tests failed. Please check the implementation.")
        sys.exit(1)

if __name__ == "__main__":
    main()
