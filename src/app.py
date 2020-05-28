from flask import Flask, render_template, redirect, request, url_for, send_file, flash
from flask_login import login_required, current_user, UserMixin, LoginManager,login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from flask_pymongo import PyMongo
    
app=Flask(__name__)
app.config['SECRET_KEY'] = 'IAMSECRETOKSANA'
app.config["MONGO_URI"] = "mongodb://mongodb:27017/oks"

mongo = PyMongo(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    
    ## Previous local database
    #user_database = {"oksana": ("oksana", "task3"),
       #        "oksana2": ("oksana2", "login")}
    def __init__(self, username, password):
        self.id = username
        self.password = password
        
    @classmethod
    def getuser(cls,username):
        if cls.getuserfromdb(cls,username) is not None:
            return User(username,cls.getuserfromdb(cls,username)[1])
        else:
            return None
    
    @classmethod
    def get(cls,id):
        user = cls.getuserfromdb(cls,id)
        print(user)
        return user

    @classmethod
    def register(cls,username,password):
        cls.id = username
        cls.username = username
        cls.password = password
        cls.insert_new_user_to_mongo(cls)
    
    
    def getuserfromdb(self,username):
        user_database = None
        user = mongo.db.users.find_one({"_id": username})
        ## user returns example {'_id': 'oksana', 'username': 'oksana', 'password': 'task3'} from database
        ## the next line is to bring it to our format like user_database like we did previously
        if user is not None:
            user_database = (user['username'], user['password'])
        return user_database

    def json(self):
        return {
            "username": self.username,
            "_id": self.id,
            "password": self.password
        }

    def insert_new_user_to_mongo(self):
        print(self.json(self))
        mongo.db.users.insert_one(self.json(self))

@login_manager.user_loader
def load_user(username):
    return User.getuser(username)

def load_user_class(username,password):
    user_entry = User.get(username)
    if (user_entry is not None):
        user = User(user_entry[0],user_entry[1])
        if (user.password == password):
            return user
    return None

class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Submit')
    
class RegistrationForm(FlaskForm):
    username = StringField('Username',description = 'Username')
    password = PasswordField('New Password',)
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Submit')
    



#When we go to localhost:5000/ , visit login page
@app.route('/',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = form.username.data
        password = form.password.data
        u = load_user_class(user,password)
        if u is not None:
            login_user(u)
            flash("Successfully logged in")
            return redirect(url_for('cabinet'))
        else:
            flash( "Wrong login credentials")
    return render_template('login.html', form=form)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    logout_user()
    return render_template("logout.html")


#Secret page cabinet, only when authenticated

@app.route('/cabinet', methods=['GET'])
@login_required
def cabinet():
    error = None
    print(current_user)
    return render_template('cabinet.html', error=error)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            username = request.form["username"]
            password = request.form["password"]
            print(username,password)
            find_user =  User.get(username)
            if find_user is None:
                User.register(username, password)
                flash(f'Account created for {form.username.data}!', 'success')
            else:
                flash(f'Account already exists for {form.username.data}!', 'success')
    return render_template('register.html', title='Register', form=form)



import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'upload'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploaded_file', methods=['GET', 'POST'])
def uploaded_file():
    return render_template("uploaded_file.html")


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''
    
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER




if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
 
