def add(a, b):
    """
    Add two numbers.
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        Sum of a and b
    """
    return a + b


def subtract(a, b):
    """
    Subtract two numbers.
    
    Args:
        a: First number
        b: Second number (subtracted from a)
    
    Returns:
        Difference of a and b
    """
    return a - b


def multiply(a, b):
    """
    Multiply two numbers.
    
    Args:
        a: First number
        b: Second number
    
    Returns:
        Product of a and b
    """
    return a * b


def divide(a, b):
    """
    Divide two numbers.
    
    Args:
        a: Dividend
        b: Divisor
    
    Returns:
        Result of a divided by b
    
    Raises:
        ValueError: If b is zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def power(base, exponent):
    """
    Raise base to the power of exponent.
    
    Args:
        base: Base number
        exponent: Power
    
    Returns:
        base raised to exponent
    """
    return base ** exponent


def modulo(a, b):
    """
    Get remainder of division.
    
    Args:
        a: Dividend
        b: Divisor
    
    Returns:
        Remainder of a divided by b
    
    Raises:
        ValueError: If b is zero
    """
    if b == 0:
        raise ValueError("Cannot perform modulo by zero")
    return a % b


def calculate_average(numbers):
    """
    Calculate average of a list of numbers.
    
    Args:
        numbers: List of numbers
    
    Returns:
        Average of the numbers
    
    Raises:
        ValueError: If list is empty
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)


def factorial(n):
    """
    Calculate factorial of n.
    
    Args:
        n: Non-negative integer
    
    Returns:
        Factorial of n
    
    Raises:
        ValueError: If n is negative
        TypeError: If n is not an integer
    """
    if not isinstance(n, int):
        raise TypeError("Factorial requires an integer")
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)


def is_prime(n):
    """
    Check if a number is prime.
    
    Args:
        n: Integer to check
    
    Returns:
        True if n is prime, False otherwise
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


class Calculator:
    """A calculator class with history tracking."""
    
    def __init__(self):
        """Initialize calculator with empty history."""
        self.history = []
        self.result = 0
    
    def add_to_history(self, operation, operands, result):
        """
        Add operation to history.
        
        Args:
            operation: Operation name
            operands: List of operands
            result: Result of operation
        """
        self.history.append({
            "operation": operation,
            "operands": operands,
            "result": result
        })
    
    def get_history(self):
        """Return the operation history."""
        return self.history
    
    def clear_history(self):
        """Clear the operation history."""
        self.history = []
