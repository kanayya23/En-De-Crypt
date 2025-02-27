import os
from flask import Flask, request, render_template, flash,redirect, send_file, url_for, session
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet, InvalidToken
from zipfile import ZipFile
import shutil
import secrets


app = Flask(__name__, static_folder='static')
app.secret_key = secrets.token_hex(16)
app.config['uf'] = os.path.join(app.root_path, 'uploads')
app.config['df'] = os.path.join(app.root_path, 'downloads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

if not os.path.exists(app.config['uf']):
    os.makedirs(app.config['uf'])

if not os.path.exists(app.config['df']):
    os.makedirs(app.config['df'])

def generate_key():
    key = Fernet.generate_key()
    with open('secret.key', 'wb') as key_file:
        key_file.write(key)

def load_key(key_path):
    return open(key_path, 'rb').read()

@app.route('/')
def index():
    return render_template('index.html', decrypted_text=None, encrypted_text=None)

@app.route('/encrypt', methods=['POST'])
def encrypt_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        return "No file uploaded"
    file = request.files['file']
    if file.filename == '':
        return "No file selected"
    # Check if the file type is allowed
    if file and allowed_file(file.filename):
        # Secure the filename
        filename = secure_filename(file.filename)
        # Save the file to the upload folder
        filepath = os.path.join(app.config['uf'], filename)
        file.save(filepath)
        # Generate a new encryption key and save it to a file named 'key.key'
        key = Fernet.generate_key()
        with open('key.key', 'wb') as key_file:
            key_file.write(key)
        # Create a Fernet instance with the generated key
        fernet = Fernet(key)
        # Read the contents of the original file
        with open(filepath, 'rb') as original_file:
            original = original_file.read()
        # Encrypt the file contents
        encrypted = fernet.encrypt(original)
        # Save the encrypted file to a file named after the original file
        with open(filename, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)
        # Create a zip file containing the encrypted file and the encryption key
        filen = filename.split(".")[0]    
        zip_path = os.path.join(app.config['uf'], filen + '.zip')
        with ZipFile(zip_path, 'w') as zip_file:
            zip_file.write(filename)
            zip_file.write('key.key')
        zip_file.close()

        # Remove the original file, the encrypted file, and the encryption key
        os.remove(filename)
        os.remove(filepath)
        os.remove('key.key')

        # Send the decrypted file to the user
        response = send_file(zip_path, as_attachment=True)
        
        return response
    else:
        # If the file type is not allowed, redirect to the home page
        return render_template('index.html')


@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt_file():
    if request.method == 'POST':
        if 'file' not in request.files or 'key' not in request.files:
            return "No file uploaded"

        file = request.files['file']
        key = request.files['key']
        if file.filename == '' or key.filename == '':
            return "No file selected"
        
        # Save the files to disk
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['uf'], filename))
        keyname = secure_filename(key.filename)
        key.save(os.path.join(app.config['uf'], keyname))
        
        # Decrypt the file
        input_path = os.path.join(app.config['uf'], filename)
        key_path = os.path.join(app.config['uf'], keyname)
        output_path = os.path.join(app.config['df'], filename)
        key = load_key(key_path)
        fernet = Fernet(key)
        with open(input_path, 'rb') as encrypted_file:
            encrypted = encrypted_file.read()
        decrypted = fernet.decrypt(encrypted)
        with open(output_path, 'wb') as decrypted_file:
            decrypted_file.write(decrypted)

        os.remove(input_path)
        os.remove(key_path)
        # Send the decrypted file to the user
        return send_file(output_path, as_attachment=True)
    else:
        return render_template('decrypt.html')
    
@app.route('/text-encryption', methods=['GET', 'POST'])
def text_encryption():
    if request.method == 'POST':
        text = bytes(request.form.get('en-text'), 'utf-8')
        # perform encryption on the text here and get the encrypted text and key
        key = Fernet.generate_key()
        f=Fernet(key)
        encrypted_text = f.encrypt(text).decode()
        key=key.decode()
        return render_template('index.html', encrypted_text=encrypted_text, key=key, text=text)
    return render_template('index.html')

@app.route('/decrypt_text',  methods=['GET', 'POST'])
def decrypt_text():
    if request.method == 'POST':
        text = bytes(request.form.get('en-text'), 'utf-8')
        key = request.form.get('key')
        # perform decryption
        try:
            f=Fernet(key)
            decrypted_text = f.decrypt(text).decode()
        except:
            decrypted_text = "Incorrect Input: check your text and key!!"
        return render_template('index.html', decrypted_text=decrypted_text)
    return render_template('index.html')

@app.route('/clear_flask_vars', methods=['POST'])
def clear_flask_vars():
    session.clear()  # clear all session variables
    return redirect(url_for('index', _anchor='textdecryp'))

@app.route('/clear')
def clear():
    
    # Clear uploads folder
    for filename in os.listdir(app.config['uf']):
        file_path = os.path.join(app.config['uf'], filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    
    # Clear downloads folder
    for filename in os.listdir(app.config['df']):
        file_path = os.path.join(app.config['df'], filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    
    flash('Folders cleared successfully', 'success')
    return redirect(url_for('index'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'}

if __name__ == '__main__':
    app.run(debug=True)
