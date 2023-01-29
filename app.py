import os

from flask import Flask, render_template, request, flash, redirect, session, g, url_for, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Book, BookNote, BookList
from forms import UserRegisterForm, UserEditForm, LoginForm, CreateEditBooklistForm, CreateEditNoteForm
from open_library import qd_search
from seed import seed_data

CUR_USER_KEY = "cur_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///olreader'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
# toolbar = DebugToolbarExtension(app)

with app.app_context():
    connect_db(app)
    seed_data(db)

#
# User actions
#

@app.before_request
def add_user_to_g():
    """If we're logged in, add cur_user to Flask global."""

    if CUR_USER_KEY in session:
        g.user = User.query.get(session[CUR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CUR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CUR_USER_KEY in session:
        del session[CUR_USER_KEY]

#
# Signup and Login routes
#

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    register_form = UserRegisterForm()

    if register_form.validate_on_submit():
        try:
            user = User.signup(
                username=register_form.username.data,
                password=register_form.password.data,
                email=register_form.email.data,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=register_form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=register_form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("Logged out!", "success")
    return redirect(url_for("login"))

#
# "Public" routes
#

@app.route('/')
def home():
    """If authenticated, show list home. Otherwise prompt to sign up"""

    if g.user:
        return render_template('index.html')

    else:
        return render_template('anon-index.html')


#
# Profile Routes
#

@app.route('/profile')
def show_profile():
    """Show logged in user profile"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    return render_template("/users/profile.html", user_id=g.user.id)


@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    """Edit logged in user profile"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    profile_form = UserEditForm(obj=g.user)
    if profile_form.validate_on_submit():
        profile_form.populate_obj(g.user)
        db.session.commit()

        return redirect(url_for("show_profile"))
    
    return render_template("/users/edit-profile.html", form=profile_form, user_id=g.user.id)


@app.route('/profile/delete', methods=['POST']) # Maybe DELETE?
def delete_profile():
    """Delete the logged in user"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    db.session.delete(g.user)
    db.session.commit()
    
    return redirect(url_for("logout"))


#
# Booklist Routes
#

@app.route('/lists/create', methods=['GET', 'POST'])
def create_booklist():
    """Create Booklist"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    list_form = CreateEditBooklistForm()
    if list_form.validate_on_submit():
        new_list = BookList()
        new_list.user_id = g.user.id
        list_form.populate_obj(new_list)

        db.session.add(new_list)
        db.session.commit()

        return redirect(url_for("show_booklist", list_id=new_list.id))
    
    return render_template("/booklists/create-list.html", form=list_form)


@app.route('/lists/<int:list_id>')
def show_booklist(list_id):
    """Display the list"""

    booklist = BookList.query.get_or_404(list_id)
    return render_template("/booklists/view-list.html", booklist=booklist)


@app.route('/lists/<int:list_id>/edit', methods=['GET', 'POST'])
def edit_booklist(list_id):
    """Edit Booklist"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    edit_list = BookList.query.get_or_404(list_id)
    if edit_list.user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    list_form = CreateEditBooklistForm(obj=edit_list)
    if list_form.validate_on_submit():
        list_form.populate_obj(edit_list)
        db.session.commit()

        return redirect(url_for("show_booklist", list_id=edit_list.id))
    
    return render_template("/booklists/edit-list.html", form=list_form, booklist=edit_list)


@app.route('/lists/<int:list_id>/delete', methods=['POST']) # Maybe DELETE?
def delete_booklist(list_id):
    """Delete the list"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    delete_list = BookList.query.get_or_404(list_id)
    if delete_list.user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    db.session.delete(delete_list)
    db.session.commit()
    
    return redirect(url_for("show_profile"))


#
# BookNote Routes
#

@app.route('/notes/create', methods=['GET', 'POST'])
def create_note():
    """Create BookNote"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    note_form = CreateEditNoteForm()
    if note_form.validate_on_submit():
        new_note = BookNote()
        new_note.user_id = g.user.id
        new_note.book_isbn = "12345" # TODO
        note_form.populate_obj(new_note)

        db.session.add(new_note)
        db.session.commit()

        return redirect(url_for("show_note", note_id=new_note.id))
    
    return render_template("/booknotes/create-note.html", form=note_form)


@app.route('/notes/<int:note_id>')
def show_note(note_id):
    """Display the BookNote"""

    note = BookNote.query.get_or_404(note_id)
    return render_template("/booknotes/view-note.html", note=note)


@app.route('/notes/<int:note_id>/edit', methods=['GET', 'POST'])
def edit_note(note_id):
    """Edit BookNote"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    edit_note = BookNote.query.get_or_404(note_id)
    if edit_note.user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    note_form = CreateEditNoteForm(obj=edit_note)
    if note_form.validate_on_submit():
        note_form.populate_obj(edit_note)
        db.session.commit()

        return redirect(url_for("show_note", note_id=edit_note.id))
    
    return render_template("/booknotes/edit-note.html", form=note_form, note=edit_note)


@app.route('/notes/<int:note_id>/delete', methods=['POST']) # Maybe DELETE?
def delete_note(note_id):
    """Delete the BookNote"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    delete_note = BookNote.query.get_or_404(note_id)
    if delete_note.user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    db.session.delete(delete_note)
    db.session.commit()
    
    return redirect(url_for("show_profile"))


#
# Book and Search
#

@app.route('/search/<term>')
def do_search_url(term):
    """qd_search"""

    json = qd_search(term)

    return render_template("search.html", term=term, results=json)

@app.route('/search')
def do_search():
    """qd_search"""

    term = request.args.get("term")
    json = qd_search(term)

    return render_template("search.html", term=term, results=json)

