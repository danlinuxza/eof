import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Title of the Streamlit app
st.title('Technology End-of-Life Information Viewer')

# List of technologies and their respective API endpoints
technologies = {
    "Docker Engine": "https://endoflife.date/api/docker-engine.json",
    "Eclipse Temurin": "https://endoflife.date/api/eclipse-temurin.json",
    "Keycloak": "https://endoflife.date/api/keycloak.json",
    "Nuxt": "https://endoflife.date/api/nuxt.json",
    "Spring Boot": "https://endoflife.date/api/spring-boot.json",
    "Vuetify": "https://endoflife.date/api/vuetify.json",
    "Proxmox": "https://endoflife.date/api/v1/products/proxmox-ve"
}

# Dropdown menu for selecting a technology
selected_technology = st.selectbox('Select Technology', list(technologies.keys()))

# URL to fetch the JSON data for the selected technology
json_url = technologies[selected_technology]

# Check if the selected technology is Proxmox
if selected_technology == "Proxmox":
    try:
        # Fetch the JSON data for Proxmox
        response = requests.get(technologies["Proxmox"])
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()

        # Display the Proxmox-specific data
        st.subheader(f'Information for {selected_technology}')
        for item in data:
            st.write(f"**Product:** {item.get('product', 'N/A')}")
            st.write(f"**Version:** {item.get('version', 'N/A')}")
            st.write(f"**Release Date:** {item.get('releaseDate', 'N/A')}")
            st.write(f"**End-of-Life Date:** {item.get('eol', 'N/A')}")
            st.write("---")

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while fetching the JSON data for Proxmox: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

else:
    try:
        # Fetch the JSON data for other technologies
        response = requests.get(json_url)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()

        # Convert JSON data to a DataFrame for easier manipulation
        df = pd.DataFrame(data)

        # Create a dropdown menu for selecting a version of the selected technology
        versions = df['cycle'].tolist()
        selected_version = st.selectbox('Select Version', versions)

        # Filter the DataFrame for the selected version
        selected_data = df[df['cycle'] == selected_version]

        # Display information about the selected version
        if not selected_data.empty:
            st.subheader(f'Information for {selected_technology} Version {selected_version}')
            for column in selected_data.columns:
                st.write(f"**{column.capitalize()}:** {selected_data.iloc[0][column]}")
        else:
            st.error(f"No data found for version {selected_version}")

        # Add a chart to display all versions and highlight those with EOL set to true
        st.subheader(f'End-of-Life Status for {selected_technology}')
        df['eol'] = df['eol'].astype(bool)  # Ensure EOL is treated as a boolean
        df['EOL Status'] = df['eol'].apply(lambda x: 'EOL' if x else 'Supported')

        fig = px.bar(df, x='cycle', y='releaseDate', color='EOL Status', 
                     title=f'EOL Status for {selected_technology}',
                     labels={'cycle': 'Version', 'releaseDate': 'Release Date'},
                     color_discrete_map={'EOL': 'red', 'Supported': 'green'})

        st.plotly_chart(fig)

    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while fetching the JSON data: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
