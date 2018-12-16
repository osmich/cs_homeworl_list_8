from flask import (
    Flask,
    render_template,
    redirect, url_for, request,
    session, jsonify
)
from flask_cors import CORS
import os, datetime
from database_operations import register_user, login_user, get_transfers, new_transfer, reset_password, admin_get_transfers, admin_get_pending, admin_accept, new_transfer_api, check_admin
from helpers import check_keys, check_login, check_transfer, send_password

from flask_restful import Api
from OpenSSL import SSL

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, create_refresh_token,
    jwt_refresh_token_required, get_raw_jwt
)


app = Flask(__name__, template_folder="templates")
CORS(app)
api = Api(app)
app.secret_key = os.urandom(987) 

jwt = JWTManager(app)
blacklist = set()

def verifyUser(sse):
    if 'user' in sse:
        return True
    return False

def verifyAdmin(sse):
    if 'admin' in sse:
        return True
    return False


@app.route('/')
def home():
    session.pop('user', None)
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    session.pop('user', None)
    if request.method == 'POST' and check_login(request.form):
        result = login_user(request.form)
        if result["result"] == True:
            if result["value"][0]["Role"] == "ADMIN":
                session['admin'] = result["value"][0]["id"]
                return render_template('admin_home.html')
            else:
                session['user'] = result["value"][0]["id"]
                return render_template('account.html')
    return render_template('index.html', error=error)

@app.route('/postRegister', methods=['GET', 'POST'])
def postRegister():
    if request.method == 'POST' and check_keys(request.form) and register_user(request.form):
        return render_template('postRegister.html', error=None)

    return render_template('errorRegister.html', error=None)


@app.route('/account', methods=['GET', 'POST'])
def account():
    if verifyUser(session):
        return render_template('account.html')
    return redirect('login')

@app.route('/logout')
def logout():
    if verifyUser(session):
        session.pop('user')
    if verifyAdmin(session):
        session.pop('admin')
    return render_template('index.html')


@app.route('/form')
def form():
    if verifyUser(session):
        return render_template('form.html')
    return render_template('index.html')


@app.route('/cform', methods=['GET', 'POST'])
def cform():
    if verifyUser(session):
        return render_template('cform.html')
    return render_template('badRequest.html')


@app.route('/sendtransfer', methods=['GET', 'POST'])
def sendTransfer():
    print("-----------")
    print(request.args.get('firstname'))
    if verifyUser(session):# and check_transfer(request.args): #and request.method == 'POST'
        result = new_transfer(request.args, session['user'])
        if result == True:
            return render_template('sendTransfer.html')
        else:
            return render_template('errorForm.html')
    return render_template('badRequest.html')

@app.route('/history')
def history():
    if verifyUser(session):
        if 'user' in request.args:
            transfers = get_transfers(request.args.get('user'))
            return render_template("history.html", data=transfers)
        transfers = get_transfers(session["user"])
        return render_template("history.html", data=transfers)
    return render_template("index.html")

@app.route('/reset')
def reset():
    if verifyUser(session):
        session.pop('user')
    return render_template('reset.html')

