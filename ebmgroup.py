import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np

# Load the dataset
@st.cache_resource
def load_data():
    return pd.read_csv('wms_manu.csv')

df = load_data()

# Sidebar filters
st.sidebar.header('Filter Options')
exports_threshold = st.sidebar.slider('Exports greater than:', 0, 100, 10)
family_owned = st.sidebar.checkbox('Family owned, family CEO')
many_competitors = st.sidebar.checkbox('Many competitors (Competition = 10)')

# Apply filters
filtered_df = df[df['export'] > exports_threshold]

if family_owned:
    filtered_df = filtered_df[filtered_df['ownership'] == 'Family owned, family CEO']

if many_competitors:
    filtered_df = filtered_df[filtered_df['competition'] == 10]

# Visualization function
def plot_visualizations(filtered_df):
    # Management Scores by Country
    avg_scores = filtered_df.groupby('country')[['management', 'monitor', 'target', 'people']].mean().reset_index()
    top_countries_management = avg_scores.nlargest(20, 'management')
    top_countries_monitor = avg_scores.nlargest(20, 'monitor')
    top_countries_target = avg_scores.nlargest(20, 'target')
    top_countries_people = avg_scores.nlargest(20, 'people')

    # Plotting
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    sns.barplot(x='management', y='country', data=top_countries_management, palette='coolwarm', ax=axs[0, 0])
    axs[0, 0].set_title('Top Countries by Overall Management Score')
    sns.barplot(x='monitor', y='country', data=top_countries_monitor, palette='coolwarm', ax=axs[0, 1])
    axs[0, 1].set_title('Top Countries by Monitoring Management Score')
    sns.barplot(x='target', y='country', data=top_countries_target, palette='coolwarm', ax=axs[1, 0])
    axs[1, 0].set_title('Top Countries by Targets Management Score')
    sns.barplot(x='people', y='country', data=top_countries_people, palette='coolwarm', ax=axs[1, 1])
    axs[1, 1].set_title('Top Countries by People Management Score')
    plt.tight_layout()
    st.pyplot(fig)

    # World Map Visualization
    plot_world_map(filtered_df)

    # Germany vs India Box Plot
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(x='country', y='management', data=filtered_df[filtered_df['country'].isin(['Germany', 'India'])], palette='coolwarm', ax=ax)
    ax.set_title('Overall Management Score Distribution: Germany vs. India')
    st.pyplot(fig)

#map
def plot_world_map(filtered_df):
    avg_scores = filtered_df.groupby('country')['management'].mean().reset_index()
    avg_scores['country'] = avg_scores['country'].replace({'United States': 'United States of America'})
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    world = world.merge(avg_scores, how="left", left_on="name", right_on="country")

    def get_color(value):
        if pd.isnull(value):
            return '#d9d9d9' 
        else:
            intervals = np.linspace(2.5, 3.4, num=10)
            colors = ['#ff0000', '#ff4d4d', '#ff8080', '#ffb3b3', '#ffe6e6', 
                    '#f0fff0', '#90ee90', '#3cb371', '#2e8b57', '#006400']  # Adjusted to green and red gradient
            for i in range(len(intervals) - 1):
                if intervals[i] <= value < intervals[i + 1]:
                    return colors[i]
            return colors[-1] 

    colors = ['#ff0000', '#ff4d4d', '#ff8080', '#ffb3b3', '#ffe6e6', 
            '#f0fff0', '#90ee90', '#3cb371', '#2e8b57', '#006400'] 

    world['color'] = world['management'].apply(get_color)
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    world.boundary.plot(ax=ax, linewidth=1)
    world.plot(color=world['color'], ax=ax)
    legend_handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10) for color in colors]
    legend_labels = ['2.5-2.6', '2.6-2.7', '2.7-2.8', '2.8-2.9', '2.9-3.0', '3.0-3.1', '3.1-3.2', '3.2-3.3', '3.3-3.4', '> 3.4']
    plt.legend(legend_handles, legend_labels, loc='lower right', title='Management Score Range')
    plt.title('World Overall Management Scores')
    st.pyplot(fig)

# Display the app title
st.title('Why Hire Us')

# Call the function to plot visualizations
plot_visualizations(filtered_df)
