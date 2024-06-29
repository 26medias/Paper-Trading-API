import matplotlib.pyplot as plt

class DataChart:
    def __init__(self, data):
        self.data = data

    def plot_subplots(self, indicators_list, output_filename='image.png'):
        n_plots = len(indicators_list)

        fig, axes = plt.subplots(n_plots, 1, figsize=(14, 7 * n_plots), sharex=True)
        
        # Plot the price and the first set of indicators on the first axis
        axes[0].plot(self.data.index, self.data['Close'], label='Close Price')
        if indicators_list[0]:
            for indicator in indicators_list[0]:
                if isinstance(indicator, str):
                    axes[0].plot(self.data.index, self.data[indicator], label=indicator)
        axes[0].set_title('Close Price and Indicators')
        axes[0].set_ylabel('Price')
        axes[0].legend()
        axes[0].grid()
        
        # Plot each set of indicators on separate axes
        for i, indicators in enumerate(indicators_list[1:]):
            for indicator in indicators:
                if isinstance(indicator, str):
                    axes[i+1].plot(self.data.index, self.data[indicator], label=indicator)
                elif isinstance(indicator, (int, float)):
                    axes[i+1].axhline(y=indicator, color='r', linestyle='--', label=f'{indicator}')
            axes[i+1].set_title(f'Indicators: {", ".join([str(ind) for ind in indicators if isinstance(ind, str)])}')
            axes[i+1].set_ylabel('Value')
            axes[i+1].legend()
            axes[i+1].grid()
        
        plt.xlabel('Date')
        plt.savefig(output_filename)
        plt.close()