@app.route('/creset', methods=['GET', 'POST'])
def creset():
    if verifyUser(session):
        session.pop('user')
    if 'user' in request.form:
        result = reset_password(request.form['user'])
        if result["result"] == True:
            send_password(result["email"], result['password'])
            return render_template('creset.html')
    return render_template('badRequest.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if verifyAdmin(session):
        return render_template('admin_home.html')
    return redirect('login')

@app.route('/alltransfers')
def alltransfers():
    if verifyAdmin(session):
        transfers = admin_get_transfers()
        return render_template("all_transfers.html", data=transfers)
    return render_template('index.html')


@app.route('/pending')
def pending():
    if verifyAdmin(session):
        transfers = admin_get_pending()
        return render_template("pending_transfers.html", data=transfers)
    return render_template('index.html')

@app.route('/approve')
def approve():
    if verifyAdmin(session):
        transfer = request.args.get('accept')
        if transfer != None:
            transfers = admin_accept(transfer)
        return render_template("pending_transfers.html", data=transfers)
    return render_template('index.html')


@app.route('/script.js')
def script():
    return render_template("script.js")

@app.route('/violate.js')
def violate():
    return render_template("violate.js")
    
@app.route('/violate2.js')
def violate2():
    return render_template("violate2.js")


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist

@app.route('/api/login', methods=['POST'])
def apiLogin():
    # return "jsonify(d)"
    # print('ds:')transfers = get_transfers(request.args.get('user'))
    # print(request.is_json)
    # print(request.get_json()['username'])
    if check_login(request.get_json()):
        result = login_user(request.get_json())
        if result["result"] == True:
            # access_token = create_access_token(identity=request.get_json()['username'])
            access_token = create_access_token(identity=result["value"][0]["id"])
            if result["value"][0]["Role"] == "ADMIN":
                # session['admin'] = result["value"][0]["id"]
                d = "{'user': " + request.get_json()['username'] +"\",  \"role\": 'admin', 'status': 'logged-in'}"
                return jsonify(access_token=access_token)
            else:
                # session['user'] = result["value"][0]["id"]
                d = "{'user': " + request.get_json()['username'] +"\", 'status': 'logged-in'}"
                return jsonify(access_token=access_token)
                # return render_template('account.html')
        d = "{'user': " + request.get_json()['username'] + "'status': 'failed to login'}"
        return d +'\n'
    return "Bad request\n"


@app.route('/api/status')
@jwt_required
def status():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user)


@app.route('/api/logout')
@jwt_required
def apiLogout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({'success': True})

@app.route('/api/register', methods=['POST'])
def apiRegister():
    data = request.get_json()
    print(data)
    if 'username' in data:
        print('yesss')
    if register_user(data):
        return jsonify({'status': 'registered', 'message': 'new user successfully registered'})

    return jsonify({'status': 'failed', 'message': 'An error occured during the registration process'})



@app.route('/api/form', methods=['POST'])
@jwt_required
def apiForm():
    print(request)
    print(request.json)
    print(request.get_json())
    result = new_transfer_api(request.get_json(), get_jwt_identity())
    if result == True:
        return jsonify({'transfer': 'success'})
    else:
        return jsonify({'transfer': 'failed'})


@app.route('/api/get/transfers')
@jwt_required
def apiGetTransfer():
    transfers = get_transfers(get_jwt_identity())
    return jsonify(transfers)



@app.route('/api/get/all/transfers')
@jwt_required
def apiGetALLTranfers():
    admin = check_admin(get_jwt_identity())
    if admin:
        transfers=admin_get_transfers()
        return jsonify(transfers)
    return jsonify({"Error": "User not allowed to perform such an acction"})

@app.route('/api/get/pending')
@jwt_required
def apiPending():
    admin = check_admin(get_jwt_identity())
    if admin:
        transfers=admin_get_pending()
        return jsonify(transfers)
    return jsonify({"Error": "User not allowed to perform such an acction"})


@app.route('/api/accept', methods=['POST'])
@jwt_required
def apiAccept():
    transfer = request.get_json()['accept']
    if transfer != None:
        admin_accept(transfer)
        return jsonify({"Status":"accepted"}) 
    return jsonify({"error":"You are not allowed to perform such an action"}) 
# @app.route('/api/reset')
# def apiReset():


# context = SSL.Context(SSL.SSLv23_METHOD)
# context.use_privatekey_file('ssl/privkeyA.pem')
# context.use_certificate_file('ssl/serverA.crt')

context = ('ssl/serverA.crt', 'ssl/privkeyA.pem')
app.config['JWT_BLACKLIST_ENABLED'] = True

if __name__ == '__main__':
    app.run(host='0.0.0.0', ssl_context=context)
    # app.run(host='0.0.0.0')



