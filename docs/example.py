"""
Example Python file to demonstrate code file support.
This file shows how the system can handle Python code with functions and classes.
"""

import os
from typing import List, Dict, Any

class ExampleClass:
    """An example class to demonstrate class detection."""
    
    def __init__(self, name: str):
        self.name = name
        self.data = []
    
    def add_item(self, item: Any) -> None:
        """Add an item to the data list."""
        self.data.append(item)
    
    def get_items(self) -> List[Any]:
        """Get all items from the data list."""
        return self.data.copy()

def example_function(param1: str, param2: int = 10) -> str:
    """
    An example function to demonstrate function detection.
    
    Args:
        param1: A string parameter
        param2: An integer parameter with default value
        
    Returns:
        A formatted string
    """
    return f"Function called with {param1} and {param2}"

def another_function():
    """Another example function."""
    return "Hello from another function!"

# Example usage
if __name__ == "__main__":
    obj = ExampleClass("test")
    obj.add_item("example")
    result = example_function("test", 42)
    print(result)
