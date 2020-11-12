from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def main():
  return  render_template('index.html')

@app.route('/chat')
def chat():
   return render_template('chat')

if (__name__=="__main__"):
    app.run()
