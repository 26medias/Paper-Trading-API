# trade_blueprint.py
from flask import Blueprint, request, jsonify
from trade_service import TradeService
from DataCaching import DataCaching

def create_trade_blueprint(db):
    trade_bp = Blueprint('trade', __name__, url_prefix='/trade')
    trade_service = TradeService(db)

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
        return jsonify({"status": "ok"}), 200

    @trade_bp.route('/tick', methods=['GET'])
    def tick_data():
        cache = DataCaching(db=db)
        cache.setTickers(trade_service.getMainWatchlist())
        cache.update_data()
        return jsonify({"status": "ok"}), 200

    @trade_bp.route('/chart', methods=['GET'])
    def chart_data():
        cache = DataCaching(db=db)
        cache.setTickers(trade_service.getMainWatchlist())
        cache.chart('NVDA', 'NVDA.png')
        return jsonify({"status": "ok"}), 200

    return trade_bp
