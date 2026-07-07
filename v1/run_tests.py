"""
Example: Using Generated Test Cases

This script demonstrates how to read and execute the generated test cases
from the JSON file and run them against the actual calculator functions.
"""

import json
import sys
from pathlib import Path
from calculator import (
    add, subtract, multiply, divide, power, modulo,
    calculate_average, factorial, is_prime
)


class TestRunner:
    """Execute generated test cases against actual functions."""
    
    def __init__(self, json_file: str):
        self.json_file = json_file
        self.test_data = None
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "total": 0,
            "failures": []
        }
        self.function_map = {
            "add": add,
            "subtract": subtract,
            "multiply": multiply,
            "divide": divide,
            "power": power,
            "modulo": modulo,
            "calculate_average": calculate_average,
            "factorial": factorial,
            "is_prime": is_prime,
        }
    
    def load_test_cases(self) -> bool:
        """Load test cases from JSON file."""
        try:
            with open(self.json_file, 'r') as f:
                self.test_data = json.load(f)
            print(f"✓ Loaded test cases from {self.json_file}")
            return True
        except FileNotFoundError:
            print(f"✗ Test file not found: {self.json_file}")
            return False
        except json.JSONDecodeError:
            print(f"✗ Invalid JSON in {self.json_file}")
            return False
    
    def run_tests(self) -> bool:
        """Execute all test cases."""
        if not self.test_data:
            return False
        
        print("\n" + "="*70)
        print("Running Generated Test Cases")
        print("="*70 + "\n")
        
        for test_suite in self.test_data.get("test_suites", []):
            func_name = test_suite.get("function")
            test_cases = test_suite.get("test_cases", [])
            
            if func_name not in self.function_map:
                print(f"⚠ Function '{func_name}' not found in function_map")
                continue
            
            print(f"\n📋 Testing: {func_name}")
            print("-" * 70)
            
            func = self.function_map[func_name]
            
            for test_case in test_cases:
                self.results["total"] += 1
                test_name = test_case.get("name", "Unnamed test")
                inputs = test_case.get("inputs", {})
                expected_output = test_case.get("expected_output")
                expected_error = test_case.get("expected_error")
                category = test_case.get("category", "unknown")
                
                try:
                    # Call the function with the provided inputs
                    result = func(**inputs)
                    
                    if expected_error:
                        # Test was supposed to raise an error but didn't
                        self.results["failed"] += 1
                        self.results["failures"].append({
                            "function": func_name,
                            "test": test_name,
                            "reason": f"Expected {expected_error} but got result: {result}"
                        })
                        print(f"  ✗ {test_name} [{category}]")
                        print(f"    → Expected error: {expected_error}, Got: {result}")
                    elif expected_output is not None:
                        # Check if result matches expected output
                        # Use approximate comparison for floats
                        if isinstance(result, float) and isinstance(expected_output, float):
                            match = abs(result - expected_output) < 1e-9
                        else:
                            match = result == expected_output
                        
                        if match:
                            self.results["passed"] += 1
                            print(f"  ✓ {test_name} [{category}]")
                        else:
                            self.results["failed"] += 1
                            self.results["failures"].append({
                                "function": func_name,
                                "test": test_name,
                                "reason": f"Expected {expected_output}, got {result}"
                            })
                            print(f"  ✗ {test_name} [{category}]")
                            print(f"    → Expected: {expected_output}, Got: {result}")
                    else:
                        # No expected output specified
                        self.results["passed"] += 1
                        print(f"  ✓ {test_name} [{category}]")
                
                except Exception as e:
                    error_type = type(e).__name__
                    
                    if expected_error and error_type == expected_error:
                        self.results["passed"] += 1
                        print(f"  ✓ {test_name} [{category}] (raised {error_type})")
                    else:
                        self.results["errors"] += 1
                        reason = f"Unexpected {error_type}: {str(e)}"
                        if expected_error:
                            reason = f"Expected {expected_error}, got {error_type}: {str(e)}"
                        self.results["failures"].append({
                            "function": func_name,
                            "test": test_name,
                            "reason": reason
                        })
                        print(f"  ✗ {test_name} [{category}]")
                        print(f"    → Error: {error_type}: {str(e)}")
        
        return True
    
    def print_summary(self):
        """Print test execution summary."""
        print("\n" + "="*70)
        print("Test Summary")
        print("="*70)
        print(f"Total Tests:  {self.results['total']}")
        print(f"Passed:       {self.results['passed']} ✓")
        print(f"Failed:       {self.results['failed']} ✗")
        print(f"Errors:       {self.results['errors']} ⚠")
        
        if self.results['failures']:
            print("\n" + "-"*70)
            print("Failures:")
            print("-"*70)
            for failure in self.results['failures']:
                print(f"\n{failure['function']} - {failure['test']}")
                print(f"  Reason: {failure['reason']}")
        
        success_rate = (self.results['passed'] / self.results['total'] * 100) if self.results['total'] > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        print("="*70 + "\n")
        
        return self.results['failed'] == 0 and self.results['errors'] == 0


def main():
    """Main entry point."""
    json_file = "generated_tests.json"
    
    # Check if custom file provided
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    
    print("Automated Test Case Runner")
    print("="*70)
    
    runner = TestRunner(json_file)
    
    if not runner.load_test_cases():
        sys.exit(1)
    
    if runner.run_tests():
        success = runner.print_summary()
        sys.exit(0 if success else 1)
    else:
        print("Failed to run tests")
        sys.exit(1)


if __name__ == "__main__":
    main()
