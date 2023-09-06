import os

from flask import Flask, render_template, request, flash, redirect, session, g, url_for, abort, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Book, BookNote, BookList
from forms import UserRegisterForm, UserEditForm, LoginForm, CreateEditBooklistForm, CreateEditNoteForm
from open_library import keyword_search, fetch_availabilty_links, fetch_trending_books, fetch_book_data
from seed import seed_data

CUR_USER_KEY = "cur_user"
MUST_BE_LOGGED_IN = "You must be signed in to access that page!"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
uri = os.getenv("DATABASE_URL", 'postgresql:///olreader')  # or other relevant config var
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri

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
        # g.user = User.query.get(session[CUR_USER_KEY])
        g.user = User.query.filter_by(id=session[CUR_USER_KEY]).one()

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
    """Show Home Page"""

    return render_template('index.html')


#
# Profile Routes
#

@app.route('/profile')
def show_profile():
    """Show logged in user profile"""

    if not g.user:
        flash(MUST_BE_LOGGED_IN, "danger")
        return redirect(url_for("login"))
    
    return render_template("/users/profile.html", user_id=g.user.id)


@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    """Edit logged in user profile"""

    if not g.user:
        flash(MUST_BE_LOGGED_IN, "danger")
        return redirect(url_for("login"))
    
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
        flash(MUST_BE_LOGGED_IN, "danger")
        return redirect(url_for("login"))
    
    if request.method == "GET":
        book_olid = request.args.get("bookid")

        if book_olid is not None:
            list_form = CreateEditBooklistForm(data={"book_olid": book_olid})
        else:
            list_form = CreateEditBooklistForm()
    else:
        list_form = CreateEditBooklistForm()

    if list_form.validate_on_submit():
        new_list = BookList()
        new_list.user_id = g.user.id
        list_form.populate_obj(new_list)

        db.session.add(new_list)
        db.session.commit()

        olid = list_form.book_olid.data
        if olid is not None and len(olid) > 0:
            new_list.add_olid(olid)

        return redirect(url_for("show_booklist", list_id=new_list.id))
    
    return render_template("/booklists/create-list.html", form=list_form)


@app.route('/lists/createlist', methods=['POST'])
def create_booklist_json():
    """Create Booklist from JSON object"""

    if not g.user:
        return jsonify({
                "err": MUST_BE_LOGGED_IN,
                "type": "danger",
                })

    title = request.json.get("title")
    blurb = request.json.get("blurb")
    olid = request.json.get("olid")

    if (title is not None and len(title) > 0):
        new_list = BookList()
        new_list.user_id = g.user.id
        new_list.title = title
        new_list.blurb = blurb

        db.session.add(new_list)
        db.session.commit()
        
        if olid is not None and len(olid) > 0:
            new_list.add_olid(olid)
    else:
        return jsonify({
                "err": f"Title is required!",
                "type": "danger",
                })
    
    return jsonify({
            "msg": "List Created!",
            "listId": new_list.id,
            "listTitle": new_list.title,
        })


@app.route('/lists/<int:list_id>')
def show_booklist(list_id):
    """Display the list"""

    booklist = BookList.query.get_or_404(list_id)
    return render_template("/booklists/view-list.html", booklist=booklist)


@app.route('/lists/<int:list_id>/add', methods=['GET', 'POST'])
def add_books_booklist(list_id):
    """Add Books to Booklist"""

    if not g.user:
        flash(MUST_BE_LOGGED_IN, "danger")
        return redirect(url_for("login"))
    
    add_list = BookList.query.get_or_404(list_id)
    if add_list.user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    if request.method == 'POST':
        olid = request.json.get("workId")
        isbn = request.json.get("isbn")
        if olid is not None and len(olid) > 0:
            book_record = Book.query.filter_by(olid=olid).first()

            if book_record is not None:
                if book_record not in add_list.books:
                    add_list.books.append(book_record)
                    db.session.commit()
                else:
                    return jsonify({
                        "err": f"List already contains {book_record.title}",
                        "type": "warning",
                        })

            else:
                # add the book!
                book_record = Book.create_book(olid, isbn)
                add_list.books.append(book_record)
                db.session.commit()

            return jsonify(book_record.to_dict())

        return jsonify({
            "err": f"Failed to find {work_id}",
            "type": "danger",
            })
    
    return render_template("/booklists/add-list.html", booklist=add_list)

@app.route('/lists/<int:list_id>/remove', methods=['POST'])
def remove_books_booklist(list_id):
    """Remove Books from Booklist"""

    if not g.user:
        flash(MUST_BE_LOGGED_IN, "danger")
        return redirect(url_for("login"))
    
    remove_list = BookList.query.get_or_404(list_id)
    if remove_list.user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    work_id = request.json.get("workId")
    if work_id is not None and len(work_id) > 0:
        book_record = Book.query.filter(Book.olid == work_id).first()

        if book_record is not None:
            if book_record in remove_list.books:
                remove_list.books.remove(book_record)
                db.session.commit()
                return jsonify({ 
                        "result": "success",
                        })
            else:
                return jsonify({
                    "err": f"{book_record.title} isn't in this list.",
                    "type": "warning",
                    })
        
        return jsonify({
                "err": f"Could not find the item to remove",
                "type": "danger",
                })


