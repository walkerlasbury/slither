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
    """Scramble variable and non-default function names in the code."""
    tree = ast.parse(code)

    # List of default Python function names that should be excluded from scrambling
    default_functions = ['print', 'input']

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

                if node.id in self.name_map:
                    return ast.copy_location(ast.Name(id=self.name_map[node.id], ctx=node.ctx), node)

                if node.id not in default_functions:
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
