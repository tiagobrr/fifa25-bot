from main import db

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    player = db.Column(db.String(50))
    team = db.Column(db.String(50))
    opponent = db.Column(db.String(50))
    goals = db.Column(db.Integer)
    win = db.Column(db.Boolean)
    league = db.Column(db.String(50))
    stadium = db.Column(db.String(50))
    date = db.Column(db.Date)
    time = db.Column(db.String(5))
    status = db.Column(db.String(20))

class PlayerStats(db.Model):
    __tablename__ = 'player_stats'
    id = db.Column(db.Integer, primary_key=True)
    player = db.Column(db.String(50))
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)

class BotConfig(db.Model):
    __tablename__ = 'bot_config'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50))
    value = db.Column(db.String(50))
