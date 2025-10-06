"""
String manipulation utilities.
"""


def reverse_string(text: str) -> str:
    """
    Reverse a string.
    
    Args:
        text: The string to reverse
        
    Returns:
        The reversed string
    """
    return text[::-1]


def count_vowels(text: str) -> int:
    """
    Count the number of vowels in a string.
    
    Args:
        text: The input string
        
    Returns:
        Number of vowels (a, e, i, o, u)
    """
    vowels = "aeiouAEIOU"
    count = 0
    for char in text:
        if char in vowels:
            count += 1
    return count


def capitalize_words(sentence: str) -> str:
    """
    Capitalize the first letter of each word in a sentence.
    
    Args:
        sentence: The input sentence
        
    Returns:
        Sentence with capitalized words
    """
    words = sentence.split()
    capitalized = [word.capitalize() for word in words]
    return " ".join(capitalized)


def is_palindrome(text: str) -> bool:
    """
    Check if a string is a palindrome.
    
    Args:
        text: The string to check
        
    Returns:
        True if palindrome, False otherwise
    """
    cleaned = ''.join(c.lower() for c in text if c.isalnum())
    return cleaned == cleaned[::-1]
