# Audio Downloader App

This Flask app allows users to download the audio from a YouTube video and generate college-level notes for the video's content. The app uses the OpenAI API to generate the notes and the yt-dlp library to download the audio.

## Installation

1. Clone this repository: `git clone https://github.com/<username>/audio-downloader-app.git`
2. Change into the project directory: `cd audio-downloader-app`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment:
    - Windows: `venv\Scripts\activate`
    - Unix/Mac: `source venv/bin/activate`
5. Install the required packages: `pip install -r requirements.txt`

## Usage

1. Run the app: `python app.py`
2. Open a web browser and go to `http://localhost:5000`
3. Enter the URL of the YouTube video you want to download and click the "Get Notes" button.
4. The app will download the audio and generate college-level notes for the video's content.
5. The notes will be displayed on the /notes page.

## Credits

This app was created by <your_name>. It uses the following libraries:

- Flask (https://flask.palletsprojects.com/)
- OpenAI API (https://beta.openai.com/)
- yt-dlp (https://github.com/yt-dlp/yt-dlp)
- pafy (https://github.com/mps-youtube/pafy)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
