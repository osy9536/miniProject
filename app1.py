from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

from pymongo import MongoClient
import certifi

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.mih9efs.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)
db = client.dbsparta


@app.route('/')
def home():
    return render_template('comment.html')


@app.route("/comment", methods=["POST"])
def web_comments_post():
    name_receive = request.form['name_give']
    comment_receive = request.form['comment_give']

    doc = {
       'name':name_receive,
        'comment':comment_receive
    }
    db.comments.insert_one(doc)

    return jsonify({'msg': '등록 완료!'})


@app.route("/comment", methods=["GET"])
def web_comments_get():
    order_list = list(db.comments.find({}, {'_id': False}))
    return jsonify({'comments': order_list})


@app.route("/comment/comments_list", methods=["GET"])
def posting_comments_list_get():
    comments_list = list(db.comments.find({}, {'_id': False}))
    return jsonify({'comments': comments_list})


@app.route("/comment/delete", methods=["POST"])
def comment_delete():
    name_list = request.form['name_give']

    db.comments.delete_one({"name": name_list})
    return jsonify({'msg': '삭제되었습니다!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
