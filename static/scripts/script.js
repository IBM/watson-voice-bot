let conversationContext = '';
let tokenSTT;
let tokenTTS;
let stream;
let currentTime = 0;

function displayMsgDiv(str, who) {
  const time = new Date();
  let hours = time.getHours();
  let minutes = time.getMinutes();
  const ampm = hours >= 12 ? 'pm' : 'am';
  hours = hours % 12;
  hours = hours ? hours : 12; // the hour "0" should be "12"
  hours = hours < 10 ? '0' + hours : hours;
  minutes = minutes < 10 ? '0' + minutes : minutes;
  const strTime = hours + ':' + minutes + ' ' + ampm;
  let msgHtml = "<div class='msg-card-wide mdl-card " + who + "'><div class='mdl-card__supporting-text'>";
  msgHtml += str;
  msgHtml += "</div><div class='" + who + "-line'>" + strTime + '</div></div>';

  $('#messages').append(msgHtml);
  $('#messages').scrollTop($('#messages')[0].scrollHeight);

  if (who == 'user') {
    $('#q').val('');
    $('#q').attr('disabled', 'disabled');
    $('#p2').fadeTo(500, 1);
  } else {
    $('#q').removeAttr('disabled');
    $('#p2').fadeTo(500, 0);
  }
}

$(document).ready(function() {
  $('#q').attr('disabled', 'disabled');
  $('#p2').fadeTo(500, 1);
  $('#h').val('0');

  $.ajax({
    url: '/api/conversation',
    convText: '',
    context: ''
  })
    .done(function(res) {
      conversationContext = res.results.context;
      displayMsgDiv(res.results.responseText, 'bot');
      play(res.results.responseText);
    })
    .fail(function(jqXHR, e) {
      console.log('Error: ' + jqXHR.responseText);
    })
    .catch(function(error) {
      console.log(error);
    });

  $('#q').keyup(function(e) {
    $('#submit').removeAttr('disabled');
    return false;
  });

  $('#submit').click(function() {
    const text = $('#q').val();
    displayMsgDiv(text, 'user');

    $.post('/api/conversation', {
      convText: text,
      context: JSON.stringify(conversationContext)
    })
      .done(function(res, status) {
        conversationContext = res.results.context;
        // eslint-disable-next-line no-undef
        stream = WatsonSpeech.TextToSpeech.synthesize({
          token: tokenTTS,
          text: res.results.responseText
        });
        displayMsgDiv(res.results.responseText, 'bot');
      })
      .fail(function(jqXHR, e) {
        console.log('Error: ' + jqXHR.responseText);
      });

    return false;
  });
});

// setting speech to text function
window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition || null;
if (window.SpeechRecognition != null) {
  const recognizer = new window.SpeechRecognition();
  const transcription = document.getElementById('q');

  // Start recognising
  recognizer.onresult = function(event) {
    transcription.textContent = '';
    // $("#chat_input").val("I am listening ...");
    for (let i = event.resultIndex; i < event.results.length; i++) {
      if (event.results[i].isFinal) {
        transcription.textContent = event.results[i][0].transcript; // + " (Confidence: " + event.results[i][0].confidence + ")"
      } else {
        transcription.textContent += event.results[i][0].transcript;
      }
    }

    document.getElementById('2').src = './static/img/mic.gif';
    $('#q').val();
    // $("#q").focus();
  };

  // Listen for errors
  recognizer.onerror = function(event) {
    console.log('Recognition error: ' + event.message + '<br />');
    document.getElementById('stt2').src = './static/img/mic.gif';
    $('#q').val('');
  };

  recognizer.onend = function(event) {
    document.getElementById('stt2').src = './static/img/mic.gif';
    // $("#q").val("");
  };
} else {
  // $("#stt2").hide();
}

function startRecording() {
  // recorder = new Recorder(input);
  // recorder.record();
  startWSTTService();
}

function stopRecording() {
  stopWSTTService();
}

