### generate table token
# import uuid
# import json
# tokens = {}

# def generate_token(user_data):
#     token = str(uuid.uuid4())
#     tokens[token] = user_data

# for i in range(1,41):
#     generate_token(i)

# with open('table_token.json', "w", encoding="utf-8") as f:
#     json.dump(tokens, f)

### generate qr code
# import qrcode
# def create_qc(token):

#     url = f"http://www.heba/table/{token}"

#     # QR 코드 생성
#     qr = qrcode.QRCode()
#     qr.add_data(url)
#     qr.make(fit=True)

#     # 이미지 파일로 저장
#     image = qr.make_image()
#     image.save("qrcode.png")

#########################################################

from flask import Flask, request, render_template, jsonify, session
import json
import os
import controller
from datetime import timedelta

app = Flask(__name__, static_folder='../react/heba-festival/build/', static_url_path='/')
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
# app.permanent_session_lifetime = timedelta(minutes=90)

with open('table_token.json', "r", encoding="utf-8") as f:
    qr_data = json.load(f)

@app.route('/<token>')
def index(token):
    table_no = controller.get_table_no_by_token(token)
    if table_no:
        session['token'] = token
        session['table_info'] = controller.get_table(controller.get_table_no_by_token(token))

        return app.send_static_file('index.html')

@app.route('/get-data', methods=['GET'])
def get_data():
    output = dict()
    # analyze what data has requested and return them
    # (ex)
    # for k,v in request.args:
    #     ...
    
    # flask automatically JSONify dictionary
    return output

@app.route('/post-data', methods=['POST'])
def post_data():
    output = dict()

    # analyze what request received and execute them
    # (ex)
    # for k,v in request.args:
    #     ...

    # record request is succeeded or failed
    output['result'] = 'OK'

    # flask automatically JSONify dictionary
    return output

### 전체 테이블
# curl -X POST -H 'Content-type:application/json' http://127.0.0.1:5000/get-all -d '{"token":"80b156da-ae18-4bfb-a413-2b6ce6532c69"}'
@app.route('/get-all', methods=['POST'])
def get_all():
    output = dict()
    data = request.get_json()  
    token = data.get('token')
    
    if controller.get_table(controller.get_table_no_by_token(token)):

        with open('table.json', "r", encoding="utf-8") as f:
            table_data = json.load(f)

        output['result'] = table_data
        return output
    else:
        output['result'] = {"fail" : "Invalid token"}
        return output

### table info 조회
# curl -X POST -H 'Content-type:application/json' http://127.0.0.1:5000/get-table -d '{"token":"80b156da-ae18-4bfb-a413-2b6ce6532c69"}'
@app.route('/get-table', methods=['POST'])
def get_table():
    output = dict()

    data = request.get_json()  
    token = data.get('token')
    table_info = controller.get_table(controller.get_table_no_by_token(token))

    if table_info:
        table_info = controller.get_table(controller.get_table_no_by_token(token))
        output['result'] = table_info
        return output
    else:
        output['result'] = {'error': 'Token is missing or invalid'}
        return output

### 입력값 저장
# curl -X POST -H 'Content-type:application/json' http://127.0.0.1:5000/set-table -d '{"token":"80b156da-ae18-4bfb-a413-2b6ce6532c69", "gender":"male", "nums":3, "note":"aaa", "photo":false}'
@app.route('/set-table', methods=["POST"])
def set_table():
    output = dict()
    data = request.get_json()

    token = data.get('token')
    table_no = controller.get_table_no_by_token(token)

    if table_no:
        gender = data.get('gender')
        nums = data.get('nums')
        note = data.get('note')
        photo = data.get('photo')

        result = controller.set_table(table_no, nums, gender, photo, note)  
        output['result'] = result
        return output
    else:
        output['result'] = {'error': 'Token is missing or invalid'}
        return output

### 테이블 정보 수정
# curl -X POST -H 'Content-type:application/json' http://127.0.0.1:5000/update-info -d '{"token":"07d2eb50-731d-4227-8ed6-f17e2884ab04","m_count":3,"f_count":4,"note":"ccc"}'
@app.route('/update-info', methods=["POST"])
def update_info():
    output = dict()
    data = request.get_json()

    token = data.get('token')
    table_no = controller.get_table_no_by_token(token)

    m_count = data.get('m_count')
    f_count = data.get('f_count')
    note = data.get('note')

    output['result'] = controller.update_info(table_no, m_count, f_count, note)        
    return output

### send like
# curl -X POST -H 'Content-type:application/json' http://127.0.0.1:5000/send-like -d '{"token":"80b156da-ae18-4bfb-a413-2b6ce6532c69", "received_table":2}'
@app.route('/send-like', methods=["POST"])
def send_like():
    output = dict()
    data = request.get_json()

    token = data.get('token')
    received_table = data.get('received_table')
    
    output['result'] = controller.send_like(controller.get_table_no_by_token(token), received_table)

    return output

