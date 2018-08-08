# -*- coding: utf-8 -*-
# Copyright 2018 IBM Corp. All Rights Reserved.

# Licensed under the Apache License, Version 2.0 (the “License”)
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
from watson_developer_cloud import AssistantV1
from watson_developer_cloud import SpeechToTextV1
from watson_developer_cloud import TextToSpeechV1


app = Flask(__name__)
socketio = SocketIO(app)


if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'conversation' in vcap:
        conversationCreds = vcap['conversation'][0]['credentials']
        assistantUsername = conversationCreds['username']
        assistantPassword = conversationCreds['password']

    if 'text_to_speech' in vcap:
        textToSpeechCreds = vcap['text_to_speech'][0]['credentials']
        textToSpeechUser = textToSpeechCreds['username']
        textToSpeechPassword = textToSpeechCreds['password']
    if 'speech_to_text' in vcap:
        speechToTextCreds = vcap['speech_to_text'][0]['credentials']
        speechToTextUser = speechToTextCreds['username']
        speechToTextPassword = speechToTextCreds['password']
    if "WORKSPACE_ID" in os.environ:
        workspace_id = os.getenv('WORKSPACE_ID')

    if "ASSISTANT_IAM_APIKEY" in os.environ:
        assistantIAMKey = os.getenv('ASSISTANT_IAM_APIKEY')

else:
    print('Found local VCAP_SERVICES')
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    assistantUsername = os.environ.get('ASSISTANT_USERNAME')
    assistantPassword = os.environ.get('ASSISTANT_PASSWORD')
    assistantIAMKey = os.environ.get('ASSISTANT_IAM_APIKEY')
    assistantUrl = os.environ.get('ASSISTANT_URL')

    textToSpeechUser = os.environ.get('TEXTTOSPEECH_USER')
    textToSpeechPassword = os.environ.get('TEXTTOSPEECH_PASSWORD')

    speechToTextUser = os.environ.get('SPEECHTOTEXT_USER')
    speechToTextPassword = os.environ.get('SPEECHTOTEXT_PASSWORD')
    workspace_id = os.environ.get('WORKSPACE_ID')


@app.route('/')
def Welcome():
    return app.send_static_file('index.html')


@app.route('/api/conversation', methods=['POST', 'GET'])
def getConvResponse():
    # Instantiate Watson Assistant client.
    # only give a url if we have one (don't override the default)
    try:
        assistant_kwargs = {
            'version': '2018-07-06',
            'username': assistantUsername,
            'password': assistantPassword,
            'iam_api_key': assistantIAMKey
        }


        assistant = AssistantV1(**assistant_kwargs)

        convText = request.form.get('convText')
        convContext = request.form.get('context')

        if convContext is None:
            convContext = "{}"
        print(convContext)
        jsonContext = json.loads(convContext)

        response = assistant.message(workspace_id=workspace_id,
                                 input={'text': convText},
                                 context=jsonContext)
    except Exception as e:
        print(e)

    print(response)
    reponseText = response["output"]["text"]
    responseDetails = {'responseText': reponseText[0],
                       'context': response["context"]}
    return jsonify(results=responseDetails)


@app.route('/api/speech-to-text/token', methods=['POST', 'GET'])
def getSttToken():
    try:
        authorization = AuthorizationV1(username=speechToTextUser,
                                        password=speechToTextPassword)
        retvalue = authorization.get_token(url=SpeechToTextV1.default_url)
    except Exception as e:
        print(e)
    return retvalue


@app.route('/api/text-to-speech/token', methods=['POST', 'GET'])
def getTtsToken():
    try:
        authorization = AuthorizationV1(username=textToSpeechUser,
                                        password=textToSpeechPassword)
        retvalue = authorization.get_token(url=TextToSpeechV1.default_url)
    except Exception as e:
        print(e)
    return retvalue


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=int(port))
