from flask import Flask, render_template, request

app = Flask(__name__)

orders = ["新しい順", "古い順"]
notes = [
    {"ノート1", "2000-01-01"},
    {"ノート2", "2000-01-01"},
    {"ノート3", "2000-01-01"}
]
print(len(notes))

@app.route("/", methods=["GET", "POST"])
def index():
    searchword = ""
    if request.method == "POST":
        searchword = request.form.get("searchword")
    return render_template("index.html", searchword=searchword, orders=orders, notes=notes, len=len(notes))

@app.route("/note")
def hello_world():
    return render_template("note.html")


if __name__ == "__main__":
    app.run(debug=True)