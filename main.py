from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import choice
app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api_key = "TopSecretAPIKey"

##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dic(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def random():
    cafes = Cafe.query.all()
    cafe = choice(cafes)
    return jsonify(cafe=cafe.to_dic())

    # return jsonify(cafe={
    #     "name":cafe.name,
    #     "img_url":cafe.img_url,
    #     "location":{
    #         "map_url":cafe.map_url,
    #         "address":cafe.location},
    #     "seats":cafe.seats,
    #     "amenities":{
    #         "has_toilet":cafe.has_toilet,
    #         "has_wifi":cafe.has_wifi,
    #         "has_sockets":cafe.has_sockets,
    #         "can_take_calls":cafe.can_take_calls,
    #         "coffee_price":cafe.coffee_price}})

@app.route("/all")
def all():
    cafes = Cafe.query.all()
    json_cafes = [cafe.to_dic() for cafe in cafes]
    return jsonify(cafes=json_cafes)


@app.route("/search")
def search():
    user_location = request.args.get("loc")
    cafes = Cafe.query.all()
    json_cafes = [cafe.to_dic() for cafe in cafes if cafe.location == user_location]
    if json_cafes:
        return jsonify(cafes=json_cafes)
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


## HTTP POST - Add Record
@app.route("/add", methods=["POST"])
def add():

    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe_to_update = Cafe.query.get(cafe_id)
    if cafe_to_update:
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the coffee price."})
    else:
        return jsonify(error={"Not Found": "The cafe with this id is not found."})


## HTTP DELETE - Delete Record
@app.route("/report-closed/<int:id>", methods=["DELETE"])
def delete(id):
    if request.args.get("api_key") == api_key:
        cafe_to_delete = Cafe.query.get(id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe."})
        else:
            return jsonify(error={"Not Found": "The cafe with this id is not found."})
    else:
        return jsonify(error={"Error": "The api_key is incorrect."})


if __name__ == '__main__':
    app.run(debug=True)
