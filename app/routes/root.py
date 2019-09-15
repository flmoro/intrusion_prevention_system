from flask import Blueprint, render_template


bp = Blueprint('root', __name__)


@bp.route('/')
@bp.route('/home')
def home():
    return render_template('home.html')


@bp.route('/about')
def about():
    return render_template('about.html')
