from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html", active_page="home")


@app.route("/storage")
def storage():
    return render_template("storage.html", active_page="storage")


@app.route("/devices")
def devices():
    return render_template("device.html", active_page="devices")


@app.route("/transfers")
def transfers():
    return render_template("transfers.html", active_page="transfers")


@app.route("/network")
def network():
    return render_template("network.html", active_page="network")


@app.route("/settings")
def settings():
    return render_template("settings.html", active_page="settings")


if __name__ == "__main__":
    app.run(debug=True)
