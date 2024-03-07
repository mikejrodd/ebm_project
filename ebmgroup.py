import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

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
    axs[0, 0].set_title('Top 10 Countries by Overall Management Score')
    sns.barplot(x='monitor', y='country', data=top_countries_monitor, palette='coolwarm', ax=axs[0, 1])
    axs[0, 1].set_title('Top 10 Countries by Monitoring Management Score')
    sns.barplot(x='target', y='country', data=top_countries_target, palette='coolwarm', ax=axs[1, 0])
    axs[1, 0].set_title('Top 10 Countries by Targets Management Score')
    sns.barplot(x='people', y='country', data=top_countries_people, palette='coolwarm', ax=axs[1, 1])
    axs[1, 1].set_title('Top 10 Countries by People Management Score')
    plt.tight_layout()
    st.pyplot(fig)

    # Germany vs India Box Plot
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(x='country', y='management', data=filtered_df[filtered_df['country'].isin(['Germany', 'India'])], palette='coolwarm', ax=ax)
    ax.set_title('Overall Management Score Distribution: Germany vs. India')
    st.pyplot(fig)

    # # Indian Firms Comparison
    # comparison_df = filtered_df[(filtered_df['country'] == 'India') & ((filtered_df['mne_country'] == 'Germany') | (filtered_df['mne_f'] == 0))]
    # comparison_df['Group'] = comparison_df.apply(lambda x: 'MNE Country = Germany' if x['mne_country'] == 'Germany' else 'MNE_f = 0', axis=1)
    # fig, ax = plt.subplots(figsize=(10, 6))
    # sns.boxplot(x='Group', y='management', data=comparison_df, palette='coolwarm', ax=ax)
    # ax.set_title('Management Score Comparison: Indian Firms with MNE Country = Germany vs MNE_f = 0')
    # st.pyplot(fig)

# Display the app title
st.title('Management Practices Dashboard')

# Call the function to plot visualizations
plot_visualizations(filtered_df)
