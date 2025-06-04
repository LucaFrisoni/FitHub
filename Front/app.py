from flask import Flask,render_template,request,redirect,url_for

app = Flask(__name__)

@app.route('/')
def home():
   return render_template('home.html')

@app.route('/planes')
def planes():
   return render_template('planes.html')

@app.route('/reservas')
def reservas():
   return render_template('reservas.html')

@app.route('/tienda')
def tienda():
   return render_template('tienda.html')

@app.route('/user')
def user():
   return render_template('user.html')
# ----------------------Auth----------------------
@app.route('/login')
def login():
   return render_template('auth/login.html')

@app.route('/registro')
def registro():
   return render_template('auth/registro.html')

@app.route('/cambiarcontra')
def cambiarcontra():
   return render_template('auth/cambiar_contra.html')


if __name__ == '__main__':
   app.run("localhost", port=3000,debug=True)