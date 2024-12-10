from flask import Flask, flash, session, render_template,request
from flask_cors import CORS
from models import chatApp
from database.database import db
from flask_socketio import SocketIO, join_room, emit
from datetime import datetime



app = Flask(__name__)
CORS(app)
app.secret_key = "quickChat"
app.config['SECRET_KEY'] = 'quickChat'
socketio = SocketIO(app)

@app.route('/')
def index():
    active_section="signup_page"
    return render_template("index.html",active_section=active_section)

@app.route('/signup_page',methods=['POST','GET'])
def signup_page():
    active_section="signup_page"
    return render_template("index.html",active_section=active_section)

@app.route('/signin_page',methods=['POST','GET'])
def signin_page():
    active_section="signin_page"
    return render_template("index.html",active_section=active_section)

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=='POST':
        result=request.form.to_dict()
        new_user=chatApp.add_new_user(result)
        if new_user:
            flash("already have an account!!", "error")
            active_section="signup_page"
            return render_template("index.html",active_section=active_section)
        active_section="signin_page"
        print('result-->>',result)
    return render_template("index.html",active_section=active_section)

realTime_active_user=set()

@app.route('/signin',methods=['POST','GET'])
def signin():
    if request.method=='POST':
        result=request.form.to_dict()
        login_user=chatApp.login_user(result)
        print('login_user data',login_user)
        if login_user==False:
            flash("The email or password is incorrect !!", "error")
            active_section="signin_page"
            return render_template("index.html",active_section=active_section)
        active_section='active_users'
        active_user=chatApp.activeUsers()
        access_email=login_user[0].get('inputEmail')
        access_email_name=login_user[0].get('inputName')
        if 'user' not in session:
             session['user']=[]
        if access_email not in session['user']:
            session['user'].append(access_email)
        print(session['user'])
        realTime_active_user.add(access_email)
        print('realTime_active_user',realTime_active_user)
    return render_template("dashboard.html",active_section=active_section,
                           active_user=active_user,access_email=access_email,access_email_name=access_email_name)


@app.route('/logout/<access_email>',methods=['POST','GET'])
def logout(access_email):
 
    session['user']=list(realTime_active_user)
    index=session['user'].index(access_email)
    print('index',index)
    session.pop(index,None)
   
    if access_email in realTime_active_user:
        realTime_active_user.discard(access_email)
    session.clear()
    active_section="signin_page"
    return render_template("index.html",active_section=active_section)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/active_users/<access_email>/<access_email_name>',methods=['POST','GET'])
def active_users(access_email,access_email_name):
    if access_email not in realTime_active_user:    
                return render_template("index.html",active_section="signin_page")
    active_section='active_users'
    active_user=chatApp.activeUsers()
    access_email=access_email
    access_email_name=access_email_name
    return render_template('dashboard.html',active_section=active_section,active_user=active_user,
                           access_email=access_email,access_email_name=access_email_name)

@app.route('/create_join_group/<access_email>/<access_email_name>',methods=['POST','GET'])
def create_join_group(access_email,access_email_name):
    if access_email not in realTime_active_user:   
                return render_template("index.html",active_section="signin_page")
    active_section='create_join_group'
    access_email=access_email
    access_email_name=access_email_name
    return render_template('dashboard.html',active_section=active_section,access_email=access_email,
                           access_email_name=access_email_name)


@app.route('/created_groups/<access_email>/<access_email_name>',methods=['POST','GET'])
def created_groups(access_email,access_email_name):
    if access_email not in realTime_active_user:   
                return render_template("index.html",active_section="signin_page")
    active_section='created_groups'
    access_email=access_email
    access_email_name=access_email_name
    groups=chatApp.all_groups(access_email)
    return render_template('dashboard.html',active_section=active_section,access_email=access_email,
                           access_email_name=access_email_name,groups=groups)


@app.route('/single_chat_page/<sender_email>/<receiver_email>/<receiver_name>/<access_email_name>',methods=['POST','GET'])
def single_chat_page(sender_email,receiver_email,receiver_name,access_email_name):
    if sender_email not in realTime_active_user: 
                return render_template("index.html",active_section="signin_page")
    sender_email=sender_email
    receiver_email=receiver_email
    both_active_user=False
    print("realTime_active_user",realTime_active_user)
    if sender_email in realTime_active_user and receiver_email in realTime_active_user:
         both_active_user=True
    receiver_name=receiver_name
    access_email_name=access_email_name
    room=min(sender_email,receiver_email)+"_"+max(sender_email,receiver_email)
    messages=chatApp.personal_message(sender_email,receiver_email,room)
    print("both_active_user",both_active_user)
    # sender_id=messages['_id']
    # receiver_id=messages['_id']
    print(messages)
    return render_template('chat.html',sender_email=sender_email,receiver_email=receiver_email,
                           access_email_name=access_email_name, both_active_user=both_active_user,
                           receiver_name=receiver_name,messages=messages,room=room)


