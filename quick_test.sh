#!/bin/bash
# Simple test runner for quick testing

echo "🚀 Running Quick Tests..."

# Run basic functionality test
echo "Testing basic functionality..."
python tests/test_simulator.py

# Run short simulation
echo "Running 6-hour simulation..."
python main.py --config configs/sample_config.json --hours 6 --output tests/quick_test_results.json

# Analyze results
echo "Analyzing results..."
python tests/analyze_results.py

echo "✅ Quick tests completed!"
