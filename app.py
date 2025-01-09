from turtle import color
from flask import Flask, render_template_string
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

app = Flask(__name__)

# Class and data initialization (same as before)
class Animal:
    def __init__(self, animal_id, species, birth_date, breed, gender):
        self.animal_id = animal_id
        self.species = species
        self.birth_date = birth_date
        self.breed = breed
        self.gender = gender
        self.weight_data = []
        self.feed_data = []

    def add_weight_measurement(self, date, weight):
        self.weight_data.append((date, weight))

    def add_feed_intake(self, date, amount):
        self.feed_data.append((date, amount))

# Initialize data (same as before)
cow1 = Animal(1, 'Cow', '2023-01-01', 'Holstein', 'Female')
cow2 = Animal(2, 'Cow', '2023-02-15', 'Jersey', 'Female')
cow3 = Animal(3, 'Cow', '2023-03-10', 'Ayrshire', 'Female')
cow4 = Animal(4, 'Cow', '2023-01-25', 'Brown Swiss', 'Female')
cow5 = Animal(5, 'Cow', '2023-02-05', 'Guernsey', 'Female')
cow6 = Animal(6, 'Cow', '2023-03-20', 'Milking Shorthorn', 'Female')

animals = [cow1, cow2, cow3, cow4, cow5, cow6]

# Add weight and feed data (same as before)
cow1.add_weight_measurement('2023-03-15', 200)
cow1.add_weight_measurement('2023-04-15', 220)
cow1.add_feed_intake('2023-03-15', 15)
cow1.add_feed_intake('2023-04-15', 18)

cow2.add_weight_measurement('2023-03-15', 180)
cow2.add_weight_measurement('2023-04-15', 205)
cow2.add_feed_intake('2023-03-15', 12)
cow2.add_feed_intake('2023-04-15', 14)

cow3.add_weight_measurement('2023-03-15', 190)
cow3.add_weight_measurement('2023-04-15', 215)
cow3.add_feed_intake('2023-03-15', 16)
cow3.add_feed_intake('2023-04-15', 17)

cow4.add_weight_measurement('2023-03-15', 210)
cow4.add_weight_measurement('2023-04-15', 235)
cow4.add_feed_intake('2023-03-15', 17)
cow4.add_feed_intake('2023-04-15', 19)

cow5.add_weight_measurement('2023-03-15', 175)
cow5.add_weight_measurement('2023-04-15', 195)
cow5.add_feed_intake('2023-03-15', 13)
cow5.add_feed_intake('2023-04-15', 15)

cow6.add_weight_measurement('2023-03-15', 205)
cow6.add_weight_measurement('2023-04-15', 225)
cow6.add_feed_intake('2023-03-15', 16)
cow6.add_feed_intake('2023-04-15', 18)

# Create DataFrame
data = []
for animal in animals:
    data.append({
        'animal_id': animal.animal_id,
        'species': animal.species,
        'birth_date': animal.birth_date,
        'breed': animal.breed,
        'gender': animal.gender,
        'weight_data': animal.weight_data,
        'feed_data': animal.feed_data
    })

df = pd.DataFrame(data)

# Helper functions
def calculate_weight_gain(weight_data):
    weights = [weight for _, weight in weight_data]
    return np.diff(weights)

def create_date_list(weight_data):
    return [date for date, _ in weight_data][1:]

def calculate_feed_efficiency(feed_data, weight_gain):
    feed_amounts = [amount for _, amount in feed_data]
    if np.sum(feed_amounts) > 0:
        return np.sum(weight_gain) / np.sum(feed_amounts)
    return 0

def calculate_average_daily_weight_gain(weight_data):
    weights = [weight for _, weight in weight_data]
    if len(weights) > 1:
        total_weight_gain = weights[-1] - weights[0]
        total_days = (pd.to_datetime(weight_data[-1][0]) - pd.to_datetime(weight_data[0][0])).days
        return total_weight_gain / total_days
    return 0

df['weight_gain'] = df['weight_data'].apply(calculate_weight_gain)
df['dates'] = df['weight_data'].apply(create_date_list)
df['feed_efficiency'] = df.apply(lambda row: calculate_feed_efficiency(row['feed_data'], row['weight_gain']), axis=1)
df['average_daily_weight_gain'] = df['weight_data'].apply(calculate_average_daily_weight_gain)

