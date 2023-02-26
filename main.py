from flask import Flask, request, jsonify, abort
import pymysql
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import json

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


@app.route('/maptips', methods=['POST'])
def get_map_tips(): #ChatGPT
    map_option = request.json['data'][0]['options'][0]['value']
    map_name = map_option.replace('map_', '')
    
    connection = get_connection()
    mycursor = connection.cursor()
    sql = 'SELECT Tips FROM MapTips WHERE MapName = %s'
    val = (map_name,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    connection.close()

    if result is not None:
        return result['Tips']
    else:
        return f"No tips found for {map_name}."


@app.route('/maptips', methods=['POST'])
def get_MapTips(key): #Suchith
    hashmap_MapTips = {}
    mycursor = connection.cursor()
    mycursor.execute('SELECT * FROM MapTips')
    result = mycursor.fetchall()
    #print(result[0]['Tips'])
    hashmap2 = {0: 'Ascent', 1: 'Bind', 2: 'Breeze', 3: 'Fracture', 4: 'Haven', 5: 'Icebox', 6: 'Lotus', 7: 'Pearl', 8: 'Split'}
  
    for i in result:
        hashmap_MapTips[hashmap2[i['Idx']]] = i['Tips']
    return(hashmap_MapTips[key])

@app.route('/discord', methods=['POST','GET'])
def handle_discord():
    PUBLIC_KEY = '3b3970fa9b15faaabab551ad3a1c947123a72ee8b8f7dea2e2edb7f95458e443'

    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    try:
        signature = request.headers["X-Signature-Ed25519"]
        timestamp = request.headers["X-Signature-Timestamp"]
    #except BadSignatureError:
    except KeyError: 
        abort(401, 'invalid request signature')
    body = request.data.decode("utf-8")
    
    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
    except BadSignatureError:
        abort(401, 'invalid request signature')

    if request.json["type"] == 1:
        return jsonify({
            "type": 1
        })

    print(request.data)
    req_data = json.loads(request.data.decode('utf-8'))
    slash_command = req_data["data"]["name"]
    print(slash_command)
    
    if slash_command == "stratroulette":
        return {
        'type': 4,
        'data': {
            'content': get_random_strat()
        }
    }
    if slash_command == "agent":
        return {
        'type': 4,
        'data': {
            'content': get_random_agent()
        }
    }
    
    if slash_command == "maptips":
        return {
        'type': 4,
        'data': {
            'content': get_map_tips()
        }
    }
    else:
        return {
        'type': 4,
        'data': {
            'content': "Invalid slash command"
        }}
    

def get_connection():
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
