import smtplib

from flask import Flask, render_template, request
import requests
from smtplib import SMTP
from dotenv import load_dotenv
import os


load_dotenv()


EMAIL = "alexkharrodpython"
SMTP_URL = "smtp.gmail.com"
PASSWORD = os.getenv("PASSWORD")



# USE YOUR OWN npoint LINK! ADD AN IMAGE URL FOR YOUR POST. 👇
posts = requests.get("https://api.npoint.io/c790b4d5cab58020d391").json()

app = Flask(__name__)


@app.route('/')
def get_all_posts():
    return render_template("index.html", all_posts=posts)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        return render_template("contact.html")
    elif request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']
        send_mail(address=email, message=message, name=name, phone=phone)
        return f"<h1>Hello {name}, we successfully sent your message"


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = None
    for blog_post in posts:
        if blog_post["id"] == index:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)

def send_mail(address, message, name, phone):
    with smtplib.SMTP(host=SMTP_URL, port=587) as connection:
        connection.starttls()
        connection.login(user=EMAIL, password=PASSWORD)
        connection.sendmail(from_addr=EMAIL, to_addrs=address, msg=f"Subject: Contact Request from {name}\n\nName: {name}\nPhone: {phone}"
                                                                   f"\nEmail: {address}\n Message: {message}")



if __name__ == "__main__":
    app.run(debug=True, port=5001)
