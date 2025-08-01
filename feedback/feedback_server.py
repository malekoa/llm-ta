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
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Thanks for your feedback</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #74ebd5, #ACB6E5);
                color: #333;
            }
            .container {
                background: white;
                padding: 2rem 3rem;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
                animation: fadeIn 0.8s ease-in-out;
            }
            h1 {
                margin: 0 0 1rem 0;
                font-size: 2rem;
            }
            p {
                font-size: 1.2rem;
            }
            .emoji {
                font-size: 4rem;
                color: #4CAF50;
                animation: bounce 0.5s ease-in-out;
            }
            .footer {
                margin-top: 2rem;
                font-size: 0.9rem;
                color: #777;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            @keyframes bounce {
                0% { transform: scale(0.5); }
                50% { transform: scale(1.2); }
                100% { transform: scale(1); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="emoji">🎉</div>
            <h1>Thank You!</h1>
            <p>Your feedback has been successfully recorded.</p>
            <div class="footer">
                Feedback recorded for <strong>TaraBot</strong>
            </div>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)