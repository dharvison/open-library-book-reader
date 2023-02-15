from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, Length


class UserRegisterForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class UserEditForm(FlaskForm):
    """Form for editing users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    bio = TextAreaField('Bio')


class CreateEditBooklistForm(FlaskForm):
    """Form to create or edit a booklist."""

    title = StringField('Title', validators=[DataRequired()])
    blurb = TextAreaField('Description')
    book_olid = HiddenField('book_olid')


class CreateEditNoteForm(FlaskForm):
    """Form to create or edit a note."""

    read = BooleanField('Read')
    note = TextAreaField('Note')
    book_olid = HiddenField('book_olid')

