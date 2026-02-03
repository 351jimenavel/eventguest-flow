from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def check_health():
    return jsonify({"message":"Ok"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=6789)