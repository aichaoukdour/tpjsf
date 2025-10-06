"""
Utility functions for data processing.
"""


def calculate_average(numbers):
    """
    Calculate the average of a list of numbers.
    
    Args:
        numbers: List of numeric values
        
    Returns:
        The arithmetic mean of the numbers
    """
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)


def merge_dictionaries(dict1, dict2):
    """
    Merge two dictionaries, with dict2 values taking precedence.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    result.update(dict2)
    return result


def filter_even_numbers(numbers):
    """
    Filter a list to keep only even numbers.
    
    Args:
        numbers: List of integers
        
    Returns:
        List containing only even numbers
    """
    return [n for n in numbers if n % 2 == 0]
