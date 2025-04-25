import pandas as pd
import streamlit as st
import math

# 1. DATA LOADING (CACHED FOR PERFORMANCE)
@st.cache_data
def load_item_data():
    data = {
        'Item Name': [f'Product {i}' for i in range(1, 5001)],
        'Main Category': ['Electronics']*2000 + ['Clothing']*2000 + ['Home']*1000,
        'Sub Category 1': ['Phones']*1000 + ['Laptops']*1000 + ['Men']*1000 + ['Women']*1000 + ['Furniture']*500 + ['Decor']*500,
        'Sub Category 2': ['Smartphones']*500 + ['Basic']*500 + ['Gaming']*500 + ['Business']*500 + ['T-Shirts']*500 + ['Jeans']*500 + ['Dresses']*500 + ['Skirts']*500 + ['Chairs']*250 + ['Tables']*250 + ['Art']*250 + ['Lamps']*250,
        'Unit Price': [10 + (i % 500) for i in range(5000)],
        'Item Unit': ['each']*5000
    }
    return pd.DataFrame(data)

# 2. ITEM WIZARD COMPONENT
def show_item_wizard(items_df, add_callback):
    st.title("Item Selection Wizard")

    search_term = st.text_input("🔍 Search items")

    # Initialize filters
    if 'wizard_filters' not in st.session_state:
        st.session_state.wizard_filters = {
            'main_categories': [],
            'sub1_categories': [],
            'sub2_categories': []
        }

    filter_col, items_col = st.columns([3, 7])

    with filter_col:
        st.subheader("Main Categories")
        main_categories = sorted(items_df['Main Category'].dropna().unique().tolist())
        for cat in main_categories:
            if st.checkbox(cat, key=f"main_{cat}", value=cat in st.session_state.wizard_filters['main_categories']):
                if cat not in st.session_state.wizard_filters['main_categories']:
                    st.session_state.wizard_filters['main_categories'].append(cat)
            else:
                if cat in st.session_state.wizard_filters['main_categories']:
                    st.session_state.wizard_filters['main_categories'].remove(cat)

        st.subheader("Sub Category 1")
        if st.session_state.wizard_filters['main_categories']:
            sub1_options = items_df[items_df['Main Category'].isin(st.session_state.wizard_filters['main_categories'])]['Sub Category 1'].dropna().unique().tolist()
        else:
            sub1_options = items_df['Sub Category 1'].dropna().unique().tolist()
        for sub1 in sorted(sub1_options):
            if st.checkbox(sub1, key=f"sub1_{sub1}", value=sub1 in st.session_state.wizard_filters['sub1_categories']):
                if sub1 not in st.session_state.wizard_filters['sub1_categories']:
                    st.session_state.wizard_filters['sub1_categories'].append(sub1)
            else:
                if sub1 in st.session_state.wizard_filters['sub1_categories']:
                    st.session_state.wizard_filters['sub1_categories'].remove(sub1)

        st.subheader("Sub Category 2")
        if st.session_state.wizard_filters['sub1_categories']:
            sub2_options = items_df[items_df['Sub Category 1'].isin(st.session_state.wizard_filters['sub1_categories'])]['Sub Category 2'].dropna().unique().tolist()
        else:
            sub2_options = items_df['Sub Category 2'].dropna().unique().tolist()
        for sub2 in sorted(sub2_options):
            if st.checkbox(sub2, key=f"sub2_{sub2}", value=sub2 in st.session_state.wizard_filters['sub2_categories']):
                if sub2 not in st.session_state.wizard_filters['sub2_categories']:
                    st.session_state.wizard_filters['sub2_categories'].append(sub2)
            else:
                if sub2 in st.session_state.wizard_filters['sub2_categories']:
                    st.session_state.wizard_filters['sub2_categories'].remove(sub2)

    with items_col:
        filtered_items = items_df.copy()

        # Apply filters
        if st.session_state.wizard_filters['main_categories']:
            filtered_items = filtered_items[filtered_items['Main Category'].isin(st.session_state.wizard_filters['main_categories'])]
        if st.session_state.wizard_filters['sub1_categories']:
            filtered_items = filtered_items[filtered_items['Sub Category 1'].isin(st.session_state.wizard_filters['sub1_categories'])]
        if st.session_state.wizard_filters['sub2_categories']:
            filtered_items = filtered_items[filtered_items['Sub Category 2'].isin(st.session_state.wizard_filters['sub2_categories'])]
        if search_term:
            filtered_items = filtered_items[filtered_items['Item Name'].str.contains(search_term, case=False)]

        # PAGINATION
        PAGE_SIZE = 50
        total_items = len(filtered_items)
        total_pages = max(1, math.ceil(total_items / PAGE_SIZE))
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1

        start_idx = (st.session_state.current_page - 1) * PAGE_SIZE
        end_idx = min(start_idx + PAGE_SIZE, total_items)

        st.markdown(f"**Showing items {start_idx + 1}-{end_idx} of {total_items}**")

        # PAGINATION CONTROLS (compact and horizontal)
        with st.container():
            left_space, nav_col1, nav_col2, page_buttons_col, nav_col3, nav_col4, right_space = st.columns([1, 1, 1, 5, 1, 1, 1])

            with nav_col1:
                if st.button("⏮", key="first_page"):
                    st.session_state.current_page = 1
                    st.rerun()
            with nav_col2:
                if st.button("◀", key="prev_page"):
                    if st.session_state.current_page > 1:
                        st.session_state.current_page -= 1
                        st.rerun()

            with page_buttons_col:
                pg_btn_cols = st.columns(min(total_pages, 5))
                max_visible_pages = 5
                half_visible = max_visible_pages // 2
                start_page = max(1, st.session_state.current_page - half_visible)
                end_page = min(total_pages, start_page + max_visible_pages - 1)
                if end_page - start_page + 1 < max_visible_pages:
                    start_page = max(1, end_page - max_visible_pages + 1)

                for i, p in enumerate(range(start_page, end_page + 1)):
                    with pg_btn_cols[i]:
                        if st.button(str(p), key=f"page_{p}"):
                            st.session_state.current_page = p
                            st.rerun()

            with nav_col3:
                if st.button("▶", key="next_page"):
                    if st.session_state.current_page < total_pages:
                        st.session_state.current_page += 1
                        st.rerun()
            with nav_col4:
                if st.button("⏭", key="last_page"):
                    st.session_state.current_page = total_pages
                    st.rerun()

        # DISPLAY ITEMS
        for idx in range(start_idx, end_idx):
            row = filtered_items.iloc[idx]
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"**{row['Item Name']}**  \n"
                            f"*{row['Main Category']} > {row['Sub Category 1']} > {row['Sub Category 2']}*  \n"
                            f"₹{row['Unit Price']:.2f} per {row['Item Unit']}")
            with col2:
                if st.button("Add", key=f"add_{idx}"):
                    add_callback(row['Item Name'])
                    st.rerun()

# 3. APP ENTRY POINT
if __name__ == "__main__":
    def handle_add_item(item_name):
        st.success(f"Added: {item_name}")
        if 'selected_items' not in st.session_state:
            st.session_state.selected_items = []
        st.session_state.selected_items.append(item_name)

    df = load_item_data()
    show_item_wizard(df, handle_add_item)

    if 'selected_items' in st.session_state and st.session_state.selected_items:
        st.subheader("Your Selections")
        for item in st.session_state.selected_items:
            st.write(f"- {item}")
