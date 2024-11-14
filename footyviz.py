import streamlit as st
import pandas as pd
import os
import plotly.express as px
import io

st.set_page_config(initial_sidebar_state='expanded')
logo = 'fulllogo_transparent_nobuffer.png'
st.sidebar.image(logo, width=150)


@st.cache_data()
def retrieve_dataset(file):
    if file is not None:
        file_extension = os.path.splitext(file.name)[1].lower()
        if file_extension == '.csv':
            return pd.read_csv(file)
        elif file_extension == '.xlsx':
            return pd.read_excel(file)
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

        # --- Filter for selected_col1 ---
        if col1_is_numeric:
            # If the column is numeric, show a range slider
            minv1 = df[selected_col1].min()
            maxv1 = df[selected_col1].max()
            selected_col1_filter = st.slider(f"Filter {selected_col1} range:", min_value=minv1, max_value=maxv1, value=(minv1, maxv1))
            filtered_data = df[df[selected_col1].between(selected_col1_filter[0], selected_col1_filter[1])]
        else:
            # If the column is non-numeric, show a select box to filter by value
            selected_col1_filter = st.selectbox(f"Filter {selected_col1} by value:", df[selected_col1].unique())
            filtered_data = df[df[selected_col1] == selected_col1_filter]

        # --- Filter for selected_col2 ---
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

        # Add an option to toggle the visibility of the horizontal lines (percentiles)
        show_percentiles = st.checkbox("Show 90th and 10th Percentile Lines", value=False)

        chart_types = ['Area Chart', 'Bar Chart', 'Line Chart', 'Scatter Plot']
        selected_chart = st.selectbox("Select Chart Type:", chart_types)

    else:
        # If no dataset is uploaded, display a warning message
        st.warning("Please upload a dataset to proceed.")

with c2:
    if df is not None and selected_chart:
        try:
            # Calculate the 90th and 10th percentiles of the selected numeric column (filtered_data)
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
            if st.sidebar.button("Generate and Download Chart as PNG"):
                # Save the chart as PNG to a BytesIO buffer (this requires Kaleido)
                img_buffer = io.BytesIO()
                fig.write_image(img_buffer, format="png")
                img_buffer.seek(0)  # Reset buffer position to the start

                # Provide a download button to download the PNG
                st.sidebar.download_button(
                    label="Download Chart as PNG",
                    data=img_buffer,
                    file_name="chart.png",
                    mime="image/png",
                )

        except TypeError as e:
            # Display warning if there's a type error, e.g., mismatched data types
            st.warning(f"Error generating chart: {e}. Please ensure that the selected columns are of appropriate data types for the chosen chart.")
    elif df is None:
        # If no dataset is uploaded, ask for it in the chart section
        st.warning("Please upload a dataset to view or generate a chart.")
    else:
        st.warning("Please select a chart type to view a graph.")
