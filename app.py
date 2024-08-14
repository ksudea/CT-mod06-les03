from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from mysql.connector import Error

my_password = "0711"
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{my_password}@localhost/fitness_center_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    age = fields.Integer(required=True)

    class Meta:
        fields = ("id", "name", "age")

class WorkoutSchema(ma.Schema):
    session_id = fields.Integer(required=True)
    member_id = fields.Integer(required=True)
    session_date = fields.Date()
    duration = fields.Integer()
    calories_burned = fields.Integer()

    class Meta:
        fields = ("session_id","member_id", "session_date", "duration", "calories_burned")

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True) 

#Task 1
class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer)
    workouts = db.relationship('Workouts', backref='member')
    

class Workouts(db.Model):
    __tablename__ = 'workoutsessionsdetailed'
    session_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    session_date = db.Column(db.Date)
    duration = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)

# Task 2 

@app.route('/members', methods=['POST'])
def add_member():
    # Logic to add a member
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    try:
        new_member = Member(id=member_data['id'], name=member_data['name'], age=member_data['age'])
        db.session.add(new_member)
        db.session.commit()
        return jsonify({"message": "New member added successfully"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    try:
    # Logic to retrieve a member
        member = Member.query.get_or_404(id)
        return member_schema.jsonify(member)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    member = Member.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    try:
        member.name = member_data['name']
        member.age = member_data['age']
        db.session.commit()
        return jsonify({"message": "Member updated successfully"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):
    try:
        member_to_remove = Member.query.get_or_404(id)
        db.session.delete(member_to_remove)
        db.session.commit()
        return jsonify({"message": "Member removed successfully"}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

#Task 3

#Schedule/add workouts
@app.route('/workouts', methods=['POST'])
def add_workout():
    # Logic to add a member
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    try:
        new_workout = Workouts(session_id=workout_data['session_id'], member_id=workout_data['member_id'], session_date=workout_data['session_date'], duration=workout_data['duration'], calories_burned=workout_data['calories_burned'])
        db.session.add(new_workout)
        db.session.commit()
        return jsonify({"message": "New workout added successfully"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# View/get workout
@app.route('/workouts/<int:session_id>', methods=['GET'])
def get_workout(session_id):
    try:
    # Logic to retrieve a member
        workout = Workouts.query.get_or_404(session_id)
        return workout_schema.jsonify(workout)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
#Update workout info
@app.route('/workouts/<int:session_id>', methods=['PUT'])
def update_workout(session_id):
    workout = Workouts.query.get_or_404(session_id)
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    try:
        workout.member_id = workout_data['member_id']
        workout.session_date = workout_data['session_date']
        workout.duration = workout_data['duration']
        workout.calories_burned = workout_data['calories_burned']
        db.session.commit()
        return jsonify({"message": "Member updated successfully"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
#Retrieve all workout sessions for a specific member
@app.route('/member-workouts/<int:member_id>', methods=['GET'])
def get_member_workouts(member_id):
    try:
    # Logic to retrieve a member
        workouts = Workouts.query.filter_by(member_id=member_id)
        return workouts_schema.jsonify(workouts)
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)