
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:20040219@localhost/sports'
db = SQLAlchemy(app)

# 数据库模型
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(50))

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    role = db.Column(db.String(100))


# 创建数据库表
def create_tables():
    with app.app_context():
        db.create_all()

create_tables()

# 登录页面
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            return redirect(url_for('main'))
        flash('用户名或密码错误')
    return render_template('login.html')

# 主页面
@app.route('/main')
def main():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('main.html')

# 项目管理页面
@app.route('/projects', methods=['GET', 'POST'])
def projects():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    search_project_name = request.form.get('search_project_name', '')

    if request.method == 'POST':
        if 'add_project' in request.form:
            name = request.form['project_name']
            description = request.form.get('description')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            status = request.form.get('status')
            new_project = Project(name=name, description=description, start_date=start_date, end_date=end_date, status=status)
            db.session.add(new_project)
            db.session.commit()
        elif 'update_project' in request.form:
            project_id = request.form['project_id']
            project = Project.query.get(project_id)
            if project:
                if 'new_name' in request.form and request.form['new_name']:
                    project.name = request.form['new_name']
                if 'new_description' in request.form and request.form['new_description']:
                    project.description = request.form['new_description']
                if 'new_start_date' in request.form and request.form['new_start_date']:
                    project.start_date = request.form['new_start_date']
                if 'new_end_date' in request.form and request.form['new_end_date']:
                    project.end_date = request.form['new_end_date']
                if 'new_status' in request.form and request.form['new_status']:
                    project.status = request.form['new_status']
                db.session.commit()
        elif 'delete_project' in request.form:
            project_id = request.form['project_id']
            project = Project.query.get(project_id)
            if project:
                db.session.delete(project)
                db.session.commit()

    projects = Project.query.filter(Project.name.ilike(f'%{search_project_name}%')).all()
    return render_template('projects.html', projects=projects)

# 参与者管理页面
@app.route('/participants', methods=['GET', 'POST'])
def participants():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    search_participant_name = request.form.get('search_participant_name', '')

    if request.method == 'POST':
        if 'add_participant' in request.form:
            name = request.form['participant_name']
            email = request.form['email']
            role = request.form['role']
            new_participant = Participant(name=name, email=email, role=role)
            db.session.add(new_participant)
            db.session.commit()
        elif 'update_participant' in request.form:
            participant_id = request.form['participant_id']
            participant = Participant.query.get(participant_id)
            if participant:
                if 'new_name' in request.form and request.form['new_name']:
                    participant.name = request.form['new_name']
                if 'new_email' in request.form and request.form['new_email']:
                    participant.email = request.form['new_email']
                if 'new_role' in request.form and request.form['new_role']:
                    participant.role = request.form['new_role']
                db.session.commit()
        elif 'delete_participant' in request.form:
            participant_id = request.form['participant_id']
            participant = Participant.query.get(participant_id)
            if participant:
                db.session.delete(participant)
                db.session.commit()

    participants = Participant.query.filter(Participant.name.ilike(f'%{search_participant_name}%')).all()
    return render_template('participants.html', participants=participants)

# 退出登录
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
