from flask import Flask, render_template, request
import ast
import random
import string

app = Flask(__name__)

def scramble_name(length=8):
    """Generate a random name with the given length."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def scramble_code(code):
    """Scramble function and variable names in the code."""
    tree = ast.parse(code)

    class NameScrambler(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            node.name = scramble_name()
            return self.generic_visit(node)

        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Store):
                node.id = scramble_name()
            return self.generic_visit(node)

    scrambled_tree = NameScrambler().visit(tree)
    scrambled_code = ast.unparse(scrambled_tree)
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
