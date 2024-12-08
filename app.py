from flask import Flask, render_template, redirect, url_for, request, flash
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, login_manager
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)
login_manager.init_app(app)

# Зареждане на потребителите за Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Администраторска страница с достъп само за логнати потребители
class AuthenticatedAdminView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

class UserAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

# Инициализация на Flask-Admin
admin = Admin(app, name='Admin Panel', template_mode='bootstrap4', index_view=AuthenticatedAdminView())
admin.add_view(UserAdmin(User, db.session))

# Начална страница
@app.route('/')
def index():
    return '<h1>Добре дошли в приложението!</h1>'

# Логин страница
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('admin.index'))
        else:
            flash('Грешно потребителско име или парола!', 'error')
    return render_template('login.html')

# Логаут
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Създаване на базата данни
@app.before_first_request
def create_tables():
    db.create_all()
    # Добави примерен потребител, ако няма
    if not User.query.filter_by(username="admin").first():
        hashed_password = generate_password_hash("password", method='pbkdf2:sha256')
        db.session.add(User(username="admin", password=hashed_password))
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
