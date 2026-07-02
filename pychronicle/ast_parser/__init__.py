import ast
import json

class ASTParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.assignments = []

    def parse(self):
        with open(self.filepath, 'r') as f:
            source = f.read()
        
        tree = ast.parse(source)
        self._extract_assignments(tree)
        return self.assignments

    def _extract_assignments(self, tree):
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.assignments.append({
                            'line': node.lineno,
                            'variable': target.id,
                            'type': 'assignment'
                        })
            elif isinstance(node, ast.AugAssign):
                if isinstance(node.target, ast.Name):
                    self.assignments.append({
                        'line': node.lineno,
                        'variable': node.target.id,
                        'type': 'aug_assignment'
                    })

    def display(self):
        print(f"\n=== AST Parser Results: {self.filepath} ===")
        print(f"Total assignments found: {len(self.assignments)}\n")
        for item in self.assignments:
            print(f"Line {item['line']:3} | {item['type']:15} | Variable: {item['variable']}")

if __name__ == "__main__":
    import sys
    filepath = sys.argv[1] if len(sys.argv) > 1 else "test_script.py"
    parser = ASTParser(filepath)
    parser.parse()
    parser.display()