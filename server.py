from flask import Flask, request,jsonify
# from flask_cors import CORS

app = Flask(__name__)
# CORS(app)
# 
@app.route("/hi", methods=["GET"])
def webhook():
    # Get the TradingView signal data from the request body
    signal_data = request.get_json()

    # Do something with the signal data, such as:
    # - Send a notification to a chat room
    # - Execute a trade
    # - Store the data in a database

    return jsonify({"message": "Test result processing has been started."}), 202

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000,debug=False, use_reloader=False)