@app.route('/lists/<int:list_id>/edit', methods=['GET', 'POST'])
def edit_booklist(list_id):
    """Edit Booklist"""

    if not g.user:
        flash(MUST_BE_LOGGED_IN, "danger")
        return redirect(url_for("login"))
    
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
        flash(MUST_BE_LOGGED_IN, "danger")
        return redirect(url_for("login"))
    
    delete_list = BookList.query.get_or_404(list_id)
    if delete_list.user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    db.session.delete(delete_list)
    db.session.commit()
    
    return redirect(url_for("show_profile"))


@app.route('/lists/read')
def show_read_books():
    """Pseudo list which shows the books the logged in user has read"""

    if not g.user:
        flash(MUST_BE_LOGGED_IN, "danger")
        return redirect(url_for("login"))
    
    read_list = [note.book for note in g.user.notes if note.read == True]

    return render_template("/booklists/read-list.html", books=read_list)


#
# Book Routes
#

@app.route('/books/<book_id>')
def show_book(book_id):
    """Display the Book"""

    if not g.user:
        flash(MUST_BE_LOGGED_IN, "danger")
        return redirect(url_for("login"))

    book = Book.query.get_or_404(book_id)
    note = BookNote.query.filter_by(user_id=g.user.id).filter_by(book_olid=book.olid).first()
    lists = [bl for bl in book.lists if bl.user_id == g.user.id]

    links = fetch_availabilty_links(book.olid)

    return render_template("/books/view-book.html", book=book, note=note, lists=lists, links=links)

#
# BookNote Routes
#

@app.route('/notes/create', methods=['GET', 'POST'])
def create_note():
    """Create BookNote"""

    if not g.user:
        flash(MUST_BE_LOGGED_IN, "danger")
        return redirect(url_for("login"))
    
    if request.method == "GET":
        book_olid = request.args.get("bookid")

        if book_olid is not None:
            for note in g.user.notes:
                if note.book_olid == book_olid:
                    flash("A note already exists for this book!", "warning")
                    return redirect(url_for("show_note", note_id=note.id))

            note_form = CreateEditNoteForm(data={"book_olid": book_olid})
        else:
            flash("Search for a book first!", "warning")
            return redirect(url_for("search_create_note"))
    else:
        note_form = CreateEditNoteForm()
    
    if note_form.validate_on_submit():
        new_note = BookNote()
        new_note.user_id = g.user.id
        note_form.populate_obj(new_note)

        olid = new_note.book_olid
        book = Book.query.filter_by(olid=olid).first()
        if (book is None):
            # add the book!
            book_record = Book.create_book(olid, None)
            db.session.commit()

        db.session.add(new_note)
        db.session.commit()

        return redirect(url_for("show_note", note_id=new_note.id))
    
    book_olid = request.args.get("bookid")
    note_form.book_olid = book_olid
    book_preview = fetch_book_data(book_olid)
    book_preview["olid"] = book_olid

    return render_template("/booknotes/create-note.html", form=note_form, book_preview=book_preview)


@app.route('/notes/create/search')
def search_create_note():
    """Search for a book to create a note for"""

    if not g.user:
        flash(MUST_BE_LOGGED_IN, "danger")
        return redirect(url_for("login"))
    
    return render_template("/booknotes/search-note.html")


@app.route('/notes/<int:note_id>')
def show_note(note_id):
    """Display the BookNote"""

    note = BookNote.query.get_or_404(note_id)
    book = note.book
    lists = [bl for bl in book.lists if bl.user_id == g.user.id]

    return render_template("/books/view-book.html", book=book, note=note, lists=lists)


@app.route('/notes/<int:note_id>/edit', methods=['GET', 'POST'])
def edit_note(note_id):
    """Edit BookNote"""

    if not g.user:
        flash(MUST_BE_LOGGED_IN, "danger")
        return redirect(url_for("login"))
    
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
        flash(MUST_BE_LOGGED_IN, "danger")
        return redirect(url_for("login"))
    
    delete_note = BookNote.query.get_or_404(note_id)
    if delete_note.user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    db.session.delete(delete_note)
    db.session.commit()
    
    return redirect(url_for("show_profile"))


#
# Search
#

@app.route('/search/<term>')
def do_search_json(term):
    """Keyword search"""

    page = request.args.get("page", 1)
    results = keyword_search(term, page=page)

    if g.user:
        lists = [{"listId": user_list.id, "listTitle": user_list.title} for user_list in g.user.lists]

    return jsonify({
        "user_lists": lists,
        "results": results,
    })


@app.route('/search')
def do_search():
    """Keyword search"""

    term = request.args.get("term")
    page = request.args.get("page", 1)
    json = keyword_search(term, page=page)

    return render_template("search/search.html", term=term, results=json)


#
# Trending
#
@app.route('/trending')
def show_trending():
    """Show trending books page"""

    return render_template("books/trending.html")


@app.route('/trending/fetch')
def fetch_trending():
    """Get trending books"""
    
    trending_type = request.args.get("type")

    trending_books = fetch_trending_books(trending_type)
    lists = []

    if g.user:
        lists = [{"listId": user_list.id, "listTitle": user_list.title} for user_list in g.user.lists]

    return jsonify({
        "user_lists": lists,
        "trending_books": trending_books,
    })