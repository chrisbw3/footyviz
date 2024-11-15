import streamlit as st
import pandas as pd
import os
import plotly.express as px
import io

st.set_page_config(layout='wide', initial_sidebar_state='expanded')
logo = '/Users/christiangentry/Documents/Data_projects/footy/Footy USA logo/fulllogo_transparent_nobuffer.png'
st.sidebar.image(logo, width=150)

@st.cache_data()
def retrieve_dataset(file):
    if file is not None:
        file_extension = os.path.splitext(file.name)[1].lower()
        if file_extension == '.csv':
            return pd.read_csv(file)
        elif file_extension == '.xlsx':
            return pd.read_excel(file)
        elif file_extension =='.json':
            return pd.read_json(file)
        else:
            st.warning("Unsupported file type uploaded.")
            return None
    return None

st.title("FootyViz")
st.write("Customized stats visualizing personal data.")

st.sidebar.markdown("""
[A branch of Footy USA.](https://x.com/_footyusa) 
- Upload Dataset
- Select Chart Style
- Plot Axis Values
""")

file = st.sidebar.file_uploader(label="Upload Dataset", type=['csv', 'xlsx'], accept_multiple_files=False)
df = retrieve_dataset(file)

c1, c2 = st.columns(2)

with c1:
    if df is not None:
        # Dataset is available, proceed with selections
        cols = df.columns.tolist()

        # Select first column for the x-axis (qualitative or quantitative)
        selected_col1 = st.selectbox("Select first value (qualitative or quantitative):", cols)
        remaining_cols = [col for col in cols if col != selected_col1]
        
        # Select second column for the y-axis (qualitative or quantitative)
        selected_col2 = st.selectbox("Select second value (qualitative or quantitative):", remaining_cols)

        # Determine the types of selected columns (numeric or non-numeric)
        col1_is_numeric = pd.api.types.is_numeric_dtype(df[selected_col1])
        col2_is_numeric = pd.api.types.is_numeric_dtype(df[selected_col2])

        # --- Checkbox for filter visibility ---
        f1 = st.checkbox(label=f"Do you want to filter by {selected_col1}?", value=False)
        f2 = st.checkbox(label=f"Do you want to filter by {selected_col2}?", value=False)

        filtered_data = df.copy()

        # --- Remove rows with NaN or 0 values for selected columns ---
        filtered_data = filtered_data[filtered_data[selected_col1].notna() & (filtered_data[selected_col1] != 0)]
        filtered_data = filtered_data[filtered_data[selected_col2].notna() & (filtered_data[selected_col2] != 0)]

        # --- Filter for selected_col1 ---
        if f1:  # Only show filter for selected_col1 if f1 is True
            if col1_is_numeric:
                # If the column is numeric, show a range slider
                minv1 = df[selected_col1].min()
                maxv1 = df[selected_col1].max()
                selected_col1_filter = st.slider(f"Filter {selected_col1} range:", min_value=minv1, max_value=maxv1, value=(minv1, maxv1))
                filtered_data = filtered_data[filtered_data[selected_col1].between(selected_col1_filter[0], selected_col1_filter[1])]
            else:
                # If the column is non-numeric, show a select box to filter by value
                selected_col1_filter = st.selectbox(f"Filter {selected_col1} by value:", df[selected_col1].unique())
                filtered_data = filtered_data[filtered_data[selected_col1] == selected_col1_filter]

        # --- Filter for selected_col2 ---
        if f2:  # Only show filter for selected_col2 if f2 is True
            if col2_is_numeric:
                # If the column is numeric, show a range slider
                minv2 = df[selected_col2].min()
                maxv2 = df[selected_col2].max()
                selected_col2_filter = st.slider(f"Filter {selected_col2} range:", min_value=minv2, max_value=maxv2, value=(minv2, maxv2))
                filtered_data = filtered_data[filtered_data[selected_col2].between(selected_col2_filter[0], selected_col2_filter[1])]
            else:
                # If the column is non-numeric, show a select box to filter by value
                selected_col2_filter = st.selectbox(f"Filter {selected_col2} by value:", df[selected_col2].unique())
                filtered_data = filtered_data[filtered_data[selected_col2] == selected_col2_filter]

        # --- Sorting Widget ---
        # Only allow sorting by numeric columns
        numeric_cols = [col for col in cols if pd.api.types.is_numeric_dtype(df[col])]
        
        sort_data = st.checkbox("Do you want to sort the data?", value=False)  # Add a checkbox for sorting
        if sort_data:  # If sorting is enabled, show sorting widgets
            if numeric_cols:  # If there are numeric columns
                sort_column = st.selectbox("Select column to sort by:", numeric_cols)
                sort_order = st.selectbox("Select sorting order:", ["Ascending", "Descending"])

                # Apply sorting based on user's selection
                if sort_column in filtered_data.columns:
                    if sort_order == "Ascending":
                        filtered_data = filtered_data.sort_values(by=sort_column, ascending=True)
                    else:
                        filtered_data = filtered_data.sort_values(by=sort_column, ascending=False)

    else:
        # If no dataset is uploaded, display a warning message
        st.warning("Please upload a dataset to proceed.")
    show_percentiles = st.checkbox("Show 90th and 10th Percentile Lines", value=False)

    chart_types = ['Area Chart', 'Bar Chart', 'Line Chart', 'Scatter Plot']
    selected_chart = st.selectbox("Select Chart Type:", chart_types)

