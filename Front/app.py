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

if __name__ == '__main__':
   app.run("localhost", port=3000,debug=True)