import yfinance

df = yfinance.download('AAPL', start='2024-01-01', end='2024-01-16')
df.to_csv('AAPL24.csv')


