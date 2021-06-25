import top_down
import utility
import pandas as pd

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    nba = pd.read_csv('basketball.csv')
    nba = top_down.SeasonData(nba)
    nba.process_data()
    market_spread = pd.read_csv('bbMarketSpread.csv')
    alt_lines = top_down.AlternateLines(nba.season, market_spread, sport='Basketball', method='Gaussian', center=None)
    alt_lines.fit()
    alt_lines.plot_alt_lines()
    print(alt_lines.market_spread)