# personal chat socketio working
@socketio.on('join')
def on_join(data):
    """Handle a user joining a chat room."""
    room = data['room']
    user=data['user']
    join_room(room)
    print("room",room)
    print('user',user)
    emit('status', {'msg': user}, room=room)
 
@socketio.on('send_message')
def handle_send_message(data):
    """Handle sending a new message."""
    room = data['room']
    sender_id = data['sender_email']
    receiver_id = data['receiver_email']
    message = data['message']
    sender_name=data['sender_name']
    receiver_name=data['receiver_name']
 
    # Save the message in MongoDB
    db.personal_message.insert_one({
        'room':room,
        'sender_email': sender_id,
        'receiver_email': receiver_id,
        'sender_name': sender_name,
        'receiver_name': receiver_name,
        'message': message,
        'timestamp': datetime.now()
    })

    emit('new_message', {
        'sender_email': sender_id,
        'sender_name':sender_name,
        'message': message
    }, room=room)
 

@app.route('/createGroup/<access_email>/<access_email_name>',methods=['POST','GET'])
def createGroup(access_email,access_email_name):
     result=request.form.to_dict()
     groups=chatApp.create_group(access_email,access_email_name,result)
     active_section='created_groups'
     access_email=access_email
     access_email_name=access_email_name
     return render_template('dashboard.html',active_section=active_section,
                            access_email=access_email,access_email_name=access_email_name,groups=groups)


@app.route('/joinGroup/<access_email>/<access_email_name>',methods=['POST','GET'])
def joinGroup(access_email,access_email_name):
     result=request.form.to_dict()
     groups=chatApp.join_group(access_email,access_email_name,result)
     active_section="create_join_group"
     access_email=access_email
     access_email_name=access_email_name
     if groups=='Joined':
        flash("Already Joined the Group !!", "warning")       
        return render_template("dashboard.html",active_section=active_section,
                               access_email=access_email,access_email_name=access_email_name)
     elif groups==False:
        flash("Access Key is incorrect !!", "error")
        return render_template("dashboard.html",active_section=active_section,
                               access_email=access_email,access_email_name=access_email_name)
     else:
        flash("Joined Successfully!!", "success")
        return render_template('dashboard.html',active_section=active_section,
                            access_email=access_email,access_email_name=access_email_name,groups=groups)


      

@app.route('/group_chat_page/<sender_email>/<access_email_name>/<groupName>/<groupAccessKey>',methods=['POST','GET'])
def group_chat_page(sender_email,access_email_name,groupName,groupAccessKey):
    if sender_email not in realTime_active_user:      
                return render_template("index.html",active_section="signin_page")
    sender_email=sender_email
    access_email_name=access_email_name
    groupName=groupName
    room=str(groupAccessKey)
    group_members=chatApp.group_members(room)
    print('group_members',group_members)
    messages=chatApp.group_message(sender_email,room)
    print(messages)
    return render_template('groupchat.html',sender_email=sender_email,
                           access_email_name=access_email_name,messages=messages,
                           groupName=groupName,room=room,group_members=group_members)


# group chat socketio working
@socketio.on('join_group')
def on_join(data):
    """Handle a user joining a chat room."""
    room = data['room']
    join_room(room)
    print("room",room)
    emit('status', {'msg': f"available"}, room=room)
 
@socketio.on('send_message_group')
def handle_send_message(data):
    """Handle sending a new message."""
    room = data['room']
    sender_id = data['sender_email']
    message = data['message']
    sender_name=data['sender_name']

 
    # Save the message in MongoDB
    db.group_message.insert_one({
        'room':room,
        'sender_email': sender_id,
        'sender_name': sender_name,
        'message': message,
        'timestamp': datetime.now()
    })

    emit('new_message_group', {
        'sender_email': sender_id,
        'sender_name':sender_name,
        'message': message
    }, room=room)



if __name__=="__main__":
    socketio.run(app, debug=True)