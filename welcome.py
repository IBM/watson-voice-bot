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
from flask import Flask, Response
from flask import jsonify
from flask import request
from flask_socketio import SocketIO
from flask_cors import CORS
from watson_developer_cloud import AssistantV1
from watson_developer_cloud import SpeechToTextV1
from watson_developer_cloud import TextToSpeechV1

app = Flask(__name__)
socketio = SocketIO(app)
CORS(app)

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'conversation' in vcap:
        conversationCreds = vcap['conversation'][0]['credentials']
        assistantUsername = conversationCreds.get('username')
        assistantPassword = conversationCreds.get('password')
        assistantIAMKey = conversationCreds.get('apikey')
        assistantUrl = conversationCreds.get('url')

    if 'text_to_speech' in vcap:
        textToSpeechCreds = vcap['text_to_speech'][0]['credentials']
        textToSpeechUser = textToSpeechCreds.get('username')
        textToSpeechPassword = textToSpeechCreds.get('password')
        textToSpeechUrl = textToSpeechCreds.get('url')
        textToSpeechIAMKey = textToSpeechCreds.get('apikey')
    if 'speech_to_text' in vcap:
        speechToTextCreds = vcap['speech_to_text'][0]['credentials']
        speechToTextUser = speechToTextCreds.get('username')
        speechToTextPassword = speechToTextCreds.get('password')
        speechToTextUrl = speechToTextCreds.get('url')
        speechToTextIAMKey = speechToTextCreds.get('apikey')

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
    textToSpeechUrl = os.environ.get('TEXTTOSPEECH_URL')
    textToSpeechIAMKey = os.environ.get('TEXTTOSPEECH_IAM_APIKEY')

    speechToTextUser = os.environ.get('SPEECHTOTEXT_USER')
    speechToTextPassword = os.environ.get('SPEECHTOTEXT_PASSWORD')
    workspace_id = os.environ.get('WORKSPACE_ID')
    speechToTextUrl = os.environ.get('SPEECHTOTEXT_URL')
    speechToTextIAMKey = os.environ.get('SPEECHTOTEXT_IAM_APIKEY')


@app.route('/')
def Welcome():
    return app.send_static_file('index.html')


@app.route('/api/conversation', methods=['POST', 'GET'])
def getConvResponse():
    # Instantiate Watson Assistant client.
    # only give a url if we have one (don't override the default)
    try:
        assistant_kwargs = {
            'version': '2018-09-20',
            'username': assistantUsername,
            'password': assistantPassword,
            'iam_apikey': assistantIAMKey,
            'url': assistantUrl
        }

        assistant = AssistantV1(**assistant_kwargs)

        convText = request.form.get('convText')
        convContext = request.form.get('context')

        if convContext is None:
            convContext = "{}"
        jsonContext = json.loads(convContext)

        response = assistant.message(workspace_id=workspace_id,
                                     input={'text': convText},
                                     context=jsonContext)
    except Exception as e:
        print(e)

    response = response.get_result()
    reponseText = response["output"]["text"]
    responseDetails = {'responseText': reponseText[0],
                       'context': response["context"]}
    return jsonify(results=responseDetails)


@app.route('/api/text-to-speech', methods=['POST'])
def getSpeechFromText():
    tts_kwargs = {
            'username': textToSpeechUser,
            'password': textToSpeechPassword,
            'iam_apikey': textToSpeechIAMKey,
            'url': textToSpeechUrl
    }

    inputText = request.form.get('text')
    ttsService = TextToSpeechV1(**tts_kwargs)

    def generate():
        audioOut = ttsService.synthesize(
            inputText,
            'audio/wav',
            'en-US_AllisonVoice').get_result()

        data = audioOut.content

        yield data

    return Response(response=generate(), mimetype="audio/x-wav")


@app.route('/api/speech-to-text', methods=['POST'])
def getTextFromSpeech():
    tts_kwargs = {
            'username': speechToTextUser,
            'password': speechToTextPassword,
            'iam_apikey': speechToTextIAMKey,
            'url': speechToTextUrl
    }

    sttService = SpeechToTextV1(**tts_kwargs)

    response = sttService.recognize(
            audio=request.get_data(cache=False),
            content_type='audio/wav',
            timestamps=True,
            word_confidence=True).get_result()

    text_output = response['results'][0]['alternatives'][0]['transcript']

    return Response(response=text_output, mimetype='plain/text')


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=int(port))
