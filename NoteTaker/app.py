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
            'preferredcodec': 'mp3',
            'preferredquality': '96'
        }],
        'extractaudio': True,
        'audioformat': 'mp3',
        'noplaylist': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    split_mp3_file(thePath + '.mp3')

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
def split_mp3_file(filepath):
    # Check if file exists
    if not os.path.isfile(filepath):
        raise ValueError(f"{filepath} is not a file.")

    # Get the file size in bytes
    file_size = os.path.getsize(filepath)

    # Check if file size is greater than 25 MB
    if file_size > 25 * 1024 * 1024:
        # Calculate the number of chunks to split the file into
        num_chunks = (file_size // (25 * 1024 * 1024)) + 1

        # Calculate the size of each chunk
        chunk_size = file_size // num_chunks

        # Open the input file
        with open(filepath, 'rb') as f:
            # Read and write each chunk to a new file
            for i in range(num_chunks):
                # Generate the filename for the new chunk
                filename = f"{os.path.splitext(filepath)[0]}_{i+1}.mp3"

                # Open the new file for writing
                with open(filename, 'wb') as chunk_file:
                    # Write the chunk to the new file
                    chunk_data = f.read(chunk_size)
                    chunk_file.write(chunk_data)
                    transcribe(filename)
    else:
        print(f"{filepath} is already under 25 MB.")
        transcribe(filepath)


@app.route('/transcribe', methods=['POST'])
def transcribe(file_path):
    audio_file = open(file_path, "rb")
    # if audio_file is bigger than 25MB, split into multiple files inside their own folder
    # if file_size > 25 * 1024 * 1024:
    #     split_audio(audio_file)

    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    print(transcript['text'])

    return jsonify({'text': transcript})


if __name__ == '__main__':
    app.run(debug=True)
