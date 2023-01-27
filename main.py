import os
from app import app
from flask import flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
	
@app.route('/')
def upload_form():
	return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_video():
	if 'file' not in request.files:
		flash('動画がありませんでした．')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('アップロードする動画が選択されていませんでした．')
		return redirect(request.url)
	else:
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		flash('動画がアップロードされました．')
		return render_template('upload.html', filename=filename)

@app.route('/display/<filename>')
def display_video(filename):
	return redirect(url_for('static', filename='uploads/' + filename), code=301)

if __name__ == "__main__":
    app.run()
	