# Automated Test Case Generator

A sophisticated Python tool that analyzes entire project codebases and automatically generates meaningful test cases in JSON format.

## Overview

This tool reads Python projects (including multiple files and folders), analyzes the code using Abstract Syntax Trees (AST), and generates comprehensive test cases based on:

- **Function signatures** and argument analysis
- **Docstrings** for understanding purpose and constraints
- **Code patterns** (loops, conditionals, error handling)
- **Domain knowledge** (recognizes common patterns like arithmetic operations, list processing, etc.)
- **Error conditions** (raises exceptions, boundary cases)

The output is a well-structured JSON file containing organized test cases with:

- Normal cases (typical inputs)
- Edge cases (boundary conditions)
- Error cases (exception handling)
- All inputs and expected outputs

## Features

**Automatic Code Analysis**: Parses Python AST to extract function and class information
**Intelligent Test Generation**: Pattern-based test case creation for common operations
**Comprehensive Coverage**: Normal cases, edge cases, boundary conditions, and error cases
**Multi-file Support**: Analyzes entire projects recursively
**JSON Output**: Machine-readable test case format
**Docstring Integration**: Uses function documentation to enhance understanding
**Error Tracking**: Identifies and tests error conditions

## Project Structure

```
v1/
├── calculator.py           # Sample application (calculator)
├── generate_tests.py       # Main test case generator script
├── generated_tests.json    # Output test cases (auto-generated)
└── README.md              # This file
```

## Sample Application: Calculator

The `calculator.py` file demonstrates the tool's capabilities with a comprehensive calculator application containing:

- **Arithmetic Operations**: add, subtract, multiply, divide, power, modulo
- **Mathematical Functions**: factorial, is_prime, calculate_average
- **Classes**: Calculator class with history tracking

## How to Use

### Basic Usage

```bash
python generate_tests.py <project_path> [output_file]
```

### Examples

**Analyze the current directory:**

```bash
python generate_tests.py .
```

**Analyze with custom output file:**

```bash
python generate_tests.py . my_tests.json
```

**Analyze a specific project folder:**

```bash
python generate_tests.py /path/to/project generated_tests.json
```

## Generated Test Cases Structure

The output JSON file contains:

```json
{
  "metadata": {
    "generated_tool": "Automated Test Case Generator",
    "version": "1.0"
  },
  "test_suites": [
    {
      "function": "function_name",
      "docstring": "Function description...",
      "arguments": ["arg1", "arg2"],
      "test_cases": [
        {
          "name": "Test case name",
          "inputs": {
            "arg1": value1,
            "arg2": value2
          },
          "expected_output": expected_value,
          "category": "normal|edge_case|boundary|error_case"
        }
      ]
    }
  ]
}
```

## Test Case Categories

### 1. **Normal Cases** (`normal`)

Typical inputs that the function handles in standard operation.

Example:

```json
{
  "name": "Basic addition",
  "inputs": { "a": 5, "b": 3 },
  "expected_output": 8,
  "category": "normal"
}
```

### 2. **Boundary Cases** (`boundary`)

Edge values at the boundaries of valid input ranges (0, 1, empty lists, etc.).

Example:

```json
{
  "name": "Adding zero",
  "inputs": { "a": 0, "b": 5 },
  "expected_output": 5,
  "category": "boundary"
}
```

### 3. **Edge Cases** (`edge_case`)

Special conditions like negative numbers, very large values, etc.

Example:

```json
{
  "name": "Negative factorial (should raise error)",
  "inputs": { "n": -5 },
  "expected_error": "ValueError",
  "category": "error_case"
}
```

### 4. **Error Cases** (`error_case`)

Inputs that should trigger exceptions or error conditions.

Example:

```json
{
  "name": "Divide by zero",
  "inputs": { "a": 5, "b": 0 },
  "expected_error": "ValueError",
  "category": "error_case"
}
```

## Generated Test Cases Example

For the calculator project, the tool generates 44 test cases across 13 test suites:

