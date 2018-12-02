from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, URL


class PostForm(FlaskForm):
    url = StringField(
        "", validators=[URL()], render_kw={"placeholder": "www.example.com"}
    )
    title = TextAreaField(
        "", validators=[DataRequired()], render_kw={"placeholder": "Your Headline"}
    )
    submit = SubmitField("Submit")


class CommentForm(FlaskForm):
    comment = TextAreaField(
        "Add your comment to the discussion:",
        id="text_box",
        validators=[DataRequired()],
    )
    submit = SubmitField("Post Your Comment")
