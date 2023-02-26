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


#AgentTips
@app.route('/agent_tips', methods=['POST'])
def get_agentTips(key):
    hashmap = {}
    connection = get_connection()
    mycursor = connection.cursor()
    mycursor.execute('SELECT * FROM AgentTips')
    result = mycursor.fetchall()
    #print(result[0]['Tips'])
    hashmap1 = {0:'astra', 1:'breach', 2:'brimstone', 3:'chamber', 4:'cypher', 5:'jett', 6:'KAY/O', 7:'killjoy', 8:'neon', 9:'omen', 10:'phoenix', 11:'raze', 12:'reyna', 13:'sage', 14:'skye', 15:'sova', 16:'viper', 17:'yoru', 18:'harbour', 19:'fade'}

    for i in result:
        hashmap[hashmap1[i['Idx']]] = i['Tips']
    return(hashmap[key])


@app.route('/maptips', methods=['POST'])
def get_MapTips(key): #Suchith
    connection = get_connection()
    hashmap_MapTips = {}
    mycursor = connection.cursor()
    mycursor.execute('SELECT * FROM MapTips')
    result = mycursor.fetchall()
    #print(result[0]['Tips'])
    hashmap2 = {0: 'map_ascent', 1: 'map_bind', 2: 'map_breeze', 3: 'map_fracture', 4: 'map_haven', 5: 'map_icebox', 6: 'map_lotus', 7: 'map_pearl', 8: 'map_split'}
  
    for i in result:
        hashmap_MapTips[hashmap2[i['Idx']]] = i['Tips']
    return(hashmap_MapTips[key])

@app.route('/shootingtips', methods=['POST'])
def shootingtips(key):
    hashmap_headshots = {}
    connection = get_connection()
    mycursor = connection.cursor()
    mycursor.execute('SELECT * FROM HeadshotImprovement')
    result = mycursor.fetchall()
    #print(result[0]['Tips'])
    hashmap2 = {0: 'Iron/bronze', 1: 'Silver/gold/plat', 2: 'Diamond/ascendant', 3: 'Immortal/radiant'}
    for i in result:
        hashmap_headshots[hashmap2[i['Idx']]] = i['Tips']
    return(hashmap_headshots[key])

@app.route('/discord', methods=['POST','GET'])
def handle_discord():
    PUBLIC_KEY = ''
    #Please insert own public key here.
    
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

    #print(request.data)
    req_data = json.loads(request.data.decode('utf-8'))
    #print(req_data)
    slash_command = req_data["data"]["name"]
    
    #extract map_breeze from data
    
    #print(slash_command)
    
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
        givenmap = req_data['data']['options'][0]['value']
        return {
        'type': 4,
        'data': {
            'content': get_MapTips(givenmap)
        }
    }
    
    if slash_command == "agent_tips":
        givenagent = req_data['data']['options'][0]['value']
        return {
        'type': 4,
        'data': {
            'content': get_agentTips(givenagent)
        }
    }
    
    if slash_command == "shootingtips":
        givenmap = req_data['data']['options'][0]['value']
        return {
        'type': 4,
        'data': {
            'content': shootingtips(givenmap)
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
