from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import hashlib
from flask_socketio import SocketIO, join_room, leave_room
import os
from flask_login import login_manager
app = Flask(__name__)
app.secret_key = "etignotasanimumdimittitinartes"
socketio = SocketIO(app)

con = sqlite3.connect('chat.db')
cur = con.cursor()
cur.execute('create table if not exists user(id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE NOT NULL, senha TEXT NOT NULL)')
con.close()

@app.route('/', methods=['GET', 'POST'])
def main():
  if(request.method=="POST"):
     try:
        nome = request.form['usuario']
        with sqlite3.connect("chat.db") as con:
           cur = con.cursor()
           x = cur.execute("SELECT * from user where nome = ? ", [nome])
           if(x.fetchall()==[]):
              return render_template('index.html', msg="1", nome=nome)
           else:
              senha = request.form['senha']
              user_entered_password = senha
              salt = "gustavo000000003"
              db_password = user_entered_password+salt
              h = hashlib.md5(db_password.encode())
              x = cur.execute("SELECT * from user where senha = ? ", [h.hexdigest()])
              if(x.fetchall()==[]):
                 return render_template('index.html', msg="2", nome=nome)
              else:
                 sala = request.form['sala']
                 if(sala=="" or sala==" "):
                    return render_template('index.html', msg="3", nome=nome)

                 session['usuario'] = nome
                 session['sala'] = sala
                 return redirect('/chat')
     except:
        render_template('index.html', msg="4")
  return  render_template('index.html')

@app.route('/chat')
def chat():
   try:
      if(session['usuario']!=None):
         
         return render_template('chat.html', nome=session['usuario'], room=session['sala'])
      else:
         return redirect('/')
   except:
      return redirect('/')
   


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():

   if(request.method=="POST"):
     try:
       
       nome = request.form['usuario']
       senha = request.form['senha']
       if(nome=='' or nome == ' '):
         return render_template('cadastro.html', msg="1")
       if(senha=='' or nome == ' '):
         return render_template('cadastro.html', msg="3", nome=nome)
      
       with sqlite3.connect("chat.db") as con:
       
        cur = con.cursor()
        x = con.execute("SELECT * from user where nome = ? ", [nome])
        
        
        if(x.fetchall()==[]):
           user_entered_password = senha
           salt = "gustavo000000003"
           db_password = user_entered_password+salt
           h = hashlib.md5(db_password.encode())
           cur.execute("INSERT INTO user(nome,senha)VALUES (?,?)",(nome,h.hexdigest()) )

           con.commit()
           return redirect('/')     
        else:
           return render_template('cadastro.html', msg = "2")

     except:
       
        con.rollback()
        return render_template('cadastro.html', msg="4")
   return render_template('cadastro.html')

       
@socketio.on('unjoin')
def handle_leave_room_event(data):

   data['name']= session['usuario']
   socketio.emit('leave', data, room=data['room']);
   leave_room(data['room'])



@socketio.on('join')
def handle_message(data):
   join_room(session['sala'])
   socketio.emit('new_user', data, room=data['room'])

@socketio.on('enviar_mensagem')
def receive(data):
   socketio.emit('nova_mensagem', data, room=data['room'])





if (__name__=="__main__"):
    socketio.run(app)
