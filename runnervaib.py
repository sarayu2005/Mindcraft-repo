from flask import Flask, request, render_template, jsonify
# Fix: Ensure the filename matches your import
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
    
    actual_output = run_python_code(code, inputs)

    return jsonify({"output": actual_output})

if __name__ == '__main__':
    app.run(debug=True)