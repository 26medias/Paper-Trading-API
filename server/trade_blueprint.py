from flask import Blueprint, request, jsonify, send_file
from trade_service import TradeService
from DataCaching import DataCaching
from Generator import Generator
from datetime import datetime
import pytz


def ts():
    utc_now = datetime.now(pytz.utc)

    # Convert to EST
    est_tz = pytz.timezone('America/New_York')
    est_now = utc_now.astimezone(est_tz)

    # Get the timestamp in milliseconds
    timestamp_ms = int(est_now.timestamp() * 1000)

    return timestamp_ms

def create_trade_blueprint(db):
    trade_bp = Blueprint('trade', __name__, url_prefix='/trade')
    trade_service = TradeService(db)
    generator = Generator(db)

    @trade_bp.route('/buy', methods=['POST'])
    def buy_trade():
        data = request.get_json()
        response, status = trade_service.buy_trade(data)
        return jsonify(response), status

    @trade_bp.route('/sell', methods=['POST'])
    def sell_trade():
        data = request.get_json()
        response, status = trade_service.sell_trade(data)
        return jsonify(response), status

    @trade_bp.route('/stats', methods=['GET'])
    def get_trade_stats():
        project_name = request.args.get('project')
        response, status = trade_service.get_trade_stats(project_name)
        return jsonify(response), status

    @trade_bp.route('/positions', methods=['GET'])
    def get_positions():
        project_name = request.args.get('project')
        response, status = trade_service.get_positions(project_name)
        return jsonify(response), status

    @trade_bp.route('/logs', methods=['GET'])
    def get_trade_logs():
        project = request.args.get('project')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        response, status = trade_service.get_trade_logs(project, page, per_page)
        return jsonify(response), status

    @trade_bp.route('/watchlist', methods=['POST'])
    def manage_watchlist():
        data = request.get_json()
        response, status = trade_service.manage_watchlist(data)
        return jsonify(response), status

    @trade_bp.route('/prices', methods=['GET'])
    def get_prices():
        tickers = request.args.get('tickers')
        response, status = trade_service.get_prices(tickers)
        return jsonify(response), status

    @trade_bp.route('/init', methods=['GET'])
    def init_data():
        cache = DataCaching(db=db)
        cache.setTickers(trade_service.getMainWatchlist())
        cache.init()
        doc_ref = db.collection('paper_settings').document('settings')
        doc_ref.set({
            'refreshed': ts()
        }, merge=True)
        return jsonify({"status": "ok"}), 200

    @trade_bp.route('/tick', methods=['GET'])
    def tick_data():
        cache = DataCaching(db=db)
        cache.setTickers(trade_service.getMainWatchlist())
        cache.update_data()
        doc_ref = db.collection('paper_settings').document('settings')
        doc_ref.set({
            'refreshed': ts()
        }, merge=True)
        return jsonify({"status": "ok"}), 200

    @trade_bp.route('/chart', methods=['GET'])
    def chart_data():
        cache = DataCaching(db=db)
        cache.setTickers(trade_service.getMainWatchlist())
        cache.chart('NVDA', 'NVDA.png')
        return jsonify({"status": "ok"}), 200

    @trade_bp.route('/status', methods=['GET'])
    def status_data():
        ticker = request.args.get('ticker')
        project = request.args.get('project')
        cache = DataCaching(db=db)
        status = cache.tickerStatus(ticker, project)
        return jsonify(status), 200

    @trade_bp.route('/img-candles', methods=['GET'])
    def get_image_candles():
        ticker = request.args.get('ticker')
        image = generator.generate_candlesticks(ticker)
        return send_file(image, mimetype='image/png')

    @trade_bp.route('/img-status', methods=['GET'])
    def get_image_status():
        ticker = request.args.get('ticker')
        image = generator.generate_status(ticker)
        return send_file(image, mimetype='image/png')

    return trade_bp
