from flask import Flask, render_template, request, redirect
from threading import Thread
import datetime
import logging
import os
from web_scraper import get_live_matches
from models.database import db, Match
import pandas as pd
import time

# --- Configuração da aplicação Flask ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///matches.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Variáveis globais ---
monitoring = False
thread = None
last_saved_ids = set()
players_to_monitor = [
    "uncle", "Koftovsky", "cl1vlind", "wboy", "nikkitta", "Boki", "Bolec", "Giox",
    "Cevuu", "Glumac", "volvo", "nekishka", "Cavempt", "bodyaoo", "noeN", "v1nniePuh",
    "Goldfer", "tohi4", "maksdh", "Noitexx", "Steksy"
]

# --- Função de monitoramento ---
def monitor_matches():
    global last_saved_ids
    logger.info("📡 Iniciando monitoramento de partidas...")
    while monitoring:
        try:
            matches = get_live_matches()
            new_matches = []

            for match in matches:
                match_id = match['match_id']
                if match_id in last_saved_ids:
                    continue

                last_saved_ids.add(match_id)

                if match['player1'] in players_to_monitor or match['player2'] in players_to_monitor:
                    new_matches.append(Match(**match))

            if new_matches:
                with app.app_context():
                    db.session.add_all(new_matches)
                    db.session.commit()
                    logger.info(f"💾 {len(new_matches)} nova(s) partida(s) salva(s) no banco de dados.")
            else:
                logger.info("🔍 Nenhuma nova partida com players monitorados.")
        except Exception as e:
            logger.error(f"❌ Erro no monitoramento: {e}")
        time.sleep(20)

# --- Início da thread de monitoramento ---
def start_monitoring_thread():
    global thread, monitoring
    if not monitoring:
        monitoring = True
        thread = Thread(target=monitor_matches)
        thread.daemon = True
        thread.start()
        logger.info("🤖 Bot de monitoramento iniciado automaticamente.")

# --- Interface web ---
@app.route('/')
def index():
    with app.app_context():
        matches = Match.query.order_by(Match.timestamp.desc()).limit(100).all()
    return render_template('index.html', matches=matches, monitoring=monitoring)

@app.route('/start', methods=['POST'])
def start_monitoring():
    start_monitoring_thread()
    return redirect('/')

@app.route('/stop', methods=['POST'])
def stop_monitoring():
    global monitoring
    monitoring = False
    logger.info("🛑 Monitoramento parado manualmente.")
    return redirect('/')

@app.route('/export')
def export_data():
    with app.app_context():
        matches = Match.query.all()
    data = [{
        'timestamp': m.timestamp,
        'player1': m.player1,
        'player2': m.player2,
        'score1': m.score1,
        'score2': m.score2,
        'team1': m.team1,
        'team2': m.team2,
        'stadium': m.stadium,
        'league': m.league,
        'match_time': m.match_time
    } for m in matches]
    df = pd.DataFrame(data)
    filename = f"matches_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = os.path.join("exports", filename)
    os.makedirs("exports", exist_ok=True)
    df.to_excel(filepath, index=False)
    logger.info(f"📁 Dados exportados para {filepath}")
    return f"Exported to {filename}"

# --- Inicialização da aplicação ---
if __name__ == '__main__':
    start_monitoring_thread()  # <- inicia o bot automaticamente
    app.run(host='0.0.0.0', port=5000, debug=True)
