from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to Quiz Master API. You know which route to hit, if you are authorised :)"

if __name__ == "__main__":
   app.run(port=5000, debug=True) 
