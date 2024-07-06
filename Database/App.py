from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///files.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the File model
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    mimetype = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Create the database within an application context
with app.app_context():
    db.create_all()

# Endpoint to upload files
@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({"error": "No files part in the request"}), 400
    
    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No files uploaded"}), 400
    
    for file in files:
        new_file = File(name=file.filename, data=file.read(), mimetype=file.mimetype) #type:ignore
        db.session.add(new_file)
    
    db.session.commit()
    return jsonify({"message": "Files successfully uploaded and stored"}), 200

# Endpoint to list files
@app.route('/files', methods=['GET'])
def list_files():
    files = File.query.all()
    files_list = [{'id': file.id, 'name': file.name, 'mimetype': file.mimetype} for file in files]
    return jsonify(files_list)

# Endpoint to download a file
@app.route('/download/<int:file_id>', methods=['GET'])
def download_file(file_id):
    file = File.query.get(file_id)
    if file is None:
        return jsonify({'error': 'File not found'}), 404

    return send_file(
        io.BytesIO(file.data),
        download_name=file.name,
        mimetype=file.mimetype,
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(debug=True)
