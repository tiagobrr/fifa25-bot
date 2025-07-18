from main import db
from sqlalchemy import Column, Integer, String, Boolean, Date

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player = db.Column(db.String(80))
    team = db.Column(db.String(80))
    opponent = db.Column(db.String(80))
    goals = db.Column(db.Integer)
    win = db.Column(db.Boolean)
    league = db.Column(db.String(80))
    stadium = db.Column(db.String(80))
    date = db.Column(db.Date)
    time = db.Column(db.String(10))
    status = db.Column(db.String(20))

class PlayerStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player = db.Column(db.String(80))
    total_games = db.Column(db.Integer)
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)

class BotConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_to = db.Column(db.String(120))
