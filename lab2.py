import pandas as pd
import boto3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def unload_file(variable):
    s3 = boto3.client('s3')
    with open(f'unloaded_file_{variable}.csv', 'wb') as file:
        s3.download_fileobj('clouduleksandra', f'create_{variable}.csv', file)
    print(f"Complite unload file 'unload_file_'{variable}")
unload_file("EUR")
unload_file("USD")

data_USD = pd.read_csv('create_USD.csv')
data_EUR = pd.read_csv('create_EUR.csv')

fig, ax = plt.subplots(1, 1)

data_USD.plot(y='rate', color='yellow', ax=ax, label='$')
data_EUR.plot(y='rate', color='blue', ax=ax, label='€')

ax.set_xlabel('date')

ax.set_title('Exchange rate of hryvnia against foreign currencies (Dollar and Euro) for 2021')
ax.legend()

plt.savefig("chart.png")
s3 = boto3.client('s3')

with open("chart.png", "rb") as file:
    s3.upload_fileobj(file, "clouduleksandra", "chart.png")

plt.show()
