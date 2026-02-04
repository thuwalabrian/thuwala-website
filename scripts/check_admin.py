from app import app, db, User
from werkzeug.security import check_password_hash

with app.app_context():
    u = User.query.filter_by(username='admin').first()
    if not u:
        print('admin: NOT FOUND')
    else:
        print('admin FOUND')
        print('username:', u.username)
        print('email:', u.email)
        print('password_hash:', u.password_hash[:60] + '...' if u.password_hash else 'None')
        print('check Admin@2024:', check_password_hash(u.password_hash, 'Admin@2024'))
