from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://homesite:oBJqg6n3yp0IItHS@cluster0.gnq7ra8.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.vote


@app.route('/voteView')
def home():
    return render_template('voteView.html')

@app.route("/voteViewData", methods=["GET"])
def homework_post():
    all_voteList = list(db.voteList.find({}, {'_id': False}))

    return jsonify({'msg':all_voteList})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)