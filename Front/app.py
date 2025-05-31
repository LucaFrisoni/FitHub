from flask import Flask,render_template,request,redirect,url_for

app = Flask(__name__)

@app.route('/')
def home():
   return render_template('home.html')

@app.route('/Reservas')
def reserva():
   return render_template('reservas.html')

if __name__ == '__main__':
   app.run("localhost", port=3000)