# trade_service.py
from firebase_admin import firestore
import yfinance as yf
import datetime
from DataCaching import DataCaching

class TradeService:
    def __init__(self, db):
        self.db = db

    def get_current_price(self, ticker):
        """Fetches the current price for a given ticker symbol using yfinance."""
        try:
            stock = yf.Ticker(ticker)
            current_price = stock.history(period='1d')['Close'][0]
            return float(current_price)
        except Exception as e:
            print(f"Error fetching price for {ticker}: {e}")
            return None

    def buy_trade(self, data):
        qty = data.get('qty')
        ticker = data.get('ticker').upper()
        price = data.get('price')
        project_name = data.get('project')

        if not all([qty, ticker, price, project_name]):
            return {'error': 'Missing required parameters'}, 400

        project_ref = self.db.collection('paper_projects').document(project_name)
        project_doc = project_ref.get()

        if not project_doc.exists:
            return {'error': 'Project not found'}, 404

        project_data = project_doc.to_dict()
        if project_data['cash'] < qty * price:
            return {'error': 'Insufficient funds'}, 400

        project_data['cash'] -= qty * price
        project_ref.update({'cash': project_data['cash']})

        position_ref = self.db.collection('trade_positions').document(f"{project_name}-{ticker}")
        position_doc = position_ref.get()
        if position_doc.exists:
            position_data = position_doc.to_dict()
            current_qty = position_data.get('qty', 0)
            current_cost = position_data.get('avg_cost', 0) * current_qty
            new_qty = current_qty + qty
            new_avg_cost = (current_cost + qty * price) / new_qty
            position_ref.update({'qty': new_qty, 'avg_cost': new_avg_cost, 'last_buy_date': datetime.datetime.now()})
        else:
            position_ref.set({
                'create_date': datetime.datetime.now(),
                'project': project_name,
                'ticker': ticker,
                'qty': qty,
                'avg_cost': price,
                'last_buy_date': datetime.datetime.now(),
                'last_sell_date': None  
            })

        trade_data = {
            'create_date': datetime.datetime.now(),
            'project': project_name,
            'type': 'buy',
            'ticker': ticker,
            'qty': qty,
            'price': price
        }
        self.db.collection('paper_trades').add(trade_data)

        return {
            'qty': qty,
            'value': qty * price,
            'cash': project_data['cash']
        }, 200

    def sell_trade(self, data):
        qty = data.get('qty')
        ticker = data.get('ticker').upper()
        price = data.get('price')
        project_name = data.get('project')

        if not all([qty, ticker, price, project_name]):
            return {'error': 'Missing required parameters'}, 400

        project_ref = self.db.collection('paper_projects').document(project_name)
        project_doc = project_ref.get()

        if not project_doc.exists:
            return {'error': 'Project not found'}, 404

        position_ref = self.db.collection('trade_positions').document(f"{project_name}-{ticker}")
        position_doc = position_ref.get()

        if not position_doc.exists:
            return {'error': 'Ticker not in portfolio'}, 400

        position_data = position_doc.to_dict()

        if position_data['qty'] < qty:
            return {'error': 'Not enough shares to sell'}, 400

        project_data = project_doc.to_dict()
        project_data['cash'] += qty * price
        project_ref.update({'cash': project_data['cash']})

        remaining_qty = position_data['qty'] - qty
        if remaining_qty == 0:
            position_ref.delete()
        else:
            position_ref.update({'qty': remaining_qty, 'last_sell_date': datetime.datetime.now()})

        trade_data = {
            'create_date': datetime.datetime.now(),
            'project': project_name,
            'type': 'sell',
            'ticker': ticker,
            'qty': qty,
            'price': price
        }
        self.db.collection('paper_trades').add(trade_data)

        avg_cost = position_data['avg_cost']
        profit = (price - avg_cost) * qty
        gains_percent = ((price - avg_cost) / avg_cost) * 100 if avg_cost else 0

        return {
            'qty': remaining_qty,
            'value': qty * price,
            'gains': gains_percent,
            'profits': profit,
            'cash': project_data['cash']
        }, 200

    def get_trade_stats(self, project_name):
        if not project_name:
            return {'error': 'Missing "project" parameter'}, 400

        positions = []
        invested_value = 0
        open_value = 0

        try:
            positions_ref = self.db.collection('trade_positions').where('project', '==', project_name)
            positions_docs = positions_ref.stream()

            for doc in positions_docs:
                position_data = doc.to_dict()
                ticker = position_data['ticker']
                qty = position_data['qty']
                avg_cost = position_data['avg_cost']
                current_price = self.get_current_price(ticker)

                if current_price is None:
                    continue

                gains = ((current_price - avg_cost) / avg_cost) * 100
                positions.append({
                    'ticker': ticker,
                    'qty': qty,
                    'avg_cost': avg_cost,
                    'current_price': current_price,
                    'gains': gains
                })
                invested_value += avg_cost * qty
                open_value += current_price * qty

            project_ref = self.db.collection('paper_projects').document(project_name)
            project_doc = project_ref.get()

            if not project_doc.exists:
                return {'error': 'Project not found'}, 404

            project_data = project_doc.to_dict()
            initial_cash = project_data.get('initial_cash', project_data['cash'])

            total_gains_percent = ((project_data['cash'] + open_value - initial_cash) / initial_cash) * 100 if initial_cash else 0
            unrealized_gains_percent = ((open_value - invested_value) / invested_value) * 100 if invested_value else 0

            return {
                'positions': positions,
                'cash': project_data['cash'],
                'invested_value': invested_value,
                'open_value': open_value,
                'gains': total_gains_percent,
                'unrealized_gains': unrealized_gains_percent
            }, 200

        except Exception as e:
            return {'error': str(e)}, 500

    def get_positions(self, project_name):
        if not project_name:
            return {'error': 'Missing "project" parameter'}, 400

        try:
            positions = []
            invested_value = 0
            open_value = 0

            positions_ref = self.db.collection('trade_positions').where('project', '==', project_name)
            positions_docs = positions_ref.stream()

            for doc in positions_docs:
                position_data = doc.to_dict()
                ticker = position_data['ticker']
                qty = position_data['qty']
                avg_cost = position_data['avg_cost']
                current_price = self.get_current_price(ticker)

                if current_price is None:
                    continue

                gains = ((current_price - avg_cost) / avg_cost) * 100
                profit = (current_price - avg_cost) * qty
                positions.append({
                    'ticker': ticker,
                    'qty': qty,
                    'avg_cost': avg_cost,
                    'current_price': current_price,
                    'gains': gains,
                    'profit': profit
                })
                invested_value += avg_cost * qty
                open_value += current_price * qty

            return {
                'positions': positions,
                'invested_value': invested_value,
                'open_value': open_value
            }, 200

        except Exception as e:
            return {'error': str(e)}, 500

    def get_trade_logs(self, project, page, per_page):
        trades_ref = self.db.collection('paper_trades').where('project', '==', project)
        total = len(list(trades_ref.stream()))
        logs = trades_ref.offset((page - 1) * per_page).limit(per_page).stream()
        
        data = [log.to_dict() for log in logs]
        page_count = (total + per_page - 1) // per_page  # Calculating page count

        pagination = {
            'total': total,
            'page_count': page_count,
            'page': page,
            'per_page': per_page
        }

        return {'pagination': pagination, 'data': data}, 200

    def manage_watchlist(self, data):
        project = data.get('project')
        ticker = data.get('ticker')
        action = data.get('action')

        if not project or not action:
            return {'error': 'Missing "project" or "action" parameter'}, 400

        watchlist_ref = self.db.collection('paper_watchlists').document(project)
        watchlist_doc = watchlist_ref.get()

        if watchlist_doc.exists:
            watchlist = watchlist_doc.to_dict().get('tickers', [])
        else:
            watchlist = []

        if action == 'add':
            if not ticker:
                return {'error': 'Missing "ticker" parameter for add action'}, 400
            if ticker not in watchlist:
                watchlist.append(ticker)
        elif action == 'remove':
            if not ticker:
                return {'error': 'Missing "ticker" parameter for remove action'}, 400
            if ticker in watchlist:
                watchlist.remove(ticker)
        elif action == 'list':
            pass
        else:
            return {'error': 'Invalid "action" parameter'}, 400

        watchlist_ref.set({'tickers': watchlist})

        return {'watchlist': watchlist}, 200

    def getMainWatchlist(self):
        response, status = self.manage_watchlist({
            "project": "main",
            "action": "list"
        })
        print(response)
        if "watchlist" not in response:
            print("!!! NO MAIN WATCHLIST FOUND !!!")
            return []
        return response["watchlist"]

    def get_prices(self, tickers):
        if not tickers:
            return {'error': 'Missing "tickers" parameter'}, 400
        
        tickers_list = tickers.split(',')
        prices = {}
        for ticker in tickers_list:
            price = self.get_current_price(ticker)
            if price is not None:
                prices[ticker] = price
        
        return prices, 200
