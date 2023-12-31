import requests
import asyncio
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from os import path
from flask_cors import CORS

DB_NAME = "websites.db"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app=app, resources=r"/*")


# initialize db
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# create db
class Websites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255))
    interval = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


""" function to create
database tables if they dont
exist
"""
def create_db_tables(app, DB_NAME):
    if not path.exists(f"/WebMon/{DB_NAME}"):
        with app.app_context():
            db.create_all()
            print(f"{DB_NAME} created successfully..")

    pass

create_db_tables(app, DB_NAME)
codes = []


def show_websites():
    """Print all websites status code."""
    asyncio.sleep(1)
    with db.app.app_context():
        for website in Websites.query.all():
            codes.append(test(website.url))

    return codes


def test(url):
    contents = requests.get(url)
    return contents.status_code

"""
Ensure only links with https
are used
"""
def validate_url(url):
    prefix = list(url[0:5])
    if "s" in prefix:
        return True
        
    return False
    

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    title = "Home"
    if request.method == 'POST':
        website_title = request.form.get('title')
        website_url = request.form.get('url')
        monitor_interval = request.form.get('interval')
        website_status = test(website_url)
        if validate_url(website_url):
            new_website = Websites(title=website_title,
                               url=website_url,
                               interval=monitor_interval,
                               status=website_status)
        # push to db
            try:
                db.session.add(new_website)
                db.session.commit()
                return redirect('/')
            except:
                return "Error adding website"
            
        return redirect(url_for("handle_errors", message="Only live url can be used "))
    else:
        websites = Websites.query.order_by(Websites.id.desc()).all()
        return render_template('index.html', title=title, websites=websites)

"""
delete the endpoint
"""   
@app.route("/webmon/delete/<int:id>")
def delete_endpoint(id):
    url = Websites.query.filter_by(id=id).first()
    db.session.delete(url)
    db.session.commit()
    websites = Websites.query.order_by(Websites.id.desc()).all()
    return render_template('index.html', title="Home", websites=websites)

"""
Endpoint to handle errors
"""
@app.route("/errors/<string:message>")
def handle_errors(message):
    return f"<h2>An error occured: {message}</h2>"

if __name__ == '__main__':
    # app.config.from_object(Config())

    # db.init_app(app)

    app.run(debug=True)