### join 
# curl -X POST -H 'Content-type:application/json' http://127.0.0.1:5000/join -d '{"from_where":1, "to_where":2, "token":"bb7d-314147da97cd-9db4d2d0-ea5a-4a96"}'
@app.route('/join', methods=["POST"])
def join_table():
    output = dict()
    data = request.get_json()
    token = data.get('token')
    if controller.get_table_no_by_token(token) == 'admin':
        from_where = data.get('from_where')
        to_where = data.get('to_where')
        
        output['result'] = controller.join_table(from_where, to_where)
        return output
    
    output['result'] = {"fail" : "Invalid token"}
    return output

### reject
# curl -X POST -H 'Content-type:application/json' http://127.0.0.1:5000/reject -d '{"token":"80b156da-ae18-4bfb-a413-2b6ce6532c69", "reject":2}'
@app.route('/reject', methods=["POST"])
def reject():
    output = dict()
    data = request.get_json()

    token = data.get('token')
    table_no = controller.get_table_no_by_token(token)
    if table_no:
        reject_table = data.get('reject')
        output['result'] = controller.reject(table_no, reject_table)
        return output
    else:
        output['result'] = {"fail" : "Invalid token"}
        return output

##########################################################
########################## 관리자 ##########################
##########################################################

### 하트 충전
# curl -X POST -H 'Content-type:application/json' http://127.0.0.1:5000/add-likes -d '{"token":"bb7d-314147da97cd-9db4d2d0-ea5a-4a96", "table_no":1, "count":2}'
@app.route('/add-likes', methods=["POST"])
def add_likes():
    output = dict()
    data = request.get_json()

    token = data.get('token')
    if controller.get_table_no_by_token(token) == 'admin':
        table_no = data.get('table_no')
        count = data.get('count')

        output['result'] = controller.add_likes(table_no, count)
        return output
    else:
        output['result'] = {"fail" : "Invalid token"}
        return output

### 시간 충전
# curl -X POST -H 'Content-type:application/json' http://127.0.0.1:5000/add-time -d '{"token":"bb7d-314147da97cd-9db4d2d0-ea5a-4a96", "table_no":1, "minutes":5}'
@app.route('/add-time', methods=["POST"])
def add_time():
    output = dict()
    data = request.get_json()

    token = data.get('token')

    if controller.get_table_no_by_token(token) == 'admin':
        table_no = data.get('table_no')
        print(table_no)
        if controller.get_table(table_no)['active'] == True:
            minutes = data.get('minutes')

            output['result'] = controller.add_time(table_no, minutes)
            return output
        else:
            output['result'] = {"fail" : f"Table {table_no} active False"}
            return output
    else:
        output['result'] = {"fail" : "Invalid token"}
        return output

### 테이블 비우기
# curl -X POST -H 'Content-type:application/json' http://127.0.0.1:5000/reset-table -d '{"token":"bb7d-314147da97cd-9db4d2d0-ea5a-4a96", "table_no":1}'
@app.route('/reset-table', methods=["POST"])
def reset_table():
    output = dict()
    data = request.get_json()

    token = data.get('token')

    if controller.get_table_no_by_token(token) == 'admin':
        table_no = data.get('table_no')
        output['result'] = controller.reset_table_2(table_no)
        return output
    else:
        output['result'] = {"fail" : "Invalid token"}
        return output


# @app.route('/table/<token>') 
# def handle_token(token):
#     table_info = controller.get_table(controller.get_table_no_by_token(token))

#     if table_info['active']:
#         return render_template('index.html', token=token, table_info=table_info)
#     else:
#         return render_template('input.html', token=token, table_info=table_info)    

# @app.route('/hunting', methods=["POST"])
# def input():
#     if not request.form.get('gender'):
#         token = request.form.get('token')
#         table_info = controller.get_table(controller.get_table_no_by_token(token))

#         if table_info['active']:
#             return render_template('hunting.html', table_info=table_info)
#         else:
#             return render_template('input.html', token=token)    
#     else:
#         token = request.form.get('token')
#         table_no = controller.get_table_no_by_token(token)
#         count = int(request.form.get('count'))
#         gender = request.form.get('gender')

#         controller.set_table(table_no, count, gender)

#         # session[str(table_no)] = token
#         # session.permanent = True
#         # print(session)

#         table_info = controller.get_table(table_no)
        
#         return render_template('hunting.html', table_info=table_info)

if __name__ == '__main__':
    # app.run(host='0.0.0.0', debug=True)
    app.run(debug=True)
