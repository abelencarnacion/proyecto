import base64
import hashlib
from flask import Flask,request, redirect, render_template, session
import redis
import pyodbc

import threading

semaphore = threading.Semaphore()

# app = Flask(__name__)

# # Creamos una conexión a Redis
r = redis.Redis(host='localhost', port=6379, db=0)

app = Flask(__name__)
app.secret_key = 'mysecretkey'

@app.route('/subscribe')
def subscribe():
    # Suscribimos el cliente a un canal
    pubsub = r.pubsub()
    pubsub.subscribe('joerlyn')

    # Iteramos sobre los mensajes del canal
    for message in pubsub.listen():
         if message and message.get('data') and message['data']!=1:
                return message['data'].decode('utf')
         print("esperando mensaje")     

# Creamos una conexión a la base de datos
# Configura la cadena de conexión
connection_string = "Driver=SQL Server;Server=.\SQLEXPRESS;Database=students;Trusted_Connection=yes;"     

# Creamos la tabla de usuarios si no existe
conn = pyodbc.connect(connection_string)




# Función para verificar si un usuario existe en la base de datos
def user_exists(username, password):  
  try:  
    conn = pyodbc.connect(connection_string)  
    cursor = conn.cursor()
   # cursor.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'")
    cursor.execute(f"SELECT * FROM users WHERE username=? and password=?",(username,password))
    results = cursor.fetchall()
  finally:
    # Cierra el cursor y la conexión
    cursor.close()
    conn.close()
  return results

# Función para agregar un usuario a la base de datos
def add_user(username, password):
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    try:  
        cursor.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')")
        conn.commit()
    finally:
        cursor.close()
        conn.close()
@app.route('/')
def home():
    # Verificamos si el usuario está autenticado
    if 'username' in session:
        return render_template('index.html')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ## Verificamos si el usuario existe en la base de datos
        if False:
            session['username'] = request.form['username']
            return redirect('/')
        else:
            return render_template('login.html', error='Usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/hmac', methods=['GET', 'POST'])
def hmac():
    message = "Hello, world!".encode("utf-8")
    m = hashlib.sha256()
    m.update(message)
    hash_result = m.digest()
    print(base64.b64encode(hash_result))
    result= base64.b64encode(hash_result)
    return result

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Agregamos el usuario a la base de datos
        add_user(request.form['username'], request.form['password'])
        return redirect('/login')
    return render_template('register.html')

@app.route('/logout')
def logout():
    # Borramos el usuario de la sesión
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(None,5000,True)
