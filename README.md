[![Build Status](https://travis-ci.org/IBM/watson-voice-bot.svg?branch=master)](https://travis-ci.org/IBM/watson-voice-bot)

# Create a web based chatbot with voice input and output

In this code pattern we will create a web based chat bot, but the twist here is that we'll be using voice input and output. For the conversation dialog we'll of course be using Watson Assistant, but we'll also be using Watson Speech To Text to capture the user's voice, and lastly we'll use Watson Text To Speech to playback the chatbots response to the user. The web application itself is built on top of JQuery and Python Flask.

When the reader has completed this code pattern they will understand how to:

* Make a Watson Speech To Text call using a Web Socket Connection
* Make a Watson Text to Speech REST API call
* Send and receive messages to Watson Assistant using REST APIs
* Integrate Watson Speech To Text, Watson Text To Speech and Watson Assistant in a web app

![](doc/source/images/architecture.png)

## Flow

1. User selects the microphone option on the browser and speaks.
2. The voice is passed on to Watson Speech To Text using a Web Socket connection.
3. The text from Watson Speech to Text is extracted and sent as input to Watson Assistant.
4. The response from Watson Assistant is passed onto Watson Text to Speech.
5. The audio output is sent to the web application and played back to the user, while the UI also displays the same text.

## Included components

* [Watson Speech-to-Text](https://www.ibm.com/watson/services/speech-to-text/): A service that converts human voice into written text.
* [Watson Text-to-Speech](https://www.ibm.com/watson/services/text-to-speech/): Converts written text into natural sounding audio in a variety of languages and voices.
* [Watson Assistant](https://www.ibm.com/watson/ai-assistant/): Create a chatbot with a program that conducts a conversation via auditory or textual methods.

## Featured technologies

* [Flask](http://flask.pocoo.org/): Python is a programming language that lets you work more quickly and integrate your systems more effectively.
* [jQuery](https://jquery.com/): It is a cross-platform JavaScript library designed to simplify the client-side scripting of HTML.

<!--
# Watch the Video
[![](http://img.youtube.com/vi/Jxi7U7VOMYg/0.jpg)](https://www.youtube.com/watch?v=Jxi7U7VOMYg)
-->

# Steps

We'll have two methods to run this application: [using an easy one-click deploy option](#using-the-deploy-to-ibm-cloud-button), or [locally with a few CLI tools](#run-the-application-locally). Depending on your objective, learning or seeing the app quickly, choose accordingly.

## Using the `Deploy to IBM Cloud` button

> If you prefer to deploy the application manually, scroll down to the next section.

Steps:

1. [Clone the repo](#1-clone-the-repo)
2. [Create the services and deploy the web app](#2-create-the-services-and-deploy-the-web-app)
3. [Upload the Watson Assistant workspace](#3-upload-the-watson-assistant-workspace)
4. [Configure environment variables](#4-configure-environment-variables)

### 1. Clone the repo

Clone the `watson-voice-bot` repo locally. In a terminal, run:

```
git clone https://github.com/IBM/watson-voice-bot
```

We’ll be using the file [`data/workspace.json`](data/workspace.json).

### 2. Create the services and deploy the web app

The next step is to deploy the application, we'll do this by clicking the button below. A nice byproduct of doing this is that the services required (Speech-to-Text, Text-to-Speech, and Assistant) will be created automatically. Click the button below.

[![Deploy to IBM Cloud](https://bluemix.net/deploy/button.png)](https://bluemix.net/deploy?repository=https://github.com/IBM/watson-voice-bot.git)

When the DevOps Toolchain Pipeline appears, click on the `Deploy` button to start the deployment. You can optionally, click on the `Delivery Pipeline` to watch the logs as the app is deployed.

![](doc/source/images/toolchain-pipeline.png)

Once deployed, the app can be viewed by clicking `View app`. The app can also be viewed in the dashboard. The app should be prefixed with the string `watson-voice-bot-`, and the corresponding services that were created can easily be identified by the `wvb-` prefix, i.e.: `wvb-assistant`.

### 3. Upload the Watson Assistant workspace

Now that our services are created and the app is deployed we need to update the application to use a specific Watson Assistant dialog. We'll be using the file [`data/workspace.json`](data/workspace.json), which documents our entire conversation dialog. To do this, launch the Watson Assistant tool and use the `import` icon button on the right. Find the [`data/workspace.json`](data/workspace.json) file from the cloned repo and import that to the Watson Assistant tool.

Each workspace in Watson Assistant has a specific ID. To find the `Workspace ID` for a given workspace, click the context menu of the workspace and select `View details`. The workspace ID can be copied and saved as we'll need it in the next step.

Optionally, to view the conversation dialog select the workspace and choose the **Dialog** tab. Here's a snippet of the dialog:

![](doc/source/images/dialog.png)

### 4. Configure environment variables

The last step to perform is to configure our application to use the right Watson Assistant dialog. We'll solve this by specifying the workspace ID as an environment variable that the web application has access to read. To do this we'll navigate to our application overview from the [IBM Cloud Dashboard](https://console.bluemix.net/dashboard/apps/), searching for `watson-voice-bot` and clicking on the name.

From the application overview, we can click on the `Runtime` menu located in the navigation bar on the left. Select the `Environment Variables` tab. Scroll down and click on `Add`.

![](doc/source/images/add_env_variable.png)

We'll add the environment variable key name as `WORKSPACEID` and for the value we'll use the workspace ID from Step 3. Click `Save` and wait for the application to reload.

Once the application restarts, click on the generated URL and start interacting with your voice enabled chatbot! See [Sample output](#sample-output) for things to say to your chatbot.

## Run the application locally

1. [Clone the repo](#1-clone-the-repo)
2. [Create Watson services with IBM Cloud](#2-create-watson-services-with-ibm-cloud)
3. [Upload the Watson Assistant workspace](#3-upload-the-watson-assistant-workspace)
4. [Configure `.env` with credentials](#4-configure-env-with-credentials)
5. [OPTIONAL Create a virtual environment](#5-optional-create-a-virtual-environment)
6. [Install the requirements](#6-install-the-requirements)
7. [Run the application](#7-run-the-application)

### 1. Clone the repo

Clone the `watson-voice-bot` repo locally. In a terminal, run:

```
git clone https://github.com/IBM/watson-voice-bot
```

We’ll be using the file [`data/workspace.json`](data/workspace.json).

### 2. Create Watson services with IBM Cloud

Create the following services:

* [**Watson Assistant**](https://console.ng.bluemix.net/catalog/services/conversation)
* [**Watson Speech To Text**](https://console.bluemix.net/catalog/services/speech-to-text)
* [**Watson Text To Speech**](https://console.bluemix.net/catalog/services/text-to-speech)

### 3. Upload the Watson Assistant workspace

Now that our services are created and the app is deployed we need to update the application to use a specific Watson Assistant dialog. We'll be using the file [`data/workspace.json`](data/workspace.json), which documents our entire conversation dialog. To do this, launch the Watson Assistant tool and use the `import` icon button on the right. Find the [`data/workspace.json`](data/workspace.json) file from the cloned repo and import that to the Watson Assistant tool.

Each workspace in Watson Assistant has a specific ID. To find the `Workspace ID` for a given workspace, click the context menu of the workspace and select `View details`. The workspace ID can be copied and saved as we'll need it in the next step.

Optionally, to view the conversation dialog select the workspace and choose the **Dialog** tab. Here's a snippet of the dialog:

![](doc/source/images/dialog.png)

### 4. Configure `.env` with credentials

Our services are created and workspace uploaded. It's now time to let our application run locally and to do that we'll configure a simple text file with the values we want to use. We begin by copying the the [`env.sample`](env.sample) file and naming it `.env`.

```
cp env.sample .env
```

We now populate the key-value pairs with credentials for each IBM Cloud service (Assistant, Speech To Text, and Text To Speech). These values can be found in the `Services` menu in IBM Cloud, by selecting the `Service Credentials` option for each service.

Lastly, the `WORKSPACEID` value was retrieved in the previous step, we use that value here.

#### `env.sample:`

```
# Replace the credentials here with your own.
# Rename this file to .env before starting the app.

# Watson Assistant
WORKSPACE_ID=<add_assistant_workspace>
ASSISTANT_URL=<add_assistant_url>
## Un-comment and use either username+password or IAM apikey.
# ASSISTANT_USERNAME=<add_assistant_username>
# ASSISTANT_PASSWORD=<add_assistant_password>
# ASSISTANT_IAM_APIKEY=<add_assistant_apikey>

# Watson Speech To Text
SPEECHTOTEXT_USER=<add_stt_username>
SPEECHTOTEXT_PASSWORD=<add stt password>

# Watson Text To SpeechToText
TEXTTOSPEECH_USER=<add tts username>
TEXTTOSPEECH_PASSWORD=<add tts password>
```

### 5. OPTIONAL Create a virtual environment

$ `virtualenv watson-voice-bot`

Activate the virtual environment:
$ `. watson-voice-bot/bin/activate`

Deactivate the virtual environment:
$ `deactivate`

### 6. Install the requirements

Run:

$ `pip install -r requirements.txt`

to install the app's dependencies

### 7. Run the application

1. Start the app by running `python welcome.py`
2. Launch a browser and navigate to [http://localhost:5000](http://localhost:5000)
3. Click on the microphone icon to begin speaking and click it again when you are finished.

# Sample output

Follow the script below for a sample path in an insurance domain, or configure your own dialog under Watson Assistant.

```
Voice Bot: Hello. How can I help you?
User Reply: I am trying to buy an insurance

Voice Bot: You have come to the right place We offer you a smart, affordable and convenient way to safeguard the future for you and your family. Can I ask you a couple of questions to come up with the best plan for you?
User Reply: ok sure

Voice Bot: Please tell me your Name followed by Date Of Birth and Annual Income
User Reply: This is Mary

Voice Bot: Please enter your Date of Birth
User Reply: 2nd June 1945

Voice Bot: Your annual income?
User Reply: 1200000 dollars

Voice Bot: Do you smoke?
User Reply: Nope I dont

Voice Bot: Please tell me your gender
User Reply: Female

Voice Bot: Enter a protection type
Select one among Basic Life Cover, Fixed Income Protection or Increasing Income Protection.
User Reply: Life Cover

Voice Bot: What premium payment frequency would you prefer? Monthly, Quarterly, Half Yearly or Yearly?
User Reply: Monthly

Voice Bot: What term would you want to go for? Enter a range between 10 years to 35 years.
User Reply: 8 years

Voice Bot: Please enter a term ranging between 10 years to 35 years.
User Reply: 12

Voice Bot: Your yearly premium for 12 years under the Basic Life Cover plan is 67767 dollars. Do you want to try any other options or go ahead with buying this?
User Reply: No What is Basic Life Cover?

Voice Bot: On death during the Policy term, Sum Assured as a lump sum is paid to the nominee and the policy terminates.
User Reply: ok Thanks

Voice Bot: Have a great day
```

![](doc/source/images/sample_output.png)

# Links

* [Watson Node.js SDK](https://github.com/watson-developer-cloud/node-sdk)
* [Relevancy Training Demo Video](https://www.youtube.com/watch?v=8BiuQKPQZJk)
* [Relevancy Training Demo Notebook](https://github.com/akmnua/relevancy_passage_bww)

# Learn more

* **Artificial Intelligence Code Patterns**: Enjoyed this Code Pattern? Check out our other [AI Code Patterns](https://developer.ibm.com/code/technologies/artificial-intelligence/).
* **AI and Data Code Pattern Playlist**: Bookmark our [playlist](https://www.youtube.com/playlist?list=PLzUbsvIyrNfknNewObx5N7uGZ5FKH0Fde) with all of our Code Pattern videos
* **With Watson**: Want to take your Watson app to the next level? Looking to utilize Watson Brand assets? [Join the With Watson program](https://www.ibm.com/watson/with-watson/) to leverage exclusive brand, marketing, and tech resources to amplify and accelerate your Watson embedded commercial solution.

# License
[Apache 2.0](LICENSE)
