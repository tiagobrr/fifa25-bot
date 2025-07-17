import os
import logging
from flask import Flask, render_template, jsonify, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from threading import Thread
import time
import datetime
import pytz

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fifa25-bot-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///fifa25_bot.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Global variables for bot state
current_matches = []
daily_matches = []
last_update = None
bot_running = False

# Configuration
MONITORED_PLAYERS = ["uncle", "Koftovsky", "cl1vlind", "wboy", "nikkitta", "Boki", "Bolec",
    "Giox", "Cevuu", "Glumac", "volvo", "nekishka", "Cavempt", "bodyaoo", "noeN", "zoyir"]

VALID_LEAGUES = ["Liga 1", "Europa League", "Premier League", "International A", "Seria A", "Champions League B"]

VALID_TEAMS = ["Marseille", "Paris Saint-Germain F.C.", "LOSC Lille", "AS Monaco", "Olympique Lyonnais",
    "Eintracht Frankfurt", "Tottenham Hotspur", "Roma", "Fenerbahce", "Manchester United",
    "Manchester City", "Chelsea", "Liverpool", "Arsenal", "Spain", "France", "Argentina", "Germany", "Italy",
    "Bologna", "Fiorentina", "Juventus", "Napoli", "PSV", "Bayer 04 Leverkusen", "Borussia Dortmund", "Atlético Madrid"]

DEFAULT_STADIUM = "Old Trafford"
DEFAULT_LEAGUE = "Liga 1"

# Timezone configuration
BRAZIL_TZ = pytz.timezone('America/Sao_Paulo')

with app.app_context():
    import models
    db.create_all()

@app.route('/')
def dashboard():
    """Main dashboard page showing live matches and statistics"""
    global current_matches, daily_matches, last_update
    
    from data_analyzer import DataAnalyzer
    analyzer = DataAnalyzer()
    stats = analyzer.get_daily_stats(daily_matches)
    
    return render_template('dashboard.html', 
                         current_matches=current_matches,
                         daily_matches=daily_matches,
                         stats=stats,
                         last_update=last_update,
                         bot_running=bot_running)

@app.route('/players')
def players():
    """Players statistics page"""
    from data_analyzer import DataAnalyzer
    analyzer = DataAnalyzer()
    player_stats = analyzer.get_player_statistics(daily_matches)
    
    return render_template('players.html', 
                         players=player_stats,
                         monitored_players=MONITORED_PLAYERS)

@app.route('/matches')
def matches():
    """Matches history page"""
    return render_template('matches.html', 
                         matches=daily_matches,
                         current_matches=current_matches)

@app.route('/reports')
def reports():
    """Reports generation and email configuration page"""
    return render_template('reports.html')

@app.route('/api/live_matches')
def api_live_matches():
    """API endpoint for live matches data"""
    global current_matches, last_update
    return jsonify({
        'matches': current_matches,
        'last_update': last_update.isoformat() if last_update else None,
        'count': len(current_matches)
    })

@app.route('/api/daily_stats')
def api_daily_stats():
    """API endpoint for daily statistics"""
    from data_analyzer import DataAnalyzer
    analyzer = DataAnalyzer()
    stats = analyzer.get_daily_stats(daily_matches)
    return jsonify(stats)

@app.route('/api/player_stats')
def api_player_stats():
    """API endpoint for player statistics"""
    from data_analyzer import DataAnalyzer
    analyzer = DataAnalyzer()
    player_stats = analyzer.get_player_statistics(daily_matches)
    return jsonify(player_stats)

@app.route('/api/generate_report', methods=['POST'])
def api_generate_report():
    """Generate and optionally email a report"""
    try:
        email_to = request.form.get('email_to')
        
        from data_analyzer import DataAnalyzer
        analyzer = DataAnalyzer()
        report_file = analyzer.generate_excel_report(daily_matches)
        
        if email_to:
            from email_service import EmailService
            email_service = EmailService()
            success = email_service.send_report(email_to, report_file)
            if success:
                flash('Report generated and emailed successfully!', 'success')
            else:
                flash('Report generated but email failed to send.', 'warning')
        else:
            flash('Report generated successfully!', 'success')
            
        return redirect(url_for('reports'))
    except Exception as e:
        app.logger.error(f"Error generating report: {e}")
        flash('Error generating report.', 'error')
        return redirect(url_for('reports'))

@app.route('/api/bot_control', methods=['POST'])
def api_bot_control():
    """Control bot start/stop"""
    global bot_running
    action = request.form.get('action')
    
    if action == 'start' and not bot_running:
        start_monitoring_thread()
        flash('Bot started successfully!', 'success')
    elif action == 'stop' and bot_running:
        bot_running = False
        flash('Bot stopped successfully!', 'info')
    
    return redirect(url_for('dashboard'))

