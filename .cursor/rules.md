---
description: Python project optimization and consistency rules for perpetual futures trading simulator
globs: ["**/*.py", "**/*.md", "**/*.json", "**/*.txt"]
alwaysApply: true
---

# Perpetual Futures Trading Simulator - Cursor Rules

## Code Quality Standards

### Python Code Style
- Use absolute imports instead of relative imports
- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Use dataclasses for immutable data structures
- Prefer Decimal over float for financial calculations
- Use meaningful variable and function names

### Financial Calculations
- Always use Decimal for monetary values and calculations
- Implement proper rounding for financial operations
- Validate input parameters (quantities > 0, prices > 0, leverage 1-10)
- Handle edge cases (zero quantities, maximum leverage, liquidation scenarios)

### Architecture Principles
- Follow SOLID principles (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion)
- Apply DRY (Don't Repeat Yourself) principle
- Use dependency injection for better testability
- Implement proper error handling and validation

## Project Structure

### Module Organization
- Keep models in `src/models/` directory
- Keep engine components in `src/engine/` directory
- Keep tests in `tests/` directory with matching structure
- Use `__init__.py` files for proper package structure

### File Naming
- Use snake_case for Python files
- Use descriptive names that indicate purpose
- Group related functionality in same modules

## Testing Requirements

### Test Coverage
- Write unit tests for all public methods
- Test edge cases and error conditions
- Test integration between components
- Use pytest for testing framework
- Aim for >90% code coverage

### Test Structure
- One test file per module
- Use descriptive test method names
- Group related tests in classes
- Use fixtures for common test data

## Documentation Standards

### Code Documentation
- Write docstrings for all public classes and methods
- Use Google-style docstrings
- Include parameter and return type information
- Document complex algorithms and business logic

### README Requirements
- Include installation instructions
- Provide usage examples
- Document configuration options
- Explain architecture and design decisions
- Include performance characteristics

## Performance Guidelines

### Efficiency Requirements
- Use O(log n) operations for order book operations
- Minimize memory allocations in hot paths
- Use appropriate data structures (heaps for priority queues)
- Avoid unnecessary object creation

### Scalability Considerations
- Design for concurrent operations
- Consider memory usage with large datasets
- Implement efficient data structures
- Plan for horizontal scaling

## Error Handling

### Validation Rules
- Validate all user inputs
- Check business rule constraints
- Handle edge cases gracefully
- Provide meaningful error messages

### Exception Handling
- Use specific exception types
- Don't catch generic exceptions unless necessary
- Log errors appropriately
- Fail fast on invalid inputs

## Security Considerations

### Input Validation
- Sanitize all user inputs
- Validate JSON configuration files
- Check file permissions for output files
- Prevent injection attacks

### Data Protection
- Don't log sensitive information
- Use secure random number generation
- Validate file paths to prevent directory traversal

## Maintenance Guidelines

### Code Reviews
- Review all changes for correctness
- Check for performance implications
- Verify test coverage
- Ensure documentation is updated

### Refactoring
- Refactor when code becomes complex
- Extract common functionality
- Improve readability and maintainability
- Update tests after refactoring

## Deployment Considerations

### Dependencies
- Pin dependency versions
- Use virtual environments
- Document all external dependencies
- Keep requirements.txt updated

### Configuration
- Use environment variables for sensitive data
- Provide default configurations
- Validate configuration on startup
- Support multiple deployment environments

## Monitoring and Logging

### Logging Standards
- Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
- Include relevant context in log messages
- Don't log sensitive information
- Use structured logging when possible

### Performance Monitoring
- Log execution times for critical operations
- Monitor memory usage
- Track error rates
- Measure throughput metrics

## Future Extensibility

### Design for Extension
- Use interfaces for major components
- Implement plugin architecture where appropriate
- Design APIs for external integrations
- Plan for additional asset types

### Version Compatibility
- Maintain backward compatibility
- Version APIs appropriately
- Document breaking changes
- Provide migration guides

## Code Examples

### Good Practices
```python
from decimal import Decimal
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class Order:
    """Represents a trading order."""
    user_id: str
    side: OrderSide
    quantity: Decimal
    price: Decimal
    leverage: int = 1
    
    def validate(self) -> bool:
        """Validate order parameters."""
        return (
            self.quantity > Decimal('0') and
            self.price > Decimal('0') and
            1 <= self.leverage <= 10
        )
```

### Avoid These Patterns
```python
# Don't use relative imports
from .models import Order

# Don't use float for financial calculations
price = 60000.0

# Don't skip validation
def process_order(order):
    # Missing validation
    return order_book.add_order(order)
```

## Continuous Improvement

### Regular Reviews
- Review and update these rules quarterly
- Incorporate lessons learned from production
- Update based on new requirements
- Share knowledge across team

### Metrics and KPIs
- Track code quality metrics
- Monitor performance benchmarks
- Measure test coverage
- Assess maintainability scores
