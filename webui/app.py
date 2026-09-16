from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/storage")
def storage():
    return render_template("storage.html")

@app.route("/devices")
def devices():
    return render_template("device.html")

@app.route("/transfers")
def transfers():
    return render_template("transfers.html")

@app.route("/network")
def network():
    return render_template("network.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

if __name__ == "__main__":
    app.run(debug=True)