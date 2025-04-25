import pandas as pd
import streamlit as st
import math

# 1. DATA LOADING (CACHED FOR PERFORMANCE)
@st.cache_data
def load_item_data():
    """Load your item data here."""
    # Sample data - REPLACE THIS WITH YOUR ACTUAL DATA LOADING CODE
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
def show_item_wizard(items_df, add_callback, close_callback=None):
    """Displays the item selection wizard with pagination row above close button"""
    
    # CSS Styling
    st.markdown("""
    <style>
        .wizard-container {
            border: 1px solid #ddd;
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 1rem 0;
            background-color: #f8f9fa;
        }
        .filter-section {
            background-color: #f0f2f6;
            padding: 0.5rem;
            border-radius: 0.3rem;
            margin-bottom: 0.5rem;
        }
        .item-card {
            padding: 0.7rem;
            margin: 0.3rem 0;
            border: 1px solid #ddd;
            border-radius: 0.3rem;
            background-color: white;
        }
        .pagination-row {
            display: flex;
            justify-content: center;
            gap: 0.2rem;
            margin-bottom: 0.5rem;
        }
        .pagination-btn {
            padding: 0.25rem 0.5rem;
            border: 1px solid #ddd;
            background: white;
            cursor: pointer;
            min-width: 2rem;
            text-align: center;
            border-radius: 0.25rem;
        }
        .pagination-btn:hover {
            background: #f0f0f0;
        }
        .pagination-btn.active {
            background: #4CAF50;
            color: white;
            border-color: #4CAF50;
            font-weight: bold;
        }
        .results-info {
            text-align: center;
            margin: 0.5rem 0;
            font-size: 0.9rem;
            color: #666;
        }
        .close-btn-container {
            display: flex;
            justify-content: flex-end;
            margin-top: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='wizard-container'>", unsafe_allow_html=True)
        st.markdown("#### Item Selection Wizard")
        
        # Two column layout (filters | items)
        filter_col, items_col = st.columns([3, 7])

        # FILTERS COLUMN (left) - Keep your existing filter code
        with filter_col:
            # ... (keep all your existing filter code) ...

        # ITEMS COLUMN (right) - Keep your existing items display code
        with items_col:
            # ... (keep your existing items display code) ...

        # PAGINATION ROW (above close button)
        st.markdown("<div class='pagination-row'>", unsafe_allow_html=True)
        
        # Create columns for each pagination control
        cols = st.columns(8)  # Adjust number based on how many buttons you have
        
        with cols[0]:
            if st.button("⏮ First", key="first_page", use_container_width=True):
                st.session_state.current_page = 1
                st.rerun()
        
        with cols[1]:
            if st.button("◀ Prev", key="prev_page", use_container_width=True):
                if st.session_state.current_page > 1:
                    st.session_state.current_page -= 1
                    st.rerun()
        
        # Page number buttons
        max_visible_pages = 3  # Reduced to fit better in the row
        half_visible = max_visible_pages // 2
        start_page = max(1, st.session_state.current_page - half_visible)
        end_page = min(total_pages, start_page + max_visible_pages - 1)
        
        if end_page - start_page + 1 < max_visible_pages:
            start_page = max(1, end_page - max_visible_pages + 1)
        
        for i, p in enumerate(range(start_page, end_page + 1), start=2):
            with cols[i]:
                if st.button(str(p), key=f"page_{p}", 
                           type="primary" if p == st.session_state.current_page else "secondary",
                           use_container_width=True):
                    st.session_state.current_page = p
                    st.rerun()
        
        with cols[-2]:
            if st.button("Next ▶", key="next_page", use_container_width=True):
                if st.session_state.current_page < total_pages:
                    st.session_state.current_page += 1
                    st.rerun()
        
        with cols[-1]:
            if st.button("Last ⏭", key="last_page", use_container_width=True):
                st.session_state.current_page = total_pages
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close pagination-row
        
        # Results info
        st.markdown(
            f"<div class='results-info'>Page {st.session_state.current_page} of {total_pages} • {total_items} items</div>", 
            unsafe_allow_html=True
        )
        
        # CLOSE BUTTON (below pagination)
        st.markdown("<div class='close-btn-container'>", unsafe_allow_html=True)
        if close_callback:
            if st.button("Close Wizard", key="close_wizard", type="primary"):
                close_callback()
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close wizard-container

# 3. EXAMPLE USAGE
if __name__ == "__main__":
    st.title("Item Selection Demo")
    
    def handle_add_item(item_name):
        st.success(f"Added: {item_name}")
        if 'selected_items' not in st.session_state:
            st.session_state.selected_items = []
        st.session_state.selected_items.append(item_name)
    
    def handle_close_wizard():
        st.session_state.show_wizard = False
        st.rerun()
    
    if 'show_wizard' not in st.session_state:
        st.session_state.show_wizard = True
    
    if st.session_state.show_wizard:
        items_data = load_item_data()
        show_item_wizard(items_data, handle_add_item, handle_close_wizard)
    
    if 'selected_items' in st.session_state and st.session_state.selected_items:
        st.subheader("Your Selections")
        for item in st.session_state.selected_items:
            st.write(f"- {item}")
    
    if not st.session_state.show_wizard:
        if st.button("Show Item Wizard"):
            st.session_state.show_wizard = True
            st.rerun()