### Add Function (4 test cases)

- Basic addition
- Adding negative numbers
- Adding zero
- Adding floats

### Divide Function (4 test cases)

- Basic division
- Division resulting in float
- Divide by zero (error case)
- Negative division

### Factorial Function (5 test cases)

- Factorial of 5
- Factorial of 0
- Factorial of 1
- Negative factorial (error)
- Non-integer input (error)

### Is Prime Function (6 test cases)

- Prime number
- Non-prime number
- Number 2 (smallest prime)
- Number 1 (not prime)
- Negative number
- Zero

...and more for other functions (multiply, power, modulo, average, etc.)

## How It Works

### Phase 1: Code Analysis

```
1. Scan directory for Python files
2. Parse each file using Python's AST module
3. Extract function/class definitions
4. Collect function signatures and docstrings
5. Analyze function body for patterns (loops, conditionals, errors)
```

### Phase 2: Test Generation

```
1. Match function names against known patterns (add, divide, factorial, etc.)
2. Generate appropriate test cases for each pattern
3. Include normal, boundary, edge, and error cases
4. Extract input/output specifications from docstrings
```

### Phase 3: Output

```
1. Organize test cases by function
2. Structure as JSON with metadata
3. Save to output file
4. Print summary statistics
```

## Code Architecture

### Main Classes

**FunctionAnalyzer** (extends ast.NodeVisitor)

- Traverses Python AST
- Extracts function/class definitions
- Collects metadata and code patterns

**TestCaseGenerator**

- Generates test cases based on analysis
- Implements pattern recognition for common operations
- Handles special cases (arithmetic, string operations, etc.)

**ProjectAnalyzer**

- Main orchestrator class
- Manages file scanning and analysis
- Coordinates test generation and JSON output

## Extending the Tool

To add support for more function patterns, modify the `_generate_specific_tests()` method in `TestCaseGenerator`:

```python
elif "custom_operation" in func_name_lower:
    tests.extend([
        {
            "name": "Test case name",
            "inputs": {"param": value},
            "expected_output": expected,
            "category": "normal"
        },
        # ... more test cases
    ])
```

## Limitations and Notes

1. **Pattern Recognition**: The tool uses function names and patterns to determine test cases. More complex logic may need manual adjustments.

2. **Docstring Dependency**: Better docstrings lead to better test generation.

3. **Type Hints**: Currently doesn't leverage type hints, but could be extended to do so.

4. **Coverage**: Generated tests provide a good starting point but should be supplemented with custom tests for complex logic.

5. **Performance**: Large projects with many files will take longer to analyze.

## Future Enhancements

- [ ] Support for type hints to improve test generation
- [ ] Integration with pytest for automatic test execution
- [ ] ML-based pattern recognition for smarter test cases
- [ ] Support for more languages (TypeScript, Java, Go, etc.)
- [ ] Interactive mode to refine generated tests
- [ ] Test case priority/difficulty rating
- [ ] Integration with CI/CD pipelines

## Dependencies

- Python 3.6+
- Standard library only (ast, json, pathlib)

No external dependencies required

## Running the Example

```bash
# Generate tests for the calculator
python generate_tests.py . generated_tests.json

# View the output
cat generated_tests.json | python -m json.tool  # Pretty print

# Or use any JSON viewer/editor
```

## Output Example

```json
{
  "metadata": {
    "generated_tool": "Automated Test Case Generator",
    "version": "1.0"
  },
  "test_suites": [
    {
      "function": "divide",
      "docstring": "Divide two numbers...",
      "arguments": ["a", "b"],
      "test_cases": [
        {
          "name": "Basic division",
          "inputs": { "a": 20, "b": 4 },
          "expected_output": 5,
          "category": "normal"
        },
        {
          "name": "Divide by zero (should raise error)",
          "inputs": { "a": 5, "b": 0 },
          "expected_error": "ValueError",
          "category": "error_case"
        }
      ]
    }
  ]
}
```
