from flask import Flask, render_template, request, url_for, jsonify, send_file, after_this_request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from youtubesearchpython import VideosSearch

from yt_dlp import *
import os

class QueryForm(FlaskForm):
    query = StringField(validators=[DataRequired('Enter a song name'), Length(min=3)])
    submit = SubmitField('Search')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Cygnuxxs'


@app.route('/', methods = ['GET', 'POST'])
def index():
    form = QueryForm()
    return render_template('home.html', form = form)

@app.route('/search', methods = ['GET', 'POST'])
def search_and_get():
    query = request.args.get('inputString')
    queried_results = VideosSearch(query).result()
    results = []
    if queried_results['result'] == []:
        return jsonify(results)
    for result in queried_results['result']:
        results.append({
            'title' : result['title'],
            'publish_date' : result['publishedTime'],
            'thumbnail_url' : result['thumbnails'][0]['url'],
            'artist' : result['channel']['name'],
            'views' : int(result['viewCount']['text'].replace(',','').split()[0]) if result['viewCount']['text'] != None else "NA",
            'description' : ''.join([] if result['descriptionSnippet'] == None else [i['text'] for i in result['descriptionSnippet']]),
            'youtube_url' : result['link'],
            'id' : result['id'],
        })
    
    return jsonify(results)

@app.route('/download', methods = ['GET', 'POST'])
def download():
    videoID = request.args.get('videoID')
    title = request.args.get('title')
    bitrate = request.args.get('bitrate')
    url = f'https://www.youtube.com/watch?v={videoID}'

    ydl_options = {
        'format' : 'bestaudio/best',
        'postprocessors' : [{
            'key' : 'FFmpegExtractAudio',
            'preferredcodec' : 'mp3',
            'preferredquality' : bitrate.replace('Kbps', ''),
        }],
        'outtmpl' : videoID + '.%(ext)s',
    }
    with YoutubeDL(ydl_options) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        title = info_dict.get('title')
    response = {
        'videoID' : videoID,
        'title' : title,
        'bitrate' : bitrate,
    }
    return jsonify(response)


@app.route('/downloadSong/<videoID>/<path:title>/<bitrate>', methods = ['GET', 'POST'])
def pushSong(videoID, title, bitrate):
    @after_this_request
    def remove_file(response):
        os.remove(f'{videoID}.mp3')
        return response

    return send_file(f'{videoID}.mp3', as_attachment=True, download_name=f'{title}({bitrate}).mp3')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
 