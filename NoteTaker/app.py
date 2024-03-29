import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
import openai, json
import yt_dlp
from urllib.parse import urlparse, parse_qs
import re
import pafy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Load the OpenAI API key from the config file
with open('config.json') as f:
    config = json.load(f)
openai.api_key = config['OPENAI_API_KEY']

generated_notes = ""
video_id = ""


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/loading')
def loading():
    return render_template('loading.html')


def generate_college_level_notes(text):
    prompt = f"summarize these as college level notes with video time stamps and youtube time urls for where the note corresponds with video. the timestamp and urls should be inline with each note. make sure to break into multiple notes for different sections. {text}"
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    test = completion.choices[0].message
    print(completion.choices[0].message)

    return test


def process_notes(api_response, video_id):
    notes = []
    content = api_response['content']
    sections = content.strip().split('\n\n')

    for section in sections:
        text = section.strip()
        timestamp = re.search(r'(\d{1,2}:\d{2}-\d{1,2}:\d{2})', text)

        if timestamp:
            timestamp_range = timestamp.group(1)
            start_time = timestamp_range.split('-')[0]
            start_time_seconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(start_time.split(":"))))
            text = re.sub(r'\d{1,2}:\d{2}-\d{1,2}:\d{2}', '', text).strip()
            youtube_url = f"https://www.youtube.com/watch?v={video_id}&t={start_time_seconds}s"
        else:
            timestamp_range = ''
            start_time_seconds = ''
            youtube_url = ''

        notes.append({
            'text': f"{timestamp_range} - {text}",
            'timestamp': timestamp_range,
            'url': youtube_url
        })

    return notes


# Modify the /notes route to use the global variable for the college_level_notes
@app.route('/notes', methods=['GET'])
def notes():
    college_level_notes = process_notes(generated_notes, video_id)
    return render_template('notes.html', notes=college_level_notes)


@app.route('/download_audio', methods=['POST'])
def download_audio():
    global video_id
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
    parsed_url = urlparse(url)
    video_id = parse_qs(parsed_url.query)["v"][0]
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    split_mp3_file(thePath + '.mp3')

    return jsonify({'message': 'Audio saved successfully.'})


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
                filename = f"{os.path.splitext(filepath)[0]}_{i + 1}.mp3"

                # Open the new file for writing
                with open(filename, 'wb') as chunk_file:
                    # Write the chunk to the new file
                    chunk_data = f.read(chunk_size)
                    chunk_file.write(chunk_data)
                    transcribe(filename)
    else:
        print(f"{filepath} is already under 25 MB.")
        transcribe(filepath)

    return redirect(url_for('notes'))


# Modify the transcribe route to store the generated notes in the global variable and redirect to the /notes route
@app.route('/transcribe', methods=['POST'])
def transcribe(file_path):
    global generated_notes
    audio_file = open(file_path, "rb")

    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    print(transcript['text'])
    test = generate_college_level_notes(transcript['text'])
    generated_notes = test  # Store the generated notes in the global variable

    return redirect(url_for('notes'))  # Redirect to the /notes route


if __name__ == '__main__':
    app.run(debug=True)