# Flask Routes
@app.route("/")
def home():
    # Generate visualizations and convert them to base64
    def plot_to_base64(fig):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches='tight')
        buf.seek(0)
        plot_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        buf.close()
        return plot_base64

    # Growth Rate (Line Plot with Background Color)
    fig1, ax1 = plt.subplots(facecolor='#f7e8f0')
    for _, row in df.iterrows():
        ax1.plot(row['dates'], row['weight_gain'], label=f"Animal {row['animal_id']}", linewidth=2)
    ax1.set_title('Growth Rate Over Time', fontsize=14, color='darkblue')
    ax1.set_xlabel('Date', color='purple')
    ax1.set_ylabel('Weight Gain', color='purple')
    ax1.legend()
    growth_rate_plot = plot_to_base64(fig1)

     # Weight Gain for Each Animal (Line Plot)
    fig1, ax1 = plt.subplots(facecolor='#f7e8f0')
    for _, row in df.iterrows():
        dates = [pd.to_datetime(date) for date in row['dates']]
        ax1.plot(dates, row['weight_gain'], label=f"Animal {row['animal_id']}", linewidth=2)
    ax1.set_title('Weight Gain for Each Animal', fontsize=14, color='darkblue')
    ax1.set_xlabel('Date', color='purple')
    ax1.set_ylabel('Weight Gain (kg)', color='purple')
    ax1.legend()
    weight_gain_plot = plot_to_base64(fig1)

    # Feed Efficiency by Breed (Box Plot)
    fig2, ax2 = plt.subplots(facecolor='#e8f0f7')
    sns.boxplot(x='breed', y='feed_efficiency', data=df, palette='coolwarm', ax=ax2)
    ax2.set_title('Feed Efficiency by Breed', fontsize=14, color='darkblue')
    feed_efficiency_breed_plot = plot_to_base64(fig2)

    # Feed Efficiency by Gender (Box Plot)
    fig3, ax3 = plt.subplots(facecolor='#e7f7e8')
    sns.boxplot(x='gender', y='feed_efficiency', data=df, palette='viridis', ax=ax3)
    ax3.set_title('Feed Efficiency by Gender', fontsize=14, color='darkgreen')
    feed_efficiency_gender_plot = plot_to_base64(fig3)

    # Average Daily Weight Gain (Bar Plot)
    fig4, ax4 = plt.subplots(facecolor='#f7f3e8')
    sns.barplot(x=df['animal_id'], y=df['average_daily_weight_gain'], palette='Spectral', ax=ax4)
    ax4.set_title('Average Daily Weight Gain by Animal', fontsize=14, color='darkred')
    ax4.set_xlabel('Animal ID', color='brown')
    ax4.set_ylabel('Average Daily Weight Gain (kg/day)', color='brown')
    avg_daily_gain_plot = plot_to_base64(fig4)

    # Render HTML
    animal_details_html = ""
    for _, row in df.iterrows():
        animal_details_html += f"""
        <div style="border: 2px solid #7c5295; padding: 10px; margin: 10px; background-color: #f0f8ff;">
            <h3 style="color: #2d6187;">Animal ID: {row['animal_id']}</h3>
            <p><strong>Species:</strong> {row['species']}</p>
            <p><strong>Birth Date:</strong> {row['birth_date']}</p>
            <p><strong>Breed:</strong> {row['breed']}</p>
            <p><strong>Gender:</strong> {row['gender']}</p>
            <p><strong>Weight Gain:</strong> {row['weight_gain']}</p>
            <p><strong>Feed Efficiency:</strong> {row['feed_efficiency']}</p>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>farmEase</title>
        <style>
        .weight_feed_graph{{
            display:flex;
            justify-content: center;
            gap:20px;
        }}

         .image_helper{{
            display:flex;
            justify-content: center;
        }}
        .avg_daily_gain{{
            display:flex;
            justify-content: center;
        }}
            body {{
                background-color: #fcf5eb;
                font-family: Arial, sans-serif;
            }}
            h1, h2 {{
                text-align: center;
                color: #7c5295;
            }}
            .content {{
                display: flex;
                justify-content: space-around;
                margin-top: 30px;
            }}
            .left-section, .right-section {{
                width: 45%;
            }}
            .img-section {{
                text-align: center;
                margin-top: 20px;
            }}
            .img-section img {{
                width: 80%;
                height: auto;
                margin: 10px 0;
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <h1>WelCome to FarmEase ProtoType </h1>
        <h1>Animal Data Visualizations</h1>
        <div class="weight_feed_graph">
        <img src="data:image/png;base64,{weight_gain_plot}" alt="Weight Gain for Each Animal"/>
        <img src="data:image/png;base64,{feed_efficiency_breed_plot}" alt="Feed Efficiency by Breed"/>
        </div>

        <h2>Feed Efficiency by Gender</h2>
        <div class="image_helper">
        <img src="data:image/png;base64,{feed_efficiency_gender_plot}" alt="Feed Efficiency by Gender"/>
        </div>
        <h2>Average Daily Weight Gain</h2>
        <div class="avg_daily_gain">
        <img src="data:image/png;base64,{avg_daily_gain_plot}" class="image_helper" alt="Average Daily Weight Gain"/>
        </div>

        <div class="content">
            
            <div class="right-section">
                <h2>Animal Details</h2>
                {animal_details_html}
            </div>
        </div>

    <div class="img-section">
        <h2>Farmer Images</h2>
        <img src="{{ url_for('static', filename='Assets/aunty.jpg') }}" alt="Aunty"> 
        <img src="{{ url_for('static', filename='Assets/farmerUncle.jpg') }}" alt="Farmer Uncle">
    </div>

    <div class="img-section">
        <h2>Animal Image</h2>
        <img src="{{ url_for('static', filename='Assets/cow-animal.jpg') }}" alt="Cow">
    </div>

    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(debug=True)
