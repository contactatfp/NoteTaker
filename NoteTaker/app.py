import os
from flask import Flask, request, jsonify, render_template
import openai, json
import yt_dlp

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
    thePath = os.path.join('audio', file_name)

    # Download the video using yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': thePath + '.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav'
        }],
        'extractaudio': True,
        'audioformat': 'wav',
        'noplaylist': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        transcribe(thePath + '.wav')

    return jsonify({'message': 'Audio saved successfully.'})


# @app.route('/transcribe', methods=['POST'])
# def transcribe(file_path):
#     # Read the saved audio file from disk
#     with open(file_path, 'rb') as f:
#         audio_file = f.read()
#
#     # Use the OpenAI API to transcribe the audio file
#     transcription_request = openai.Audio.TranscriptionRequest(
#         file=audio_file,
#         model="whisper-1"
#     )
#     transcription_response = openai.Audio.transcribe(
#         transcription_request.model,
#         transcription_request.file,
#         prompt=transcription_request.prompt,
#         response_format=transcription_request.response_format,
#         temperature=transcription_request.temperature,
#         language=transcription_request.language
#     )
#     transcription_text = transcription_response['text']
#
#     # Save the transcription as a text file
#     text_file_name = os.path.splitext(file_path)[0] + '.txt'
#     with open(text_file_name, 'w') as f:
#         f.write(transcription_text)
#
#     mytext = jsonify({'text': transcription_text})
#     print(mytext['text'])
#
#     # Return the transcription as JSON
#     return jsonify({'text': transcription_text})
@app.route('/split-audio', methods=['POST'])
def split_audio(file):

    max_size = 25 * 1024 * 1024
    output_dir = os.path.join(os.path.dirname(__file__), 'audio', 'split_files')

    def split_file(file):
        file_number = 1
        while True:
            # Read up to max_size bytes from the file
            data = file.read(max_size)
            if not data:
                break

            # Write the data to a new file in the output directory
            filename = os.path.join(output_dir, f"file{file_number}.wav")
            with open(filename, 'wb') as f:
                f.write(data)

            file_number += 1

        return file_number - 1

    num_files = split_file(file)
    return f"File was split into {num_files} files and stored in {output_dir}."


@app.route('/transcribe', methods=['POST'])
def transcribe(file_path):
    audio_file = open(file_path, "rb")
    file_size = os.path.getsize(file_path)
    # if audio_file is bigger than 25MB, split into multiple files inside their own folder
    # if file_size > 25 * 1024 * 1024:
    #     split_audio(audio_file)

    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    print(transcript['text'])

    return jsonify({'text': transcript})


if __name__ == '__main__':
    app.run(debug=True)
