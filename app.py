import certifi
import datetime
import hashlib
import jwt
from flask import Flask, render_template, request, jsonify, url_for, redirect

app = Flask(__name__)

from pymongo import MongoClient
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

client = MongoClient(
    'mongodb+srv://osy9536:~tpdud434861@cluster0.u6oggvp.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbvote

##### 로그인
SECRET_KEY = 'SPARTA'


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"id": payload['id']})
        return render_template('login.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for('login', msg='로그인 시간이 만료되었습니다.'))
    except jwt.exceptions.DecodeError:
        return redirect(url_for('login', msg='로그인 정보가 존재하지 않습니다.'))


@app.route('/login')
def login():
    msg = request.args.get('msg')
    return render_template('login.html', msg=msg)


# 로그인 기능
# id,pw를 클라이언트에게 받아와 pw를 해쉬인코딩 하여 암호화한다.
# id와 암호화한 pw를 mongoDB에 있는지 확인하고, 없을시에는 result = None
# 클라이언트에게 받은 id와 pw가 mongoDB와 일치할 시 token을 생성한다.
# 클라이언트에게 토큰을 전송한다.
@app.route("/api/sign_in", methods=["POST"])
def sign_in():
    email_receive = request.form['email_give']
    password_receive = request.form['pw_give']
    # pw를 암호화합니다.
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # 해당 유저를 찾습니다.
    result = db.users.find_one({'email': email_receive, 'password': pw_hash})
    # 찾으면 토큰을 만들어 발급합니다.
    if result is not None:
        payload = {'id': email_receive,
                   'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)}
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token, 'msg': '로그인 성공!'})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디 또는 비밀번호가 일치하지 않습니다.'})


##### 회원가입
ca = certifi.where()

@app.route('/voteView')
def voteview():
    return render_template('voteView.html')

@app.route("/voteViewData", methods=["GET"])
def homework_post2():
    all_voteList = list(db.vote.find({}, {'_id': False}).sort("count_id",-1))

    return jsonify({'msg':all_voteList})



#회원가입 버튼 클릭시 이동
@app.route('/signup')
def sign_up():
    return render_template('signup_index.html')

#로그인 완료 시 메인 페이지로 이동
@app.route('/page/main')
def page_main():
    return render_template('voteView.html')

@app.route("/api/signup", methods=["POST"])
def web_signup_post():
    name_receive = request.form['name_give']
    email_receive = request.form['email_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {'name': name_receive, 'email': email_receive, 'password': pw_hash}
    db.users.insert_one(doc)

    return jsonify({'msg': '가입 완료'})


@app.route("/signin", methods=["GET"])
def web_signup_get():
    user_list = list(db.users.find({}, {'_id': False}))
    return jsonify({'users': user_list})

@app.route("/comment", methods=["POST"])
def web_comments_post():
    token_receive = request.cookies.get('mytoken')
    try:
        payload=jwt.decode(token_receive,SECRET_KEY,algorithms=['HS256'])
        user_info = db.users.find_one({"email": payload["id"]})
        comment_receive = request.form['comment_give']
        vote_receive = request.form['voteId_give']
        doc = {
            'user_id': user_info["email"],
            'comment': comment_receive,
            'vote_id': vote_receive
        }
        db.comments.insert_one(doc)

        return jsonify({'msg': '등록 완료!'})
    except(jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/comment", methods=["GET"])
def web_comments_get():
    order_list = list(db.comments.find({}, {'_id': False}))
    return jsonify({'comments': order_list})
@app.route("/comment/comments_list", methods=["POST"])
def posting_comments_list_get():
    voteId_Receive= request.form["voteId_give"]
    comments_list = list(db.comments.find({'vote_id':voteId_Receive}, {'_id': False}))
    return jsonify({'comments': comments_list})

@app.route("/comment/delete", methods=["POST"])
def comment_delete():
    name_list = request.form['name_give']

    db.comments.delete_one({"user_id": name_list})
    return jsonify({'msg': '삭제되었습니다!'})


@app.route("/homework/l_modify", methods=["POST"])
def modify_left():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.users.find_one({"email": payload["id"]})
    voteId_Receive = request.form["voteId_give"]
    doc = {'voteid': voteId_Receive,
           'email': user_info['email']
           }
    db.voteuser.insert_one(doc)
    left_num_receive = request.form["left_num_give"]
    db.vote.update_one({'count_id':int(voteId_Receive)},
                            {'$set': {'left_num': left_num_receive}})
    return jsonify({'msg': '투표 완료!'})

@app.route("/homework/r_modify", methods=["POST"])
def modify_right():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.users.find_one({"email": payload["id"]})
    voteId_Receive = request.form["voteId_give"]
    doc = {'voteid': voteId_Receive,
           'email': user_info['email']
           }
    db.voteuser.insert_one(doc)
    right_num_receive = request.form["right_num_give"]
    db.vote.update_one({'count_id':int(voteId_Receive)},
                            {'$set': {'right_num': right_num_receive}})
    return jsonify({'msg': '투표 완료!'})


@app.route("/homework", methods=["POST"])
def homework_get():
    voteId_Receive = request.form["voteId_give"]

    comment_list = list(db.vote.find({'count_id':int(voteId_Receive)}, {'_id': False}))



    return jsonify({'comment': comment_list})

@app.route("/voteDisible", methods=["POST"])
def voteDisible():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    user_info = db.users.find_one({"email": payload["id"]})
    voteId_Receive = request.form["voteId_give"]
    comment_list = list(db.voteuser.find({"voteid":voteId_Receive,'email':user_info['email'] }, {'_id': False}))




    return jsonify({'comment': comment_list})


@app.route("/votingPost",methods=["POST"])
def voting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        left_name_receive = db.users.find_one({'email': payload["id"]})
        print(left_name_receive)
        right_num_receive = request.form['right_num_give']
        left_num_receive = request.form['left_num_give']
        voting_title_receive = request.form['voting_title_give']
        voting1_body_receive = request.form['voting1_body_give']
        voting2_body_receive = request.form['voting2_body_give']
        cnt = db.count.find_one({})
        doc = {'count_id': cnt["cnt"],
                'user_id' : left_name_receive["email"],
               'title':voting_title_receive,
               'left_name':voting1_body_receive,
               'right_name':voting2_body_receive,
               'right_num': right_num_receive,
               'left_num': left_num_receive}
        db.vote.insert_one(doc)
        db.count.update_one({},
                            {'$set': {'cnt': cnt["cnt"]+1}})
        return jsonify({'msg': '투표글 작성 완료'})
    except jwt.exceptions.DecodeError:
        return redirect(url_for("/login_1", msg="로그인 정보가 존재하지 않습니다."))
@app.route("/votingPost")
def goto_votingPost():
    return render_template('votingPost.html');

@app.route("/detail")
def goto_detail():
    return render_template('detail.html');


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)