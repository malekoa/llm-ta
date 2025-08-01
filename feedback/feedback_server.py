import sys, os
from dotenv import load_dotenv
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from bot.database import Database
from flask import Flask, request

load_dotenv()

app = Flask(__name__)

@app.route("/feedback")
def feedback():
    vote = request.args.get("vote")
    message_id = request.args.get("message_id")

    if vote not in ("up", "down") or not message_id:
        return "Invalid parameters", 400

    with Database() as db:
        db.add_vote(message_id, vote)

    return """
    <html>
        <head><title>Thanks</title></head>
        <body>
            <h3>Thanks for your feedback!</h3>
            <p>Your response has been recorded.</p>
        </body>
    </html>
    """

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)