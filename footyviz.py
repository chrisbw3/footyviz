import streamlit as st
import pandas as pd
import os
import plotly.express as px
import io

st.set_page_config(layout='wide', initial_sidebar_state='expanded')
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
        elif file_extension =='.json':
            return pd.read_json(file)
        else:
            st.warning("Unsupported file type uploaded.")
            return None
    return None

st.title("FootyViz")
st.write("Customized stats visualizing personal data. Please read the disclaimer on the sidebar before expanding the app below.")

st.sidebar.markdown("""
[A branch of Footy USA.](https://x.com/_footyusa) 
- Upload Dataset
- Select Chart Style
- Plot Axis Values
""")

st.sidebar.warning('''DISCLAIMER: To ensure app runs correctly, make sure datasets contain columns "Player" and "Team".''')

file = st.sidebar.file_uploader(label="Upload Dataset", type=['csv', 'xlsx'], accept_multiple_files=False)
df = retrieve_dataset(file)
with st.expander("Expand to view the app content", expanded=False):
    c1, c2 = st.columns(2)

    with c1:
        if df is not None:
            cols = df.columns.tolist()
            selected_col1 = st.selectbox("Select first value (qualitative or quantitative):", cols)
            remaining_cols = [col for col in cols if col != selected_col1]
            selected_col2 = st.selectbox("Select second value (qualitative or quantitative):", remaining_cols)

            col1_is_numeric = pd.api.types.is_numeric_dtype(df[selected_col1])
            col2_is_numeric = pd.api.types.is_numeric_dtype(df[selected_col2])

            apply_filters = st.checkbox("Enable Filters", value=False, key="apply_filters_checkbox")
            filtered_data = df.copy()

            if apply_filters:
                filter_col1 = st.selectbox("Select first column to filter by:", cols, key="filter_col1_selectbox")
                filter_col2 = st.selectbox("Select second column to filter by:", cols, key="filter_col2_selectbox")
                filter_col1_is_numeric = pd.api.types.is_numeric_dtype(df[filter_col1])
                filter_col2_is_numeric = pd.api.types.is_numeric_dtype(df[filter_col2])

                filtered_data = filtered_data[filtered_data[selected_col1].notna() & (filtered_data[selected_col1] != 0)]
                filtered_data = filtered_data[filtered_data[selected_col2].notna() & (filtered_data[selected_col2] != 0)]

                team_column_exists = 'Team' in df.columns

                apply_filter_col1 = st.checkbox(f"Apply filter for {filter_col1}?", value=False, key=f"filter_col1_checkbox_{filter_col1}")
                if apply_filter_col1:
                    if filter_col1_is_numeric:
                        minv1 = df[filter_col1].min()
                        maxv1 = df[filter_col1].max()
                        selected_filter1_range = st.slider(f"Filter {filter_col1} range:", min_value=minv1, max_value=maxv1, value=(minv1, maxv1), key=f"filter1_slider_{filter_col1}")
                        filtered_data = filtered_data[filtered_data[filter_col1].between(selected_filter1_range[0], selected_filter1_range[1])]
                    else:
                        selected_filter1_values = st.multiselect(f"Filter {filter_col1} by values:", df[filter_col1].unique(), default=df[filter_col1].unique(), key=f"filter1_multiselect_{filter_col1}")
                        filtered_data = filtered_data[filtered_data[filter_col1].isin(selected_filter1_values)]

                apply_filter_col2 = st.checkbox(f"Apply filter for {filter_col2}?", value=False, key=f"filter_col2_checkbox_{filter_col2}")
                if apply_filter_col2:
                    if filter_col2_is_numeric:
                        minv2 = df[filter_col2].min()
                        maxv2 = df[filter_col2].max()
                        selected_filter2_range = st.slider(f"Filter {filter_col2} range:", min_value=minv2, max_value=maxv2, value=(minv2, maxv2), key=f"filter2_slider_{filter_col2}")
                        filtered_data = filtered_data[filtered_data[filter_col2].between(selected_filter2_range[0], selected_filter2_range[1])]
                    else:
                        selected_filter2_values = st.multiselect(f"Filter {filter_col2} by values:", df[filter_col2].unique(), default=df[filter_col2].unique(), key=f"filter2_multiselect_{filter_col2}")
                        filtered_data = filtered_data[filtered_data[filter_col2].isin(selected_filter2_values)]

                if team_column_exists:
                    selected_teams = st.multiselect("Select teams to filter by:", df['Team'].unique(), default=df['Team'].unique(), key="team_filter_multiselect")
                    if selected_teams:
                        filtered_data = filtered_data[filtered_data['Team'].isin(selected_teams)]

                sort_column = st.selectbox("Select column to sort by:", [selected_col1, selected_col2], index=1, key="sort_column_selectbox")
                sort_order = st.selectbox("Select sorting order:", ["Ascending", "Descending"], key="sort_order_selectbox")

                if sort_column in filtered_data.columns:
                    if sort_order == "Ascending":
                        filtered_data = filtered_data.sort_values(by=sort_column, ascending=True)
                    else:
                        filtered_data = filtered_data.sort_values(by=sort_column, ascending=False)

            else:
                filtered_data = df.copy()

        else:
            st.warning("Please upload a dataset to proceed.")

        show_percentiles = st.checkbox("Show 90th and 10th Percentile Lines", value=False, key="percentile_lines_checkbox")

        chart_types = ['Area Chart', 'Bar Chart', 'Line Chart', 'Scatter Plot']
        selected_chart = st.selectbox("Select Chart Type:", chart_types, key="chart_type_selectbox")

    with c2:
        if df is not None and selected_chart:
            try:
                if col2_is_numeric and not filtered_data.empty:
                    percentile_90 = filtered_data[selected_col2].quantile(0.9)
                    percentile_10 = filtered_data[selected_col2].quantile(0.1)

                    if selected_chart == 'Area Chart':
                        chart_title = st.text_input(label="Enter Chart Title", key="chart_title_input")
                        fig = px.area(filtered_data, x=selected_col1, y=selected_col2, title=f"{chart_title}", color='Team', hover_data={'Player': True})
                    elif selected_chart == 'Bar Chart':
                        chart_title = st.text_input(label="Enter Chart Title", key="chart_title_input")
                        fig = px.bar(filtered_data, x=selected_col1, y=selected_col2, title=f"{chart_title}", color='Team', hover_data={'Player': True})
                    elif selected_chart == 'Line Chart':
                        chart_title = st.text_input(label="Enter Chart Title", key="chart_title_input")
                        fig = px.line(filtered_data, x=selected_col1, y=selected_col2, title=f"{chart_title}", color='Team', hover_data={'Player': True})
                    elif selected_chart == 'Scatter Plot':
                        chart_title = st.text_input(label="Enter Chart Title", key="chart_title_input")
                        fig = px.scatter(filtered_data, x=selected_col1, y=selected_col2, title=f"{chart_title}", color='Team', hover_data={'Player': True})
                    else:
                        st.warning("Invalid chart type selected.")

                    if show_percentiles:
                        fig.add_hline(y=percentile_90, line=dict(color="red", dash="dash"), annotation_text="90th Percentile", annotation_position="top right")
                        fig.add_hline(y=percentile_10, line=dict(color="blue", dash="dash"), annotation_text="10th Percentile", annotation_position="bottom right")

                    st.plotly_chart(fig)

                    if st.sidebar.button("Generate Chart as PNG"):
                        img_buffer = io.BytesIO()
                        fig.write_image(img_buffer, format="png")
                        img_buffer.seek(0)

                        st.sidebar.download_button(
                            label="Download PNG",
                            data=img_buffer,
                            file_name="chart.png",
                            mime="image/png",
                        )

                else:
                    st.warning("Selected column for the y-axis is not numeric or data is empty.")

            except TypeError as e:
                st.warning(f"Error generating chart: {e}.")
