import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
from PIL import Image, ImageDraw
import matplotlib.colors as mcolors
from DataCaching import DataCaching

class Generator:
    def __init__(self, db):
        self.data_cache = DataCaching(db)

    def _generate_candlestick_chart(self, ticker, data):
        data['Datetime'] = pd.to_datetime(data['Datetime'], unit='s')
        data.set_index('Datetime', inplace=True)
        data.index.name = 'Date'

        # Define the custom style
        mc = mpf.make_marketcolors(up='#26a69a', down='#ef5350', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc, facecolor='#131722', edgecolor='#131722',
                            gridcolor='#2a2a2a', gridstyle='--')

        # Generate the candlestick chart
        fig, ax = mpf.plot(data, type='candle', style=s, returnfig=True)

        # Hide axis
        ax[0].set_axis_off()

        # Save the plot
        filename = f'{ticker}_candles.png'
        fig.savefig(filename, bbox_inches='tight', pad_inches=0, facecolor='#131722')
        plt.close(fig)

        return filename



    def _generate_status_grid(self, ticker, status):
        def get_value_color(value):
            cmap = mcolors.LinearSegmentedColormap.from_list(
                'value_gradient', [(0, '#31ce53'), (0.5, '#265c99'), (1, '#eb3333')]
            )
            norm = mcolors.Normalize(vmin=0, vmax=100)
            rgb = cmap(norm(value))[:3]
            return tuple(int(c * 255) for c in rgb)

        def get_delta_color(delta):
            print(delta)
            cmap = mcolors.LinearSegmentedColormap.from_list(
                'delta_gradient', [(0, '#eb3333'), (0.5, '#265c99'), (1, '#31ce53')]
            )
            norm = mcolors.Normalize(vmin=-100, vmax=100)
            rgb = cmap(norm(delta))[:3]
            return tuple(int(c * 255) for c in rgb)

        img = Image.new('RGB', (40, 30), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Define the positions on the grid
        positions = [(10 * x, 10 * y) for y in range(3) for x in range(4)]
        values = [
            (status['5d']['delta1'], get_delta_color), (status['1d']['delta1'], get_delta_color), (status['1h']['delta1'], get_delta_color), (status['1min']['delta1'], get_delta_color),
            (status['5d']['delta0'], get_delta_color), (status['1d']['delta0'], get_delta_color), (status['1h']['delta0'], get_delta_color), (status['1min']['delta0'], get_delta_color),
            (status['5d']['value'], get_value_color), (status['1d']['value'], get_value_color), (status['1h']['value'], get_value_color), (status['1min']['value'], get_value_color)
        ]

        for pos, (value, color_func) in zip(positions, values):
            color = color_func(value) if value is not None else (255, 255, 255)
            draw.rectangle([pos, (pos[0] + 10, pos[1] + 10)], fill=color)

        filename = f'{ticker}_status.png'
        img.save(filename)

        return filename



    def status(self, ticker):
        ticker_status = self.data_cache.tickerStatus(ticker)
        if not ticker_status:
            print(f"No data available for {ticker}")
            return None

        data = ticker_status['last_10']
        status = ticker_status['status']

        # Generate the candlestick chart
        candlestick_filename = self._generate_candlestick_chart(ticker, pd.DataFrame(data))

        # Generate the status grid image
        status_grid_filename = self._generate_status_grid(ticker, status)

        return {
            'candles': candlestick_filename,
            'status': status_grid_filename
        }