def monitoring_loop():
    """Background monitoring loop"""
    global current_matches, daily_matches, last_update, bot_running
    
    from web_scraper import FIFA25Scraper
    from email_service import EmailService
    from data_analyzer import DataAnalyzer
    from models import Match, PlayerStats, BotConfig
    
    scraper = FIFA25Scraper()
    email_service = EmailService()
    today = datetime.date.today()
    daily_email_sent = False
    
    app.logger.info("🤖 FIFA 25 monitoring bot started")
    
    while bot_running:
        try:
            with app.app_context():
                # Use Brazilian timezone (UTC-3)
                current_time = datetime.datetime.now(BRAZIL_TZ)
                current_date = current_time.date()
                
                # Reset daily data if new day
                if current_date != today:
                    daily_matches = []
                    today = current_date
                    daily_email_sent = False
                    app.logger.info("🔄 New day started, resetting daily data")
                
                # Scrape live matches (every minute)
                app.logger.info("🔍 Scanning for live matches...")
                live_matches = scraper.get_live_matches()
                
                # Filter matches for monitored players
                filtered_matches = []
                for match in live_matches:
                    if ((match['player_left'] in MONITORED_PLAYERS or match['player_right'] in MONITORED_PLAYERS) and
                        match['team_left'] in VALID_TEAMS and match['team_right'] in VALID_TEAMS):
                        
                        # Add both players' data
                        filtered_matches.append({
                            'player': match['player_left'],
                            'team': match['team_left'],
                            'opponent': match['team_right'],
                            'goals': match['goals_left'],
                            'win': match['goals_left'] > match['goals_right'],
                            'league': DEFAULT_LEAGUE,
                            'stadium': DEFAULT_STADIUM,
                            'date': current_date.isoformat(),
                            'time': current_time.strftime('%H:%M'),
                            'status': 'live'
                        })
                        
                        filtered_matches.append({
                            'player': match['player_right'],
                            'team': match['team_right'],
                            'opponent': match['team_left'],
                            'goals': match['goals_right'],
                            'win': match['goals_right'] > match['goals_left'],
                            'league': DEFAULT_LEAGUE,
                            'stadium': DEFAULT_STADIUM,
                            'date': current_date.isoformat(),
                            'time': current_time.strftime('%H:%M'),
                            'status': 'live'
                        })
                
                current_matches = filtered_matches
                
                # Add new matches to daily collection and save to database
                for match_data in filtered_matches:
                    if match_data not in daily_matches:
                        daily_matches.append(match_data)
                        
                        # Save to database
                        try:
                            # Convert date string back to date object
                            match_date = datetime.datetime.fromisoformat(match_data['date']).date()
                            
                            # Check if match already exists
                            existing_match = Match.query.filter_by(
                                player=match_data['player'],
                                team=match_data['team'],
                                opponent=match_data['opponent'],
                                date=match_date,
                                time=match_data['time']
                            ).first()
                            
                            if not existing_match:
                                match = Match(
                                    player=match_data['player'],
                                    team=match_data['team'],
                                    opponent=match_data['opponent'],
                                    goals=match_data['goals'],
                                    win=match_data['win'],
                                    league=match_data['league'],
                                    stadium=match_data['stadium'],
                                    date=match_date,
                                    time=match_data['time'],
                                    status=match_data['status']
                                )
                                db.session.add(match)
                                db.session.commit()
                                app.logger.info(f"💾 Saved match: {match_data['player']} vs {match_data['opponent']}")
                        except Exception as e:
                            app.logger.error(f"❌ Error saving match: {e}")
                            db.session.rollback()
                
                last_update = current_time
                
                if filtered_matches:
                    app.logger.info(f"✅ Found {len(filtered_matches)} live matches")
                else:
                    app.logger.info("⭕ No live matches found for monitored players")
                
                # Send daily email at 23:59 Brazilian time
                if (not daily_email_sent and current_time.hour >= 23 and current_time.minute >= 59 and daily_matches):
                    try:
                        analyzer = DataAnalyzer()
                        report_file = analyzer.generate_excel_report(daily_matches)
                        
                        email_to = os.environ.get('EMAIL_TO', 'admin@example.com')
                        if email_service.send_report(email_to, report_file):
                            app.logger.info("📧 Daily report sent successfully")
                            daily_email_sent = True
                        else:
                            app.logger.error("❌ Failed to send daily report")
                    except Exception as e:
                        app.logger.error(f"❌ Error sending daily report: {e}")
            
        except Exception as e:
            app.logger.error(f"❌ Error in monitoring loop: {e}")
        
        # Wait 1 minute before next scan
        time.sleep(60)
    
    app.logger.info("🛑 Monitoring bot stopped")

def start_monitoring_thread():
    """Start the monitoring thread"""
    global bot_running
    if not bot_running:
        bot_running = True
        thread = Thread(target=monitoring_loop)
        thread.daemon = True
        thread.start()

# Start monitoring on app startup
with app.app_context():
    start_monitoring_thread()

