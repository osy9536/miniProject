import jwt, datetime, hashlib, certifi
from flask import Flask, render_template, request, jsonify, url_for, redirect

app = Flask(__name__)

from pymongo import MongoClient
from datetime import datetime, timedelta

client = MongoClient('mongodb+srv://test:sparta@cluster0.6bemlvq.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta

@app.route("/votingPost",methods=["POST"])
def voting():
    left_name_receive = db.users.find_one({'name' : payload})
    voting_title_receive = request.form['voting_title_give']
    voting1_body_receive = request.form['voting1_body_give']
    voting2_body_receive = request.form['voting2_body_give']

    name
    doc = {'name_2' : left_name_receive ,'title':voting_title_receive, 'voting1':voting1_body_receive, 'voting':voting2_body_receive }
    db.users.insert_one(doc)

    return jsonify({'msg': '투표글 작성 완료'})



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)