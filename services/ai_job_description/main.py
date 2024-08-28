from flask import Flask, request, jsonify
from generate_description import generate_description

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    try:
        generated_description = generate_description(data)
        return jsonify({'generated_description': generated_description}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)