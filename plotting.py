import matplotlib.pylab as plt 
import pandas as pd
import matplotlib.dates as mdates

results_df = pd.read_csv("sentiments.csv")
results_df["Signal"] = results_df["Sentiment"].replace(0, pd.NA).ffill().fillna(0).astype(int)  # Forward fill non-zero, fallback to 0 if all preceding are NA

# Performance metrics
results_df['Return'] = results_df['Mean'].pct_change()
results_df['Strategy_Return'] = results_df['Signal'].shift(1) * results_df['Return']
results_df['Cumulative_Return'] = (1 + results_df['Return']).cumprod()
results_df['Cumulative_Strategy_Return'] = (1 + results_df['Strategy_Return']).cumprod()

# Calculate final returns for display
final_market_return = results_df['Cumulative_Return'].iloc[-1]
final_strategy_return = results_df['Cumulative_Strategy_Return'].iloc[-1]

# Print final cumulative returns
print(f"Final Cumulative Market Return: {final_market_return:.2f}")
print(f"Final Cumulative Strategy Return: {final_strategy_return:.2f}")

# Top subplot: Scatter plot of Mean prices with trading signals
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
colors = ["green" if s==1 else "red" if s==-1 else "blue" for s in results_df['Sentiment']]

# Top subplot: Scatter plot of Mean prices with trading signals
results_df['Date'] = pd.to_datetime(results_df['Date']).dt.date
# ax1.scatter(results_df['Date'], results_df['Open'], label='Open', alpha=0.5)
ax1.scatter(results_df['Date'], results_df['Mean'], c=colors, label='Signals')
ax1.set_title('Mean Prices with Sentiment Signals')
ax1.set_ylabel('Mean Price')
ax1.legend()

# Bottom subplot: Cumulative returns
ax2.plot(results_df['Date'], results_df['Cumulative_Return'], label='Market Return', color='blue')
ax2.plot(results_df['Date'], results_df['Cumulative_Strategy_Return'], label='Strategy Return', color='orange')
ax2.set_title('Market Return vs. Strategy Return')
ax2.set_xlabel('Date')
ax2.set_ylabel('Cumulative Return')
ax2.legend()

# Display final cumulative returns on the plot
textstr = f'Final Cumulative Market Return: {final_market_return:.2f}\n'
textstr += f'Final Cumulative Strategy Return: {final_strategy_return:.2f}'
ax2.text(0.05, 0.95, textstr, transform=ax2.transAxes, fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Set x-axis major locator to every 5th entry and rotate date labels for better visibility
ax2.xaxis.set_major_locator(mdates.DayLocator(interval=10))  # Assuming the 'Date' is a datetime object
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

plt.tight_layout()
plt.show()
