from flask import Flask
from flask import render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
from flask import flash

app = Flask(__name__)

app.config['SECRET_KEY'] = '100d56df75a29ea6717b1db3436e06b8'   # prevents website attacks, cookie manipulation

posts = [
    {
        "author": "Corey Schafer",
        "title": "Blog Post 1",
        "content": "First post content",
        "date_posted": "April 20, 2018",
    },
    {
        "author": "Jane Doe",
        "title": "Blog Post 2",
        "content": "Second post content",
        "date_posted": "April 21, 2018",
    },
]


@app.route("/")
@app.route("/home")
def home():
    # return '<h1>Home Page<h1>'  # easier to use a template
    return render_template("home.html", posts=posts)


@app.route("/about")
def about():
    return render_template("about.html", title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))

    return render_template("register.html", title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':

            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful!', 'danger')
    return render_template("login.html", title='Login', form=form) 
        

if __name__ == "__main__":

    app.run(
        debug=True
    )  # this means you dont have to restart the server after each change

