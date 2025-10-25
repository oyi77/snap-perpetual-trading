#!/usr/bin/env python3
"""
Simple liquidation test to verify liquidation logic works.
"""

import sys
import os
from decimal import Decimal

# Add project root to path (go up one level from tests folder)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.data_models import Position, PositionSide, User

def test_liquidation_logic():
    """Test the liquidation logic directly."""
    print("🧪 TESTING LIQUIDATION LOGIC")
    print("=" * 40)
    
    # Create a user with low collateral
    user = User("test_user", Decimal('1000'))  # $1000 collateral
    
    # Create a high leverage long position
    position = Position(
        user_id="test_user",
        side=PositionSide.LONG,
        quantity=Decimal('1.0'),  # 1 BTC
        entry_price=Decimal('50000'),  # Entry at $50k
        leverage=10,  # 10x leverage
        collateral=Decimal('5000')  # $5000 collateral required
    )
    
    print(f"Initial position:")
    print(f"  Quantity: {position.quantity} BTC")
    print(f"  Entry Price: ${position.entry_price}")
    print(f"  Leverage: {position.leverage}x")
    print(f"  Collateral: ${position.collateral}")
    print(f"  Position Value: ${position.position_value}")
    print(f"  Maintenance Margin: ${position.maintenance_margin}")
    print(f"  Equity: ${position.equity}")
    print(f"  Is Liquidatable: {position.is_liquidatable}")
    
    # Simulate price drop to $40k (20% drop)
    print(f"\n📉 Simulating price drop to $40,000 (20% drop)...")
    position.unrealized_pnl = (Decimal('40000') - position.entry_price) * position.quantity
    
    print(f"After price drop:")
    print(f"  Unrealized PNL: ${position.unrealized_pnl}")
    print(f"  Equity: ${position.equity}")
    print(f"  Maintenance Margin: ${position.maintenance_margin}")
    print(f"  Is Liquidatable: {position.is_liquidatable}")
    
    # Simulate bigger price drop to $35k (30% drop)
    print(f"\n📉 Simulating bigger price drop to $35,000 (30% drop)...")
    position.unrealized_pnl = (Decimal('35000') - position.entry_price) * position.quantity
    
    print(f"After bigger price drop:")
    print(f"  Unrealized PNL: ${position.unrealized_pnl}")
    print(f"  Equity: ${position.equity}")
    print(f"  Maintenance Margin: ${position.maintenance_margin}")
    print(f"  Is Liquidatable: {position.is_liquidatable}")
    
    # Test short position
    print(f"\n📈 Testing SHORT position liquidation...")
    short_position = Position(
        user_id="test_user",
        side=PositionSide.SHORT,
        quantity=Decimal('1.0'),  # 1 BTC
        entry_price=Decimal('50000'),  # Entry at $50k
        leverage=10,  # 10x leverage
        collateral=Decimal('5000')  # $5000 collateral required
    )
    
    # Simulate price increase to $60k (20% increase)
    short_position.unrealized_pnl = (short_position.entry_price - Decimal('60000')) * short_position.quantity
    
    print(f"Short position after price increase to $60k:")
    print(f"  Unrealized PNL: ${short_position.unrealized_pnl}")
    print(f"  Equity: ${short_position.equity}")
    print(f"  Maintenance Margin: ${short_position.maintenance_margin}")
    print(f"  Is Liquidatable: {short_position.is_liquidatable}")

if __name__ == "__main__":
    test_liquidation_logic()
