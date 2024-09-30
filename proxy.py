from flask import Flask, jsonify, render_template, request, Response
from partScraper import runScraper
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/proxy', methods=['POST'])
def proxy():
    # URL of the external API
    api_url = 'https://importglasscorp.com/ajax.php'

    # Get the raw data from the request
    data = request.get_data()

    # Get the headers from the original request
    headers = {
        'Content-Type': request.headers.get('Content-Type')
    }

    # Forward the request to the external API
    try:
        response = requests.post(api_url, data=data, headers=headers)
        response.raise_for_status()
        # Return the response content and status code
        return Response(response.content, status=response.status_code, content_type=response.headers.get('Content-Type'))
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/vehicle-lookup', methods=['GET'])
def vehicleLookup():
    return render_template('vehicle-lookup.html')


@app.route('/part-search/<partNumber>', methods=['GET'])
def partSearch(partNumber):
    return render_template('products.html', data=partNumber)

@app.route('/products/<partNumber>', methods=['GET'])
def products(partNumber):
    data = runScraper(partNumber)
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)
