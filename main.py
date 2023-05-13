from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from wtforms import SubmitField, StringField
from wtforms.validators import URL, DataRequired
from flask_wtf import FlaskForm
from datetime import datetime
import string
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwerty'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database//urls.sqlite3'

db = SQLAlchemy()

class URLModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(255), unique=True)
    short = db.Column(db.String(255), unique=True)
    visits = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'Url {self.id}: ({self.title[:20]}...)'
    
db.init_app(app)

with app.app_context():
    db.create_all()
    
class URLForm(FlaskForm):
    link = StringField('Введите ссылку',
                        validators=[DataRequired('Поле не должно быть пустым'),
                                    URL(message="Неверная ссылка")])
    submit = SubmitField('Получить короткую ссылку')
    
def get_short():
    while True:
        short = ''.join([random.choice(string.ascii_letters) for _ in range(8)])
        with app.app_context():
            if not URLModel.query.filter(URLModel.short == short).first():
                return short

get_short()

@app.route('/', methods=["GET", "POST"])
def home():
    form = URLForm()
    if form.validate_on_submit():
        link = URLModel()
        link.link = form.link.data
        link.short = get_short()
        with app.app_context():
            if URLModel.query.filter(URLModel.link == link.link).first():
                return render_template('index.html', form=form)
            db.session.add(link)
            db.session.commit()
        return redirect(url_for('urls'))
    return render_template('index.html', form=form)

@app.route('/urls')
def urls():
    urls_ = URLModel.query.all()
    return render_template('urls.html', urls=urls_[::-1])

@app.route('/<string:short>', methods=['GET'])
def short_redirect(short):
    link = URLModel.query.filter( URLModel.short == short ).first()
    if link:
        link.visits += 1
        db.session.add(link)
        db.session.commit()
        return redirect(link.link)
    
if __name__ == '__main__':
    app.run()