from flask import Blueprint, request, jsonify
from concurrent.futures import ThreadPoolExecutor
from MarketCycle import MarketCycle

mc = MarketCycle()

def create_data_blueprint():
    project_bp = Blueprint('data', __name__, url_prefix='/data')

    @project_bp.route('/stats', methods=['GET'])
    def get_stats():
        symbol = request.args.get('symbol')
        symbols = request.args.get('symbols')
        
        if symbol is not None and symbols is None:
            return jsonify(mc.stats(symbol)), 200
        elif symbols is not None:
            output = {}
            symbols_list = symbols.split(',')
            
            def fetch_stats(symbol):
                return symbol, mc.stats(symbol)
            
            with ThreadPoolExecutor() as executor:
                results = list(executor.map(fetch_stats, symbols_list))
            
            for symbol, stats in results:
                output[symbol] = stats
            
            return jsonify(output), 200

    return project_bp
