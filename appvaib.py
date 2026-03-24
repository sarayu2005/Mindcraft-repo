from flask import Flask, request, render_template, jsonify
# Changed 'runner' to 'runnervaib' to match your filename
from runnervaib import run_python_code 

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('menu.html')

@app.route('/set1')
def set1():
    return render_template('set1.html')

@app.route('/set2')
def set2():
    return render_template('set2.html')

@app.route('/set3')
def set3():
    return render_template('set3.html')

@app.route('/run', methods=['POST'])
def execute_code():
    data = request.json
    code = data.get('code', '')
    inputs = data.get('inputs', [])

    # Calls the logic from runnervaib.py
    actual_output = run_python_code(code, inputs)

    return jsonify({
        "output": actual_output
    })

if __name__ == '__main__':
    # Setting debug=True is perfect for development
    app.run(debug=True)