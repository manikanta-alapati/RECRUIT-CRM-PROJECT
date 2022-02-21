from datetime import datetime, timedelta
from urllib import response
from flask import Flask, Response, request, jsonify
import sqlite3
import jwt

db_file = "db.sqlite"

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        print(e)
    return conn

# with open('schema.sql') as f:
#     connection = create_connection()
#     connection.executescript(f.read())

app = Flask(__name__)

def login_required(func):
    def decorated(*args, **kwargs):
        headers = request.headers
        token = headers.get('Authorization')
        if not token:
            return Response(status=403)

        load = jwt.decode(token, "SECRET", algorithms=["HS256"])
        email, exp = load["email"], load["exp"]
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(f"select * from users where email='{email}';")
        users = cursor.fetchall()
        request.user = users[0]
        return func(*args, **kwargs)
    
    decorated.__name__ = func.__name__
    return decorated


@app.route("/company", methods=['POST'])
@login_required
def create_company():
    body = request.json
    fields = ["user_mail", "name", "website", "phone_number", "city", "state", "country", "industry"]
    data = dict()
    for field in fields:
        if field in body:
            data[field] = body[field]
        else:
            data[field] = "Account" if field=="industry" else ""
    user_mail, name, website, phone_number, city, state, country, industry = data["user_mail"], data["name"], data["website"], data["phone_number"], data["city"], data["state"], data["country"], data["industry"]
    query = f"insert into company (user_mail, name, website, phone_number, city, state, country, industry) values ( '{user_mail}', '{name}', '{website}', '{phone_number}', '{city}', '{state}', '{country}', '{industry}');"
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    return Response(status=200)

@app.route("/company/<int:id>/update", methods=["POST"])
@login_required
def update_company(id):
    body = request.json
    fields = ["name", "website", "phone_number", "city", "state", "country", "industry"]
    data = dict()
    query_part = ""
    for field in fields:
        if field in body:
            data[field] = body[field]
            query_part += f"{field} = '{body[field]}',"
    if query_part!="":
        query_part = query_part[:-1]
    print("update", data)
    query = f"update company set {query_part} where id={id};"
    print("update query", query)
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    return Response(status=200)

@app.route("/company/<int:id>/delete", methods=["POST"])
@login_required
def delete_company(id):
    body = request.json
    query = f"delete from company where id={id};"
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    return Response(status=200)


@app.route("/company/<int:id>", methods=["GET"])
@login_required
def get_company(id):
    query = f"select * from company where id={id};"
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    data = list(map(lambda tup: list(tup), cursor.fetchall()))
    print('companies', data[0])
    return jsonify(data[0])

@app.route("/company/all")
@login_required
def get_companies():
    query = f"select * from company;"
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    data = list(map(lambda tup: list(tup), cursor.fetchall()))
    print('companies', data)
    return jsonify(data)


@app.route("/users/signup", methods=["POST"])
def signup():
    body = request.json
    email, password, name = body["email"], body["password"], body["name"]
    query = f"insert into users values ('{email}', '{name}', '{password}');"
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    return Response(status = 200)


@app.route("/users/login", methods=["POST"])
def login():
    body = request.json
    email, password = body["email"], body["password"]
    query = f"select * from users where email='{email}';"
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    user = list(map(lambda tup: list(tup), cursor.fetchall()))
    print("users:",user)
    if len(user)==0 or user[0][2] != password:
        return Response(status=403)
    jwt_token = jwt.encode({"email": user[0][0], 'exp': datetime.utcnow()+timedelta(minutes=60)}, "SECRET", algorithm="HS256")

    return jsonify({"jwt_token": jwt_token.decode("utf-8")})
    

app.run(3000)


# create table company (company_id integer primary key autoincrement, user_mail varchar(100) not null, name varchar(50) not null, website text, phone_number varchar(10) not null, city varchar(50), state varchar(50), country varchar(50), industry text check(industry in ('Account', 'IT', 'Sales', 'Health Care')) not null default 'Account', foreign key(user_mail) references users(email));

# create table users (email varchar(100) primary key, name varchar(50) not null, password text not null);