with c2:
    if df is not None and selected_chart:
        try:
            # **Recalculate percentiles on filtered data**
            if col2_is_numeric and not filtered_data.empty:
                percentile_90 = filtered_data[selected_col2].quantile(0.9)
                percentile_10 = filtered_data[selected_col2].quantile(0.1)

                # Create the chart
                if selected_chart == 'Area Chart':
                    chart_title = st.text_input(label="Enter Chart Title")
                    fig = px.area(filtered_data, x=selected_col1, y=selected_col2, title=f"{chart_title}")
                elif selected_chart == 'Bar Chart':
                    chart_title = st.text_input(label="Enter Chart Title")
                    fig = px.bar(filtered_data, x=selected_col1, y=selected_col2, title=f"{chart_title}")
                elif selected_chart == 'Line Chart':
                    chart_title = st.text_input(label="Enter Chart Title")
                    fig = px.line(filtered_data, x=selected_col1, y=selected_col2, title=f"{chart_title}")
                elif selected_chart == 'Scatter Plot':
                    chart_title = st.text_input(label="Enter Chart Title")
                    fig = px.scatter(filtered_data, x=selected_col1, y=selected_col2, title=f"{chart_title}")
                else:
                    st.warning("Invalid chart type selected.")

                # Add horizontal lines if checkbox is selected
                if show_percentiles:
                    # Add the 90th percentile (red) and 10th percentile (blue) horizontal lines
                    fig.add_hline(y=percentile_90, line=dict(color="red", dash="dash"), annotation_text="90th Percentile", annotation_position="top right")
                    fig.add_hline(y=percentile_10, line=dict(color="blue", dash="dash"), annotation_text="10th Percentile", annotation_position="bottom right")

                # Display the chart
                st.plotly_chart(fig)

                # Add button to download the chart as PNG
                if st.sidebar.button("Generate Chart as PNG"):
                    # Save the chart as PNG to a BytesIO buffer (this requires Kaleido)
                    img_buffer = io.BytesIO()
                    fig.write_image(img_buffer, format="png")
                    img_buffer.seek(0)  # Reset buffer position to the start

                    # Provide a download button to download the PNG
                    st.sidebar.download_button(
                        label="Download PNG",
                        data=img_buffer,
                        file_name="chart.png",
                        mime="image/png",
                    )

            else:
                st.warning("Selected column for the y-axis is not numeric or data is empty.")

        except TypeError as e:
            # Display warning if there's a type error, e.g., mismatched data types
            st.warning(f"Error generating chart: {e}.")