// changing the mic icon depedening upon its name. Also disabling the speech recognizer in this case
$('#stt2').click(function() {
  const fullPath = document.getElementById('stt2').src;
  const filename = fullPath.replace(/^.*[\\/]/, '');
  if (filename == 'mic.gif') {
    try {
      document.getElementById('stt2').src = './static/img/mic_active.png';
      startRecording();
    } catch (ex) {
      // console.log("Recognizer error .....");
    }
  } else {
    stopRecording();
    $('#q').val('');
    document.getElementById('stt2').src = './static/img/mic.gif';
  }
});

function callConversation(res) {
  $('#q').attr('disabled', 'disabled');

  $.post('/api/conversation', {
    convText: res,
    context: JSON.stringify(conversationContext)
  })
    .done(function(res, status) {
      conversationContext = res.results.context;
      // eslint-disable-next-line no-undef
      stream = WatsonSpeech.TextToSpeech.synthesize({
        token: tokenTTS,
        text: res.results.responseText
      });

      displayMsgDiv(res.results.responseText, 'bot');
    })
    .fail(function(jqXHR, e) {
      console.log('Error: ' + jqXHR.responseText);
    });
}

function startWSTTService() {
  // eslint-disable-next-line no-undef
  stream = WatsonSpeech.SpeechToText.recognizeMicrophone({
    token: tokenSTT,
    object_mode: false,
    model: 'en-US_NarrowbandModel',
    keepMicrophone: true,
    max_alternatives: 0,
    // keywords_threshold: 1,
    interim_results: false
  });

  stream.setEncoding('utf8'); // get text instead of Buffers for on data events

  stream.on('data', function(data) {
    console.log('Time Taken by STT:' + (new Date().getTime() / 1000 - currentTime));
    displayMsgDiv(data, 'bot');
    callConversation(data);
  });

  stream.on('error', function(err) {
    console.log(err);
    $('#q').val('Error opening the STT Stream ...');
  });

  stream.on('listening', function() {
    console.log('received event listening');
    $('#q').val('I am listening ...');
  });
  $('#q').val('I am listening ...');
}

function stopWSTTService() {
  stream.stop();
  currentTime = new Date().getTime() / 1000;
}

/*
function getAudio(response) {  
  const audio = document.createElement('audio');
  audio.crossOrigin = 'anonymous';
  audio.src = options.res;
  audio.play();  
}
*/

function play(inputText) {
  const context = new (window.AudioContext || window.webkitAudioContext)();
  let buf;

  // $.post('/api/text-to-speech', {
  //   text: inputText
  // }).then(function(response) {
  //   // const byteCharacters = atob(response);
  //   // console.log('byte Chars: ' + byteCharacters);
  //   const arrayBuffer = new ArrayBuffer(response.length);
  //   const bufferView = new Uint8Array(arrayBuffer);
  //   for (let i = 0; i < response.length; i++) {
  //     arrayBuffer[i] = response[i];
  //   }

  //   // console.log('buffer view: ' + arrayBuffer);
  //   context.decodeAudioData(
  //     arrayBuffer,
  //     function(buffer) {
  //       buf = buffer;
  //       play();
  //     },
  //     function(error) {
  //       console.error('decodeAudioData error', error);
  //     }
  //   );
  // });
  const url = '/api/text-to-speech';
  const params = 'text=' + inputText;
  const request = new XMLHttpRequest();
  request.open('GET', url, true);
  request.responseType = 'arraybuffer';

  // Decode asynchronously
  request.onload = function() {
    context.decodeAudioData(
      request.response,
      function(buffer) {
        buf = buffer;
        play();
      },
      function(error) {
        console.error('decodeAudioData error', error);
      }
    );
  };
  request.send(params);

  // Play the loaded file
  function play() {
    // Create a source node from the buffer
    const source = context.createBufferSource();
    console.log('buffer::: ' + buf);
    source.buffer = buf;
    // Connect to the final output node (the speakers)
    source.connect(context.destination);
    // Play immediately
    source.start(0);
  }
}
