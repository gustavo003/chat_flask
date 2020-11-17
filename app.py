from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import hashlib
from flask_socketio import SocketIO, join_room, leave_room
import os
from flask_login import LoginManager, login_user, UserMixin, login_required, logout_user, current_user
from flask_session import Session

app = Flask(__name__)
app.secret_key = "etignotasanimumdimittitinartes"
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
socketio = SocketIO(app, manage_session=False)

con = sqlite3.connect('chat.db')
cur = con.cursor()
cur.execute('create table if not exists user(id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE NOT NULL, senha TEXT NOT NULL)')
con.close()

class User(UserMixin):
    pass

lm = LoginManager(app)

@lm.user_loader
def user_loader(nome):
   user = User()
   user.id = nome;

   return user


@property
def is_authenticated(self):
   return True

@property
def is_anonymous(self):
   return False

@lm.unauthorized_handler
def unauthorized():
    return redirect('/')


def query_db(query, args=(), one=False):
    db = sqlite3.connect('chat.db')
    print(query);
    print(args)
    cur = db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/', methods=['GET', 'POST'])
def main():
  if(request.method=="POST"):
     try:
        nome = request.form['usuario']
        x = query_db("SELECT * from user where nome = ? ", [nome])
        if(x==[]):
           return render_template('index.html', msg="1", nome=nome)
        else:
          
           senha = request.form['senha']
           user_entered_password = senha
           salt = "gustavo000000003"
           db_password = user_entered_password+salt
           h = hashlib.md5(db_password.encode())
         
           if(x[0][2]!=h.hexdigest()):    
              return render_template('index.html', msg="2", nome=nome)
           sala = request.form['sala']
           if(sala=="" or sala==" "):
              return render_template('index.html', msg="3", nome=nome)
           session['sala'] = sala
           session['nome'] = nome
           user = User()
           user.id=nome
           login_user(user)
           return redirect('/chat')
     except:
        render_template('index.html', msg="4")
  return  render_template('index.html')

@app.route('/chat')
@login_required
def chat():      
   return render_template('chat.html', nome=current_user.id, room=session['sala'])
   

   


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
   if(request.method=="POST"):
      try:
         nome = request.form['usuario']
         senha = request.form['senha']
         if(not nome or nome==" "):
            return render_template('cadastro.html', msg="1")
         if(not senha or senha==" "):
            return render_template('cadastro.html', msg="3", nome=nome)

         x = query_db("SELECT * from user where nome = ? ", [nome])
         if(x==[]):
            user_entered_password = senha
            salt = "gustavo000000003"
            db_password = user_entered_password+salt
            h = hashlib.md5(db_password.encode())
            db = sqlite3.connect('chat.db')
            cursor = db.cursor()
            cursor.execute("INSERT INTO user(nome,senha)VALUES (?,?) ", (nome, h.hexdigest()))
            db.commit()
            return redirect('/')     
         else:
            return render_template('cadastro.html', msg = "2")
      except:
         return render_template('cadastro.html', msg="4")
   return render_template('cadastro.html')

       
@socketio.on('unjoin')
def handle_leave_room_event(data):
   data['name'] = session['nome']
 
   socketio.emit('leave', data, room = data['room'])
   if(data['name']==data['nome']):
      print(data['nome'])
      logout_user()
      leave_room(data['room'])
    
   
   



@socketio.on('join')
def handle_message(data):
   join_room(session['sala'])
   socketio.emit('new_user', data, room=data['room'])

@socketio.on('enviar_mensagem')
def receive(data):
   socketio.emit('nova_mensagem', data, room=data['room'])





if (__name__=="__main__"):
    port = int(os.environ.get("PORT", 5000))
    socketio.run(host='0.0.0.0', port=port)
