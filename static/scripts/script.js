var conversationContext = '';
var audioContext = new AudioContext();
var audioInput = null,
    realAudioInput = null,
    inputPoint = null,
    audioRecorder = null;
var tokenSTT;
var tokenTTS;
var stream ;
var currentTime = 0;

window.addEventListener('load', init );

function init()
{
    initSTTService();
}
function initSTTService()
{
    fetch('/api/speech-to-text/token')
    .then(function(response) {
        return response.text();
    }).then(function(_token) {
        tokenSTT = _token;
    }).catch(function(error) {
        console.log(error);
    });
}
function initTTSService(){
  fetch('/api/text-to-speech/token')
  .then(function(response) {
      return response.text();
  }).then(function(_token) {
      tokenTTS = _token;
  }).catch(function(error) {
      console.log(error);
  });
}

function gotStream(stream) {
    inputPoint = audioContext.createGain();

    realAudioInput = audioContext.createMediaStreamSource(stream);
    audioInput = realAudioInput;
    audioInput.connect(inputPoint);

    analyserNode = audioContext.createAnalyser();
    analyserNode.fftSize = 2048;
    inputPoint.connect( analyserNode );

    audioRecorder = new Recorder( inputPoint );

    zeroGain = audioContext.createGain();
    zeroGain.gain.value = 0.0;
    inputPoint.connect( zeroGain );
    zeroGain.connect( audioContext.destination );
}

function display_msg_div(str, who) {
  var time    = new Date();
  var hours   = time.getHours();
  var minutes = time.getMinutes();
  var ampm    = hours >= 12 ? 'pm' : 'am';
  hours       = hours % 12;
  hours       = hours ? hours : 12; // the hour '0' should be '12'
  hours       = hours < 10 ? '0'+hours : hours;
  minutes     = minutes < 10 ? '0'+minutes : minutes;
  var strTime = hours + ':' + minutes + ' ' + ampm;
  var msg_html = "<div class='msg-card-wide mdl-card " + who + "'><div class='mdl-card__supporting-text'>"
  msg_html    += str;
  msg_html    += "</div><div class='" + who + "-line'>" + strTime + "</div></div>";

  $("#messages").append(msg_html);
  $('#messages').scrollTop($('#messages')[0].scrollHeight);

  if(who=='user') {
    $("#q").val("");
    $("#q").attr("disabled", "disabled");
    $("#p2").fadeTo(500,1);
  } else {
    $("#q").removeAttr("disabled");
    $("#p2").fadeTo(500,0);
  }

}

$(document).ready(function(){
  $("#q").attr("disabled", "disabled");
  $("#p2").fadeTo(500,1);
  $("#h").val('0');

  fetch('/api/text-to-speech/token')
  .then(function(response) {
      return response.text();
  }).then(function(_token) {
      tokenTTS = _token;
      $.ajax({
        url: "/api/conversation",
        convText: "",
        context:"",
      }).done(function(res) {
        conversationContext = res.results.context;
        display_msg_div(res.results.responseText, 'bot');

        stream = WatsonSpeech.TextToSpeech.synthesize({
            token: tokenTTS,
            text:res.results.responseText
          });

      }).fail(function(jqXHR, e) {
        console.log('Error: ' + jqXHR.responseText);
      });
  }).catch(function(error) {
      console.log(error);
  });


	$("#q").keyup(function(e){
			$("#submit").removeAttr("disabled");
      return false;
	});

	$("#submit").click(function(){
			var text = $("#q").val();
      display_msg_div(text, 'user');

      $.post("/api/conversation",
      {
          convText:res,
          context:JSON.stringify(conversationContext)
      }).done(function(res, status) {
          conversationContext = res.results.context;
          stream = WatsonSpeech.TextToSpeech.synthesize({
              token: tokenTTS,
              text:res.results.responseText
          });
          display_msg_div(res.results.responseText, 'bot');
      }).fail(function(jqXHR, e) {
        console.log('Error: ' + jqXHR.responseText);
      });

      return false;
	});
});

// Generate a unique id for this client
function guid() {
  function s4() {
    return Math.floor((1 + Math.random()) * 0x10000)
      .toString(16)
      .substring(1);
  }
  return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
    s4() + '-' + s4() + s4() + s4();
}

