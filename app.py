from flask import Flask, render_template, request
import ast
import random
import string
import astor

app = Flask(__name__)

def scramble_name(length=8):
    """Generate a random name with the given length."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def scramble_code(code):
    """Scramble variable names in the code while preserving function names."""
    tree = ast.parse(code)

    class NameScrambler(ast.NodeTransformer):
        def __init__(self):
            self.name_map = {}

        def scramble_name(self, original_name):
            """Scramble the original name or return the already scrambled name if available."""
            if original_name in self.name_map:
                return self.name_map[original_name]
            else:
                scrambled_name = scramble_name()
                self.name_map[original_name] = scrambled_name
                return scrambled_name

        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Store):
                return node

            if isinstance(node.ctx, ast.Load):
                if hasattr(node, 'parent') and isinstance(node.parent, ast.Attribute) and node.parent.attr == node.id:
                    return node

                if isinstance(node.parent, ast.FunctionDef):
                    return node  # Skip scrambling function names

                if isinstance(node.parent, ast.Call) and isinstance(node.parent.func, ast.Name) and node.parent.func.id == node.id:
                    return node  # Skip scrambling function names used as arguments

                if isinstance(node.parent, ast.Attribute) and node.parent.attr == node.id:
                    return node

                if isinstance(node.parent, ast.Assign) and isinstance(node.parent.targets[0], ast.Name) and node.parent.targets[0].id == node.id:
                    return node

                if isinstance(node.parent, ast.ExceptHandler) and isinstance(node.parent.name, ast.Name) and node.parent.name.id == node.id:
                    return node

                if isinstance(node.parent, ast.withitem) and isinstance(node.parent.optional_vars, ast.Name) and node.parent.optional_vars.id == node.id:
                    return node

                if isinstance(node.parent, ast.AnnAssign) and isinstance(node.parent.target, ast.Name) and node.parent.target.id == node.id:
                    return node

                if isinstance(node.parent, ast.arguments) and node.parent.vararg and node.parent.vararg.arg == node.id:
                    return node

                if node.id in self.name_map:
                    return ast.copy_location(ast.Name(id=self.name_map[node.id], ctx=node.ctx), node)

                scrambled_name = self.scramble_name(node.id)
                self.name_map[node.id] = scrambled_name
                return ast.copy_location(ast.Name(id=scrambled_name, ctx=node.ctx), node)

            return node

    scrambled_tree = NameScrambler().visit(tree)
    scrambled_code = astor.to_source(scrambled_tree)
    return scrambled_code

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_code = request.form['code']
        encrypted_code = scramble_code(original_code)
        return render_template('index.html', encrypted_code=encrypted_code)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
