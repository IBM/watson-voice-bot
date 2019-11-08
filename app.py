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
from flask import request, redirect
from flask_socketio import SocketIO
from flask_cors import CORS
from ibm_watson import AssistantV1
from ibm_watson import SpeechToTextV1
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core import get_authenticator_from_environment

import assistant_setup

app = Flask(__name__)
socketio = SocketIO(app)
CORS(app)


# Redirect http to https on CloudFoundry
@app.before_request
def before_request():
    fwd = request.headers.get('x-forwarded-proto')

    # Not on Cloud Foundry
    if fwd is None:
        return None
    # On Cloud Foundry and is https
    elif fwd == "https":
        return None
    # On Cloud Foundry and is http, then redirect
    elif fwd == "http":
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)


@app.route('/')
def Welcome():
    return app.send_static_file('index.html')


@app.route('/api/conversation', methods=['POST', 'GET'])
def getConvResponse():

    convText = request.form.get('convText')
    convContext = request.form.get('context', "{}")
    jsonContext = json.loads(convContext)

    response = assistant.message(workspace_id=workspace_id,
                                 input={'text': convText},
                                 context=jsonContext)

    response = response.get_result()
    reponseText = response["output"]["text"]
    responseDetails = {'responseText': '... '.join(reponseText),
                       'context': response["context"]}
    return jsonify(results=responseDetails)


@app.route('/api/text-to-speech', methods=['POST'])
def getSpeechFromText():
    inputText = request.form.get('text')
    ttsService = TextToSpeechV1()

    def generate():
        if inputText:
            audioOut = ttsService.synthesize(
                inputText,
                accept='audio/wav',
                voice='en-US_AllisonVoice').get_result()

            data = audioOut.content
        else:
            print("Empty response")
            data = "I have no response to that."

        yield data

    return Response(response=generate(), mimetype="audio/x-wav")


@app.route('/api/speech-to-text', methods=['POST'])
def getTextFromSpeech():

    sttService = SpeechToTextV1()

    response = sttService.recognize(
            audio=request.get_data(cache=False),
            content_type='audio/wav',
            timestamps=True,
            word_confidence=True,
            smart_formatting=True).get_result()

    # Ask user to repeat if STT can't transcribe the speech
    if len(response['results']) < 1:
        return Response(mimetype='plain/text',
                        response="Sorry, didn't get that. please try again!")

    text_output = response['results'][0]['alternatives'][0]['transcript']
    text_output = text_output.strip()
    return Response(response=text_output, mimetype='plain/text')


port = os.environ.get("PORT") or os.environ.get("VCAP_APP_PORT") or 5000
if __name__ == "__main__":
    load_dotenv()

    # SDK is currently confused. Only sees 'conversation' for CloudFoundry.
    authenticator = (get_authenticator_from_environment('assistant') or
                     get_authenticator_from_environment('conversation'))
    assistant = AssistantV1(version="2019-11-06", authenticator=authenticator)
    workspace_id = assistant_setup.init_skill(assistant)
    socketio.run(app, host='0.0.0.0', port=int(port))
