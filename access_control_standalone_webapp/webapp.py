from flask import Flask, render_template, Response, session, flash
from flask.ext.login import LoginManager, UserMixin, login_required, login_user, logout_user
from flask_restful import Resource, Api
import json, flask, os, shutil, signal, sys, pwd, argparse

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)



class ACL:
    def __init__(self, list_filename = "users.json", card_reader_pipe_file = "card_reader.pipe"):
        self.list_filename = list_filename
        self.card_reader_pipe_file = card_reader_pipe_file
        self.populate()
        
    def populate(self):
        if os.path.getsize(self.list_filename) == 0:
            self.users = []

        else:
            with open(self.list_filename, 'r') as fd:
                self.users = json.loads(fd.read())
                
            for user in self.users:
                if not "name" in user:
                    raise ValueError('Expecting key "name" for each user in the users json file')
                    
                if not "card_number" in user:
                    raise ValueError('Expecting key "card_number" for each user in the users json file')
                
                if not "active" in user:
                    raise ValueError('Expecting key "active" for each user in the users json file')
                    
                if not type(user['active']) is bool:
                    raise ValueError('Expecting key "active" to be of type bool for user {0}'.format(user['name']))
        
    def add_new_user(self, username_field, card_number_field, is_active):
        if is_active.lower() == "true":
            active = True
        else:
            active = False
        temp_user = {"active": active, "name": username_field, "card_number": card_number_field}
        self.users.append(temp_user)
        
        self.rewrite_acl_file()
        self.populate()
        self.signal_reader_reload()
        
    def update_user(self, username_field, card_number_field, is_active, current_name, current_card_number, current_active):
        found = False
        for user in self.users:
            if user['card_number'] == current_card_number:
                found = True
                user['card_number'] = card_number_field
                user['name']        = username_field
                user['active']      = True if is_active.lower() == 'true' else False
                break
                
                
        self.rewrite_acl_file()
        self.populate()
        self.signal_reader_reload()
        
    def delete_user(self, current_name, current_card_number, current_active):
        found = False
        for user in self.users:
            if user['card_number'] == current_card_number:
                found = True
                self.users.remove(user)
                break
                
        self.rewrite_acl_file()
        self.populate()
        self.signal_reader_reload()
        
    def signal_reader_reload(self):
        try:
            config.write_pipe_fd.write('1') #writing to the pipe the parent proc gave us; meant to function as a signal, to tell the parent proc that the user file has been modified
        
        except Exception as e:
            flash(u"Could not signal the card reader module to update its user list: the card reader is most likey not aware of this most recent user update. Error: {0}".format(e), 'danger')
        
    def rewrite_acl_file(self):
        content = json.dumps(self.users, sort_keys=True, indent=4, separators=(',', ': '))
        shutil.copyfile(self.list_filename, self.list_filename + ".bckup")
        with open(self.list_filename, "w") as fd:
            fd.write(content)

                

class Config:
    def __init__(self,  pipe_number, config_filename = "webapp_settings.json"):
        self.main_user_password = ""
        self.config_filename    = config_filename
        self.populate()
        self.write_pipe_fd = os.fdopen(pipe_number, 'w', 0) #parent passed a pipe number, we want to write to it and buffer  0 bytes (thus no output buffering, immediate writing)
        
        
    def populate(self):
        with open(self.config_filename, 'r') as fd:
            config = json.loads(fd.read())
            
        if not "main_user" in config:
            raise ValueError('Expecting key "main_user" in the json file')
        else:
            self.main_user = config['main_user']
            
        if not "main_password" in config:
            raise ValueError('Expecting key "main_password" in the json file')
        else:
            self.main_password = config['main_password']
            
        if not "user_id_demotion" in config:
            raise ValueError('Expecting key "user_id_demotion" in the json file')
        else:
            self.user_id_demotion = config['user_id_demotion']
            



class User():
    def __init__(self, name, authenticated, active=True):
        self.name = name
        self.active = active
        self.authenticated = authenticated
        
        
    
    def is_authenticated(self):
        return self.authenticated
        
    def is_active(self):
        return self.active
        
    def is_anonymous(self):
        return False
        
    def get_id(self):
        return self.name.decode('utf-8')

