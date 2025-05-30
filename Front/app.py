from flask import Flask,render_template,request,redirect,url_for

app = Flask(__name__)

@app.route('/')
def home():
   return render_template('home.html')

if __name__ == '__main__':
   app.run("localhost", port=3000,debug=True)