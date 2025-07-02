from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    searchword = None
    if request.method == "POST":
        searchword = request.form.get("searchword")
    return render_template("index.html", searchword=searchword)

if __name__ == "__main__":
    app.run(debug=True)