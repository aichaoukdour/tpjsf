"""
Mathematical operations and calculations.
"""

import math


def factorial(n: int) -> int:
    """
    Calculate the factorial of a number.
    
    Args:
        n: Non-negative integer
        
    Returns:
        The factorial of n
    """
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)


def is_prime(n: int) -> bool:
    """
    Check if a number is prime.
    
    Args:
        n: Integer to check
        
    Returns:
        True if n is prime, False otherwise
    """
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number.
    
    Args:
        n: Position in the Fibonacci sequence (0-indexed)
        
    Returns:
        The nth Fibonacci number
    """
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b


def gcd(a: int, b: int) -> int:
    """
    Calculate the greatest common divisor of two numbers.
    
    Args:
        a: First integer
        b: Second integer
        
    Returns:
        The GCD of a and b
    """
    while b:
        a, b = b, a % b
    return abs(a)
