# Copyright 2018 IBM Corp. All Rights Reserved.

# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os

from dotenv import load_dotenv
from flask import Flask
from flask import jsonify
from flask import request
from flask_socketio import SocketIO
from watson_developer_cloud import AuthorizationV1
from watson_developer_cloud import ConversationV1
from watson_developer_cloud import SpeechToTextV1
from watson_developer_cloud import TextToSpeechV1


app = Flask(__name__)
socketio = SocketIO(app)


if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'conversation' in vcap:
        conversationcreds = vcap['conversation'][0]['credentials']
        conversationUser = conversationcreds['username']
        conversationPassword = conversationcreds['password']
    if 'text_to_speech' in vcap:
        texttospeachcreds = vcap['text_to_speech'][0]['credentials']
        texttospeachUser = texttospeachcreds['username']
        texttospeachPassword = texttospeachcreds['password']
    if 'speech_to_text' in vcap:
        speachtotextcreds = vcap['speech_to_text'][0]['credentials']
        speachtotextUser = speachtotextcreds['username']
        speachtotextPassword = speachtotextcreds['password']
    if "WORKSPACEID" in os.environ:
        workspace_id = os.getenv('WORKSPACEID')


else:
    print('Found local VCAP_SERVICES')
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    conversationUser = os.environ.get('CONVERSATION_USER')
    conversationPassword = os.environ.get('CONVERSATION_PASSWORD')

    texttospeachUser = os.environ.get('TEXTTOSPEECH_USER')
    texttospeachPassword = os.environ.get('TEXTTOSPEECH_PASSWORD')

    speachtotextUser = os.environ.get('SPEECHTOTEXT_USER')
    speachtotextPassword = os.environ.get('SPEECHTOTEXT_PASSWORD')
    workspace_id = os.environ.get('WORKSPACEID')


@app.route('/')
def Welcome():
    return app.send_static_file('index.html')


@app.route('/api/conversation', methods=['POST', 'GET'])
def getConvResponse():
    conversation = ConversationV1(
        username=conversationUser,
        password=conversationPassword,
        version='2017-04-21')
    convText = request.form.get('convText')
    convContext = request.form.get('context')

    if convContext is None:
        convContext = "{}"

    jsonContext = json.loads(convContext)
    response = conversation.message(workspace_id=workspace_id,
                                    input={'text': convText},
                                    context=jsonContext)
    reponseText = response["output"]["text"]
    responseDetails = {'responseText': reponseText[0],
                       'context': response["context"]}
    return jsonify(results=responseDetails)


@app.route('/api/speech-to-text/token', methods=['POST', 'GET'])
def getSttToken():
    try:
        authorization = AuthorizationV1(username=speachtotextUser,
                                        password=speachtotextPassword)
        retvalue = authorization.get_token(url=SpeechToTextV1.default_url)
    except Exception as e:
        print(e)
    return retvalue


@app.route('/api/text-to-speech/token', methods=['POST', 'GET'])
def getTtsToken():
    try:
        authorization = AuthorizationV1(username=texttospeachUser,
                                        password=texttospeachPassword)
        retvalue = authorization.get_token(url=TextToSpeechV1.default_url)
    except Exception as e:
        print(e)
    return retvalue


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=int(port))