##User view pages
@login_manager.unauthorized_handler
def unauthorized_page():
    flash(u'Please log in first', 'danger')
    return flask.redirect(flask.url_for('home_page'))
        

@login_manager.user_loader
def load_user(user_id):
    if user_id == config.main_user:
        return User(user_id, True)
    else:
        return None


@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash(u'Logged out', 'info')
    return flask.redirect(flask.url_for('home_page'))
    
    
@app.route("/delete_user", methods=['GET', 'POST'])
@login_required
def delete_user():
    post = flask.request.form
    user_acl.delete_user(post['current_name'], post['current_card_number'], post['current_active'])
    flash_txt = "Deleted user '{0}', with card '{1}'. Card enabled? {2}".format(post['current_name'], post['current_card_number'], post['current_active'])
    flash(flash_txt, 'info')
    return flask.redirect(flask.url_for('user_management_page'))
    
@app.route("/update_user", methods=['GET', 'POST'])
@login_required
def update_user():
    post = flask.request.form
    if post['editing_new_user'].lower() == 'true':
        user_acl.add_new_user(post['username_field'], post['card_number_field'], post['is_active'])
        flash_txt = "Added new user '{0}', with card '{1}'. Card enabled? {2}".format(post['username_field'], post['card_number_field'], post['is_active'])
        
    else:
        user_acl.update_user(post['username_field'], post['card_number_field'], post['is_active'], post['current_name'], post['current_card_number'], post['current_active'])
        flash_txt = "User updated to '{0}', with card '{1}'. Card enabled? {2}   [was '{3}', card number '{4}', was card enabled? {5}]".format(post['username_field'], post['card_number_field'], post['is_active'], post['current_name'], post['current_card_number'], post['current_active'])
        
    flash(flash_txt, 'info')
    return flask.redirect(flask.url_for('user_management_page'))


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    username = flask.request.form['username_field']
    password = flask.request.form['password_field']
    remember_me = False
    if "remember-me" in flask.request.form:
        remember_me = True
        
    if username == config.main_user and password == config.main_password:
        user = User(username, True)

    else:
        flash(u'Invalid credentials provided', 'danger')
        return flask.redirect(flask.url_for('home_page'))
        
    flash(u'Logged in', 'success')
    login_user(user, remember = remember_me)
    return flask.redirect(flask.url_for('home_page'))


@app.route('/')
def home_page():
    return render_template("index.html")

    
@app.route('/user_management/<card_number>')
@login_required
def edit_user(card_number):
    if card_number.isdigit() and int(card_number) == -1: #new user
        return render_template("user_edit.html", user = True, new_user = True)
    
    #editing user
    user = None
    for user_ in user_acl.users:
        if user_['card_number'] == card_number:
            user = user_
            
    if not user:
            flash("User card number '{0}' invalid".format(card_number), 'danger')
            return render_template("user_management.html", users = user_acl.users)
    return render_template("user_edit.html", user = user, new_user = False)
    
@app.route('/user_management')
@login_required
def user_management_page():
    return render_template("user_management.html", users = user_acl.users)
    
    
#If we're started by root, we want to drop our privileges
def demote_self():
    if os.getuid() == 0: #if we're root
        demoted_uid = pwd.getpwnam(config.user_id_demotion).pw_uid  #getting the uid for our user with reduced privileges
        os.setuid(demoted_uid) #asking the OS to demote us to this user so we're no longer root

#parsing command-line argumetns
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pipe',    action='store', type=int,   help="pipe number passed by the parent process; will write to this pipe number as a way to signal to the parent that the users file was changed -- if you're running this from the shell, just pass the digit 1 and this process will write chars to the stdout every time a user is changed", required=True )
    args = parser.parse_args()
    return args
        
if __name__ == '__main__':
    args = parse_args()
    
    global config    #storing global configs
    config = Config(pipe_number=args.pipe); 
    
    global user_acl  #storing users who have access and who don't to the lab
    user_acl = ACL() 

    demote_self() #lose root privileges if we ever had them
    
    app.config["SECRET_KEY"] = '4oxJDiK9N:;/$%**COe3JiNUG73162CbV' #needed for session cookies
    app.run(debug=True, host="0.0.0.0")