//setting speech to text function
window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition || null;
if (window.SpeechRecognition != null ){
    var recognizer = new window.SpeechRecognition();
    var transcription = document.getElementById('q');


    // Start recognising
    recognizer.onresult = function(event) {
        transcription.textContent = '';
        //$("#chat_input").val("I am listening ...");
        for (var i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
                transcription.textContent = event.results[i][0].transcript ;//+ ' (Confidence: ' + event.results[i][0].confidence + ')'
            } else {
                transcription.textContent += event.results[i][0].transcript;
            }
        }

        document.getElementById("2").src = "./static/img/mic.gif";
        var msg = $("#q").val();
        //$("#q").focus();
    };

    // Listen for errors
    recognizer.onerror = function(event) {
        console.log('Recognition error: ' + event.message + '<br />');
        document.getElementById("stt2").src = "./static/img/mic.gif";
        $('#q').val('');
    };

    recognizer.onend = function(event) {
        document.getElementById("stt2").src = "./static/img/mic.gif";
        //$('#q').val('');
    };
}
else{
    //$("#stt2").hide();
}

function startRecording() {
  //recorder = new Recorder(input);
  //recorder.record();
  startWSTTService();

}

function stopRecording() {
  stopWSTTService();
}





function stopCallback(blob){
  websocket.send(blob);
  websocket.send(JSON.stringify({action: 'stop'}));
}

//changing the mic icon depedening upon its name. Also disabling the speech recognizer in this case
$('#stt2').click(function(){
    var fullPath = document.getElementById("stt2").src;
    var filename = fullPath.replace(/^.*[\\\/]/, '');
    if(filename=="mic.gif"){
        try{
            document.getElementById("stt2").src = "./static/img/mic_active.png";
            startRecording();
        } catch(ex) {
            //console.log("Recognizer error .....");
        }
    }
    else{
        stopRecording();
        $("#q").val('');
        document.getElementById("stt2").src = "./static/img/mic.gif";
    }

});

function callTexttoSpeach(res)
{
  display_msg_div(res, 'bot');
  $("#q").attr("disabled", "disabled");

  $.post("/api/conversation",
  {
      convText:res,
      context:JSON.stringify(conversationContext)
  }).done(function(res, status) {
      conversationContext = res.results.context;

      stream = WatsonSpeech.TextToSpeech.synthesize({
          token: tokenTTS,
          text:res.results.responseText
      });
      display_msg_div(traslatedText, 'bot');

  }).fail(function(jqXHR, e) {
    console.log('Error: ' + jqXHR.responseText);
  });

}


function callConversation(res)
{
      $("#q").attr("disabled", "disabled");

      $.post("/api/conversation",
      {
          convText:res,
          context:JSON.stringify(conversationContext)
      }).done(function(res, status) {
          conversationContext = res.results.context;
          stream = WatsonSpeech.TextToSpeech.synthesize({
              token: tokenTTS,
              text:res.results.responseText
          });

      display_msg_div(res.results.responseText, 'bot');

      }).fail(function(jqXHR, e) {
        console.log('Error: ' + jqXHR.responseText);
      });
}

function startWSTTService()
{
    stream = WatsonSpeech.SpeechToText.recognizeMicrophone({
      token: tokenSTT,
      object_mode: false,
      //model:'en-US_BroadbandModel',
      model:'en-US_NarrowbandModel',
      //keywords: ['bill', 'plan', 'prepaid'],
      customization_id: "3f1b4290-c19a-4764-b7c7-7a28dd700eb5",
      acoustic_customization_id: "752ddc4e-c8ef-46dd-92bb-bed6bf9b194e",
      customization_weight: 1.0,
      keepMicrophone: true,
      max_alternatives: 0,
      //keywords_threshold: 1,
      interim_results: false
    });

    stream.setEncoding('utf8'); // get text instead of Buffers for on data events

    stream.on('data', function(data) {
      console.log("Time Taken by STT:"+ ((new Date().getTime() / 1000)- currentTime))
      display_msg_div(data, 'bot');
      callConversation(data);
    });

    stream.on('error', function(err) {
        console.log(err);
        $("#q").val("Error opening the STT Stream ...");
    });

    stream.on('listening', function() {
        console.log("received event listening")
        $("#q").val("I am listening ...");
    });
    $("#q").val("I am listening ...");

}

function stopWSTTService()
{
    stream.stop();
    currentTime = new Date().getTime() / 1000;

}
