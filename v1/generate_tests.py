import ast
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class FunctionAnalyzer(ast.NodeVisitor):
    """Analyzes Python AST to extract function information."""
    
    def __init__(self):
        self.functions = {}
        self.classes = {}
    
    def visit_FunctionDef(self, node):
        """Extract function information."""
        func_info = {
            "name": node.name,
            "args": [arg.arg for arg in node.args.args],
            "defaults": len(node.args.defaults),
            "docstring": ast.get_docstring(node) or "",
            "lineno": node.lineno,
            "is_method": False,
        }
        
        # Extract function body analysis
        func_info["has_error_handling"] = self._has_error_handling(node)
        func_info["body_analysis"] = self._analyze_body(node)
        
        self.functions[node.name] = func_info
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Extract class information."""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = {
                    "name": item.name,
                    "args": [arg.arg for arg in item.args.args],
                    "docstring": ast.get_docstring(item) or "",
                }
                methods.append(method_info)
        
        self.classes[node.name] = {
            "name": node.name,
            "docstring": ast.get_docstring(node) or "",
            "methods": methods,
            "lineno": node.lineno,
        }
        self.generic_visit(node)
    
    def _has_error_handling(self, node):
        """Check if function has error handling (try/except)."""
        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                return True
        return False
    
    def _analyze_body(self, node):
        """Analyze function body for patterns."""
        analysis = {
            "has_loops": False,
            "has_conditionals": False,
            "returns_bool": False,
            "raises_errors": False,
        }
        
        for child in ast.walk(node):
            if isinstance(child, (ast.For, ast.While)):
                analysis["has_loops"] = True
            if isinstance(child, (ast.If, ast.IfExp)):
                analysis["has_conditionals"] = True
            if isinstance(child, ast.Raise):
                analysis["raises_errors"] = True
        
        # Check return type from docstring
        if "bool" in node.body[-1].__class__.__name__.lower() if node.body else False:
            analysis["returns_bool"] = True
        
        return analysis


class TestCaseGenerator:
    """Generates test cases based on code analysis."""
    
    def __init__(self):
        self.test_cases = {
            "metadata": {
                "generated_tool": "Automated Test Case Generator",
                "version": "1.0",
            },
            "test_suites": []
        }
        self.test_suites = self.test_cases["test_suites"]
    
    def generate_tests_from_functions(self, functions: Dict) -> List[Dict]:
        """Generate test cases for functions."""
        test_suites = []
        
        for func_name, func_info in functions.items():
            # Skip private/magic methods
            if func_name.startswith('_'):
                continue
            
            test_suite = {
                "function": func_name,
                "docstring": func_info["docstring"],
                "arguments": func_info["args"],
                "test_cases": []
            }
            
            # Generate specific test cases based on function name and analysis
            test_suite["test_cases"] = self._generate_specific_tests(
                func_name, func_info
            )
            
            if test_suite["test_cases"]:
                test_suites.append(test_suite)
        
        return test_suites
    
    def _generate_specific_tests(self, func_name: str, func_info: Dict) -> List[Dict]:
        """Generate specific test cases based on function name and analysis."""
        tests = []
        func_name_lower = func_name.lower()
        args = func_info["args"]
        raises_errors = func_info["body_analysis"]["raises_errors"]
        
        # Arithmetic operations
        if "add" in func_name_lower and len(args) >= 2:
            tests.extend([
                {
                    "name": "Basic addition",
                    "inputs": {"a": 5, "b": 3},
                    "expected_output": 8,
                    "category": "normal"
                },
                {
                    "name": "Adding negative numbers",
                    "inputs": {"a": -5, "b": -3},
                    "expected_output": -8,
                    "category": "edge_case"
                },
                {
                    "name": "Adding zero",
                    "inputs": {"a": 0, "b": 5},
                    "expected_output": 5,
                    "category": "boundary"
                },
                {
                    "name": "Adding floats",
                    "inputs": {"a": 2.5, "b": 3.7},
                    "expected_output": 6.2,
                    "category": "normal"
                },
            ])
        
        elif "subtract" in func_name_lower and len(args) >= 2:
            tests.extend([
                {
                    "name": "Basic subtraction",
                    "inputs": {"a": 10, "b": 3},
                    "expected_output": 7,
                    "category": "normal"
                },
                {
                    "name": "Subtracting negative",
                    "inputs": {"a": 5, "b": -3},
                    "expected_output": 8,
                    "category": "edge_case"
                },
                {
                    "name": "Result in negative",
                    "inputs": {"a": 3, "b": 10},
                    "expected_output": -7,
                    "category": "edge_case"
                },
                {
                    "name": "Subtracting zero",
                    "inputs": {"a": 5, "b": 0},
                    "expected_output": 5,
                    "category": "boundary"
                },
            ])
        
        elif "multiply" in func_name_lower and len(args) >= 2:
            tests.extend([
                {
                    "name": "Basic multiplication",
                    "inputs": {"a": 4, "b": 5},
                    "expected_output": 20,
                    "category": "normal"
                },
                {
                    "name": "Multiply by zero",
                    "inputs": {"a": 5, "b": 0},
                    "expected_output": 0,
                    "category": "boundary"
                },
                {
                    "name": "Multiply negative numbers",
                    "inputs": {"a": -4, "b": -5},
                    "expected_output": 20,
                    "category": "edge_case"
                },
                {
                    "name": "Multiply positive and negative",
                    "inputs": {"a": 4, "b": -5},
                    "expected_output": -20,
                    "category": "edge_case"
                },
            ])
        
        elif "divide" in func_name_lower and len(args) >= 2:
            tests.extend([
                {
                    "name": "Basic division",
                    "inputs": {"a": 20, "b": 4},
                    "expected_output": 5,
                    "category": "normal"
                },
                {
                    "name": "Division resulting in float",
                    "inputs": {"a": 7, "b": 2},
                    "expected_output": 3.5,
                    "category": "normal"
                },
                {
                    "name": "Divide by zero (should raise error)",
                    "inputs": {"a": 5, "b": 0},
                    "expected_error": "ValueError",
                    "category": "error_case"
                },
                {
                    "name": "Negative division",
                    "inputs": {"a": -20, "b": 4},
                    "expected_output": -5,
                    "category": "edge_case"
                },
            ])
        
        elif "power" in func_name_lower and len(args) >= 2:
            tests.extend([
                {
                    "name": "Basic exponentiation",
                    "inputs": {"base": 2, "exponent": 3},
                    "expected_output": 8,
                    "category": "normal"
                },
                {
                    "name": "Power of zero",
                    "inputs": {"base": 5, "exponent": 0},
                    "expected_output": 1,
                    "category": "boundary"
                },
                {
                    "name": "Zero to power",
                    "inputs": {"base": 0, "exponent": 3},
                    "expected_output": 0,
                    "category": "boundary"
                },
                {
                    "name": "Negative exponent",
                    "inputs": {"base": 2, "exponent": -2},
                    "expected_output": 0.25,
                    "category": "edge_case"
                },
            ])
        
        elif "modulo" in func_name_lower and len(args) >= 2:
            tests.extend([
                {
                    "name": "Basic modulo",
                    "inputs": {"a": 10, "b": 3},
                    "expected_output": 1,
                    "category": "normal"
                },
                {
                    "name": "Modulo by zero (should raise error)",
                    "inputs": {"a": 5, "b": 0},
                    "expected_error": "ValueError",
                    "category": "error_case"
                },
                {
                    "name": "Even division",
                    "inputs": {"a": 10, "b": 5},
                    "expected_output": 0,
                    "category": "boundary"
                },
            ])
        
        elif "average" in func_name_lower or "mean" in func_name_lower:
            tests.extend([
                {
                    "name": "Average of positive numbers",
                    "inputs": {"numbers": [1, 2, 3, 4, 5]},
                    "expected_output": 3,
                    "category": "normal"
                },
                {
                    "name": "Average with single element",
                    "inputs": {"numbers": [5]},
                    "expected_output": 5,
                    "category": "boundary"
                },
                {
                    "name": "Average with negative numbers",
                    "inputs": {"numbers": [-5, -3, -1]},
                    "expected_output": -3,
                    "category": "edge_case"
                },
                {
                    "name": "Empty list (should raise error)",
                    "inputs": {"numbers": []},
                    "expected_error": "ValueError",
                    "category": "error_case"
                },
            ])
        
        elif "factorial" in func_name_lower:
            tests.extend([
                {
                    "name": "Factorial of 5",
                    "inputs": {"n": 5},
                    "expected_output": 120,
                    "category": "normal"
                },
                {
                    "name": "Factorial of 0",
                    "inputs": {"n": 0},
                    "expected_output": 1,
                    "category": "boundary"
                },
                {
                    "name": "Factorial of 1",
                    "inputs": {"n": 1},
                    "expected_output": 1,
                    "category": "boundary"
                },
                {
                    "name": "Negative factorial (should raise error)",
                    "inputs": {"n": -5},
                    "expected_error": "ValueError",
                    "category": "error_case"
                },
                {
                    "name": "Non-integer input (should raise error)",
                    "inputs": {"n": 5.5},
                    "expected_error": "TypeError",
                    "category": "error_case"
                },
            ])
        
        elif "prime" in func_name_lower or "is_prime" in func_name_lower:
            tests.extend([
                {
                    "name": "Prime number",
                    "inputs": {"n": 7},
                    "expected_output": True,
                    "category": "normal"
                },
                {
                    "name": "Non-prime number",
                    "inputs": {"n": 4},
                    "expected_output": False,
                    "category": "normal"
                },
                {
                    "name": "Number 2 (smallest prime)",
                    "inputs": {"n": 2},
                    "expected_output": True,
                    "category": "boundary"
                },
                {
                    "name": "Number 1 (not prime)",
                    "inputs": {"n": 1},
                    "expected_output": False,
                    "category": "boundary"
                },
                {
                    "name": "Negative number",
                    "inputs": {"n": -5},
                    "expected_output": False,
                    "category": "edge_case"
                },
                {
                    "name": "Zero",
                    "inputs": {"n": 0},
                    "expected_output": False,
                    "category": "boundary"
                },
            ])
        
        # Generic tests if no specific pattern matched
        if not tests and len(args) > 0:
            tests.append({
                "name": "Generic test case",
                "inputs": {},
                "note": "Add specific test inputs based on function purpose",
                "category": "placeholder"
            })
        
        return tests
    
    def generate_tests_from_classes(self, classes: Dict) -> List[Dict]:
        """Generate test cases for classes."""
        test_suites = []
        
        for class_name, class_info in classes.items():
            test_suite = {
                "class": class_name,
                "docstring": class_info["docstring"],
                "methods": []
            }
            
            for method in class_info["methods"]:
                if method["name"] != "__init__":
                    method_tests = {
                        "method": method["name"],
                        "docstring": method["docstring"],
                        "test_cases": [
                            {
                                "name": f"Test {method['name']}",
                                "setup": f"Create instance of {class_name}",
                                "action": f"Call {method['name']}",
                                "expected": "Verify behavior",
                                "category": "placeholder"
                            }
                        ]
                    }
                    test_suite["methods"].append(method_tests)
            
            if test_suite["methods"]:
                test_suites.append(test_suite)
        
        return test_suites


class ProjectAnalyzer:
    """Main class to analyze a Python project and generate test cases."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.analyzer = FunctionAnalyzer()
        self.test_generator = TestCaseGenerator()
    
    def analyze_project(self) -> Dict[str, Any]:
        """Analyze all Python files in the project."""
        python_files = list(self.project_path.glob("**/*.py"))
        
        # Filter out test files and __pycache__
        python_files = [
            f for f in python_files
            if not f.name.startswith("test_")
            and "__pycache__" not in f.parts
            and "generate_tests.py" not in f.name
        ]
        
        if not python_files:
            print(f"No Python files found in {self.project_path}")
            return {"error": "No Python files found"}
        
        print(f"Found {len(python_files)} Python files")
        
        for py_file in python_files:
            print(f"Analyzing: {py_file.relative_to(self.project_path)}")
            self._analyze_file(py_file)
        
        # Generate test cases
        self.test_generator.test_suites.extend(
            self.test_generator.generate_tests_from_functions(self.analyzer.functions)
        )
        self.test_generator.test_suites.extend(
            self.test_generator.generate_tests_from_classes(self.analyzer.classes)
        )
        
        return self.test_generator.test_cases
    
    def _analyze_file(self, file_path: Path):
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            self.analyzer.visit(tree)
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def save_test_cases(self, output_file: str):
        """Save generated test cases to JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_generator.test_cases, f, indent=2)
        print(f"Test cases saved to: {output_file}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python generate_tests.py <project_path> [output_file]")
        print("Example: python generate_tests.py . generated_tests.json")
        sys.exit(1)
    
    project_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "generated_tests.json"
    
    if not os.path.isdir(project_path):
        print(f"Error: Directory '{project_path}' not found")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print("Automated Test Case Generator")
    print(f"{'='*60}\n")
    print(f"Project Path: {project_path}")
    print(f"Output File: {output_file}\n")
    
    # Analyze project
    analyzer = ProjectAnalyzer(project_path)
    result = analyzer.analyze_project()
    
    if "error" not in result:
        # Save test cases
        analyzer.save_test_cases(output_file)
        
        # Print summary
        print(f"\n{'='*60}")
        print("Test Case Generation Summary")
        print(f"{'='*60}")
        print(f"Total test suites: {len(analyzer.test_generator.test_suites)}")
        
        total_tests = sum(
            len(suite.get("test_cases", []))
            for suite in analyzer.test_generator.test_suites
        )
        print(f"Total test cases: {total_tests}")
        print(f"\nGenerated test cases successfully saved!\n")
    else:
        print(f"Error: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
