from flask import Flask, request, jsonify, abort
from google.auth import compute_engine
import pymysql
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

app = Flask(__name__)

@app.route('/strat', methods=['POST'])
def get_random_strat():
    connection = get_connection()
    mycursor = connection.cursor()
    mycursor.execute('SELECT * FROM gotham ORDER BY RAND() LIMIT 1')
    result = mycursor.fetchone()
    connection.close()
    return result['Strats']

@app.route('/agent', methods=['POST'])
def get_random_agent():
    connection = get_connection()
    mycursor = connection.cursor()
    mycursor.execute("SELECT * FROM AgentList ORDER BY RAND() LIMIT 1")
    result = mycursor.fetchone()
    connection.close()
    return result['Agents']

@app.route('/discord', methods=['POST','GET'])
def handle_discord():
    PUBLIC_KEY = '3b3970fa9b15faaabab551ad3a1c947123a72ee8b8f7dea2e2edb7f95458e443'

    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))

    signature = request.headers["X-Signature-Ed25519"]
    timestamp = request.headers["X-Signature-Timestamp"]
    body = request.data.decode("utf-8")
    
    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
    except BadSignatureError:
        abort(401, 'invalid request signature')

    if request.json["type"] == 1:
        return jsonify({
            "type": 1
        })

    #message = request.json['message'] #message sent to bot
    response = f'Strat: {get_random_strat()}\nAgent: {get_random_agent()}'
    return {
        'type': 4,
        'data': {
            'content': response
        }
    }

def get_connection():
    credentials = compute_engine.Credentials()
    connection = pymysql.connect(
    user = 'hack',
    password = '12345',
    host = '34.27.157.107',
    port=3306,
    db = 'ValStratRoulette',
    cursorclass = pymysql.cursors.DictCursor,
    charset = 'utf8mb4',
    autocommit = True)
    return connection

if __name__ == "__main__":
    app.run()