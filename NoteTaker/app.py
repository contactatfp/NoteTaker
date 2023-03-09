import os
import urllib.request
from flask import Flask, request, jsonify, render_template
import openai, json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Load the OpenAI API key from the config file
with open('config.json') as f:
    config = json.load(f)
openai.api_key = config['OPENAI_API_KEY']


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/download_audio', methods=['POST'])
def download_audio():
    if request.headers['Content-Type'] != 'application/json':
        return jsonify({'error': 'Invalid Content-Type'}), 400
    url = request.json['url']
    file_name = os.path.basename(url)
    audio_file = urllib.request.urlopen(url).read()
    thePath = os.path.join('audio', file_name)

    with open(thePath, 'wb') as f:
        f.write(audio_file)

    # transcribe(os.path.join('audio', file_name))
    return jsonify({'message': 'Audio saved successfully.'})


@app.route('/transcribe', methods=['POST'])
def transcribe(file):
    # Read the saved audio file from disk
    file_name = request.json[file]
    file_path = file_name
    with open(file_path, 'rb') as f:
        audio_file = f.read()

    # Use the OpenAI API to transcribe the audio file
    transcription_request = openai.Audio.TranscriptionRequest(
        file=audio_file,
        model="whisper-1"
    )
    transcription_response = openai.Audio.transcribe(
        transcription_request.model,
        transcription_request.file,
        prompt=transcription_request.prompt,
        response_format=transcription_request.response_format,
        temperature=transcription_request.temperature,
        language=transcription_request.language
    )
    transcription_text = transcription_response['text']

    # Save the transcription as a text file
    text_file_name = os.path.splitext(file_path)[0] + '.txt'
    with open(text_file_name, 'w') as f:
        f.write(transcription_text)

    mytext = jsonify({'text': transcription_text})
    print(mytext['text'])

    # Return the transcription as JSON
    return jsonify({'text': transcription_text})


if __name__ == '__main__':
    app.run(debug=True)
