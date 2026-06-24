from flask import Flask , render_template , jsonify
from deep_translator import GoogleTranslator

app = Flask(__name__)

@app.route("/") #calls index function
def index():
    return render_template("index.html")

@app.route("/languages")
def get_all_supported_languages():
    #key - language name , value - language code
    name_code = GoogleTranslator().get_supported_languages(as_dict = True)
    return jsonify(name_code)





if __name__ == "__main__":
    app.run(debug = True)
