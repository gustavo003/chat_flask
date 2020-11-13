from flask import Flask, render_template, request
import sqlite3
import hashlib
app = Flask(__name__)

con = sqlite3.connect('chat.db')

con.execute('create table if not exists user(id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE NOT NULL, senha TEXT NOT NULL)')
con.close()
@app.route('/')
def main():
  return  render_template('index.html')

@app.route('/chat')
def chat():
   return render_template('chat')

@app.route('/cadastro')
def cadastro():
   return render_template('cadastro.html')

@app.route('/saveuser', methods=['POST', 'GET'])
def saveuser():
   if(request.method=="POST"):
     try:
       nome = request.form['usuario'];
       senha = request.form['senha'];
       
       user_entered_password = 'trabalhodesistemasdistribuidos'
       salt = "gustavo000000003"
       db_password = user_entered_password+salt
       h = hashlib.md5(db_password.encode())

       with sqlite3.connect("chat.db") as con:
        cur = con.cursor()

        cur.execute("INSERT INTO user(nome,senha)VALUES (?,?)",(nome,h.hexdigest()) );

        con.commit();
        return render_template('chat.html', nome=nome);
     except:
       con.rollback();
       return render_template('index.html')



if (__name__=="__main__"):
    app.run()
