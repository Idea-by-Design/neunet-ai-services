from flask import Flask, request, jsonify
from services.ai_job_description.generate_description import generate_description

app = Flask(__name__)

@app.route('/ai', methods=['POST'])
def generate_job_description():
    data = request.json
    description = generate_description(data)
    return jsonify({'generated_description': description})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
