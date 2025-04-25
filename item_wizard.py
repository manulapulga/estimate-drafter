import pandas as pd
import streamlit as st
import math

# 1. DATA LOADING (CACHED FOR PERFORMANCE)
@st.cache_data
def load_item_data():
    """Load and cache the item data"""
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
    """Display the optimized item selection wizard"""
    
    # CSS Styling for the wizard
    st.markdown("""
    <style>
        /* Pagination container */
        .pagination-container {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0;
            margin-bottom: 1rem;
        }
        
        /* Pagination button base style */
        .pagination-btn {
            padding: 0.25rem 0.5rem;
            border: 1px solid #ddd;
            background: white;
            cursor: pointer;
            min-width: 2rem;
            text-align: center;
            margin: 0;
            font-size: 0.9rem;
        }
        
        /* Remove double borders between buttons */
        .pagination-btn:not(:first-child) {
            border-left: none;
        }
        
        /* First button rounded left */
        .pagination-btn:first-child {
            border-radius: 4px 0 0 4px;
        }
        
        /* Last button rounded right */
        .pagination-btn:last-child {
            border-radius: 0 4px 4px 0;
        }
        
        /* Hover effect */
        .pagination-btn:hover {
            background: #f0f0f0;
        }
        
        /* Active page button */
        .pagination-btn.active {
            background: #4CAF50;
            color: white;
            border-color: #4CAF50;
            font-weight: bold;
        }
        
        /* Disabled buttons */
        .pagination-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='wizard-container'>", unsafe_allow_html=True)
        st.markdown("#### Item Selection Wizard")
        
        filter_col, items_col = st.columns([3, 7])

        with filter_col:
            # ... (keep your existing filter code exactly the same) ...

        with items_col:
            # ... (keep your existing filtering logic exactly the same) ...
            
            # PAGINATION CONTROLS - COMPACT HORIZONTAL BAR
            PAGE_SIZE = 50
            total_items = len(filtered_items)
            total_pages = max(1, math.ceil(total_items / PAGE_SIZE))
            
            if 'current_page' not in st.session_state:
                st.session_state.current_page = 1
            
            start_idx = (st.session_state.current_page - 1) * PAGE_SIZE
            end_idx = min(start_idx + PAGE_SIZE, total_items)
            
            st.markdown(
                f"<div class='results-count'>Showing items {start_idx + 1}-{end_idx} of {total_items}</div>", 
                unsafe_allow_html=True
            )
            
            # Create a container for the pagination buttons
            pagination_html = """
            <div class="pagination-container">
            """
            
            # First page button
            disabled = "disabled" if st.session_state.current_page == 1 else ""
            pagination_html += f"""
                <button class="pagination-btn" {disabled} onclick="window.streamlitApi.setComponentValue('first')">⏮</button>
            """
            
            # Previous page button
            disabled = "disabled" if st.session_state.current_page == 1 else ""
            pagination_html += f"""
                <button class="pagination-btn" {disabled} onclick="window.streamlitApi.setComponentValue('prev')">◀</button>
            """
            
            # Page number buttons (show up to 5 pages around current)
            max_visible = 5
            half = max_visible // 2
            start_page = max(1, st.session_state.current_page - half)
            end_page = min(total_pages, start_page + max_visible - 1)
            
            if end_page - start_page + 1 < max_visible:
                start_page = max(1, end_page - max_visible + 1)
            
            for p in range(start_page, end_page + 1):
                active = "active" if p == st.session_state.current_page else ""
                pagination_html += f"""
                    <button class="pagination-btn {active}" onclick="window.streamlitApi.setComponentValue({p})">{p}</button>
                """
            
            # Next page button
            disabled = "disabled" if st.session_state.current_page == total_pages else ""
            pagination_html += f"""
                <button class="pagination-btn" {disabled} onclick="window.streamlitApi.setComponentValue('next')">▶</button>
            """
            
            # Last page button
            disabled = "disabled" if st.session_state.current_page == total_pages else ""
            pagination_html += f"""
                <button class="pagination-btn" {disabled} onclick="window.streamlitApi.setComponentValue('last')">⏭</button>
            """
            
            pagination_html += "</div>"
            
            # Display the pagination and handle button clicks
            pagination_action = st.markdown(pagination_html, unsafe_allow_html=True)
            
            if hasattr(pagination_action, '_value'):
                action = pagination_action._value
                if action == 'first':
                    st.session_state.current_page = 1
                elif action == 'prev' and st.session_state.current_page > 1:
                    st.session_state.current_page -= 1
                elif action == 'next' and st.session_state.current_page < total_pages:
                    st.session_state.current_page += 1
                elif action == 'last':
                    st.session_state.current_page = total_pages
                elif isinstance(action, int) and 1 <= action <= total_pages:
                    st.session_state.current_page = action
                st.rerun()
            
            # ... (keep your existing item display code) ...

        st.markdown("</div>", unsafe_allow_html=True)

# 3. EXAMPLE USAGE
if __name__ == "__main__":
    st.title("Item Selection Demo")
    
    def handle_add_item(item_name):
        st.success(f"Added: {item_name}")
        if 'selected_items' not in st.session_state:
            st.session_state.selected_items = []
        st.session_state.selected_items.append(item_name)
    
    items_data = load_item_data()
    show_item_wizard(items_data, handle_add_item)
    
    if 'selected_items' in st.session_state and st.session_state.selected_items:
        st.subheader("Your Selections")
        for item in st.session_state.selected_items:
            st.write(f"- {item}")
