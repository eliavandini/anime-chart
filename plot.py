import json
import plotly.express as px
from datetime import datetime

data = json.load(open("result.json"))
# Convert timestamps to datetime objects
for key, entry in data.items():
    entry["timestamps"] = [datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") for ts in entry["timestamps"]]

# Prepare data for plotting
plot_data = []
for key, entry in data.items():
    for timestamp, value in zip(entry["timestamps"], entry["value"]):
        plot_data.append({"Title": entry["title"], "Timestamp": timestamp, "Value": value})

# Create Plotly figure
fig = px.line(plot_data, x="Timestamp", y="Value", color="Title", markers=True, line_group="Title",
              title="Time-line Graph", labels={"Value": "Y-Axis Label", "Timestamp": "X-Axis Label"},
              template="plotly_white")

# Show the figure
fig.show()