from flask import Flask, render_template

app = Flask(__name__)

@ app.route('/')
def homepage():
    return render_template('index.html')

@ app.route('/models')
def models():
    return render_template('models.html')

@ app.route('/methodology')
def methodology():
    return render_template('methodology.html')