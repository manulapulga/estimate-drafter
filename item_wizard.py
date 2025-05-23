import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# 1. DATA LOADING (CACHED FOR PERFORMANCE)
@st.cache_data
def load_item_data():
    """
    Load your item data here.
    Replace this with your actual data loading code.
    For example, if you have a CSV file:
    return pd.read_csv('your_items.csv')
    """
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
def show_item_wizard(items_df, add_callback):
    """
    Displays the Smart Filter with filters and pagination
    Parameters:
    - items_df: Your pandas DataFrame of items
    - add_callback: Function to call when "Add" button is clicked
    """
    
    # CSS Styling for the wizard
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
        .filter-header {
            font-weight: bold;
            margin-bottom: 0.3rem;
            color: #333;
            font-size: 0.9rem;
        }
        .item-card {
            padding: 0.7rem;
            margin: 0.3rem 0;
            border: 1px solid #ddd;
            border-radius: 0.3rem;
            background-color: white;
        }
        .item-title {
            font-weight: 600;
            font-size: 0.95rem;
            margin-bottom: 0.2rem;
        }
        .item-categories {
            color: #666;
            font-size: 0.8rem;
            margin-bottom: 0.3rem;
        }
        .item-price {
            font-weight: 500;
            color: #2e7d32;
            font-size: 0.85rem;
        }
        .results-count {
            color: #666;
            margin-bottom: 0.5rem;
            font-size: 0.85rem;
        }
        .pagination-info {
            padding-top: 0.5rem;
        }
        .pagination-button {
            margin: 0 0.2rem;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        # Wizard container
        st.markdown("<div class='wizard-container'>", unsafe_allow_html=True)
        st.markdown("#### Smart Filter")
        
        # Two column layout (filters on left, items on right)
        filter_col, items_col = st.columns([2, 8])

        # In the show_item_wizard function, modify the FILTERS COLUMN section as follows:
        
        # FILTERS COLUMN
        with filter_col:
            
            
            # Search box
            search_term = st.text_input("🔍 Search items", key="wizard_search")
            
            # Initialize filters in session state if not exists
            if 'wizard_filters' not in st.session_state:
                st.session_state.wizard_filters = {
                    'main_categories': [],
                    'sub1_categories': [],
                    'sub2_categories': []
                }
            # Clear All Filters button
            if st.button("🧹 Clear All Filters", key="clear_filters", use_container_width=True,
                        help="Reset all filters to their default state"):
                # Reset all filter selections
                st.session_state.wizard_filters = {
                    'main_categories': [],
                    'sub1_categories': [],
                    'sub2_categories': []
                }
                
                # Clear all checkbox states
                main_categories = sorted(items_df['Main Category'].dropna().unique().tolist())
                for category in main_categories:
                    st.session_state[f"main_{category}"] = False
                
                sub1_options = items_df['Sub Category 1'].dropna().unique().tolist()
                for sub1 in sub1_options:
                    st.session_state[f"sub1_{sub1}"] = False
                    
                sub2_options = items_df['Sub Category 2'].dropna().unique().tolist()
                for sub2 in sub2_options:
                    st.session_state[f"sub2_{sub2}"] = False
                    
                st.session_state.current_page = 1
                st.rerun()
            # Replace the checkbox sections in your code with these versions:
            # MAIN CATEGORY FILTER
            st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
            st.markdown("<div class='filter-header'>Main Categories</div>", unsafe_allow_html=True)
            main_categories = sorted(items_df['Main Category'].dropna().unique().tolist())
            
            def update_main_category(category):
                if category not in st.session_state.wizard_filters['main_categories']:
                    st.session_state.wizard_filters['main_categories'].append(category)
                else:
                    st.session_state.wizard_filters['main_categories'].remove(category)
                st.session_state.current_page = 1  # Reset to first page when filters change
            
            for category in main_categories:
                st.checkbox(
                    category,
                    key=f"main_{category}",
                    value=category in st.session_state.wizard_filters['main_categories'],
                    on_change=update_main_category,
                    args=(category,),
                    kwargs=None
                )
            st.markdown("</div>", unsafe_allow_html=True)
            
            # SUB CATEGORY 1 FILTER
            st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
            st.markdown("<div class='filter-header'>Sub Categories 1</div>", unsafe_allow_html=True)
            
            def update_sub1_category(sub1):
                if sub1 not in st.session_state.wizard_filters['sub1_categories']:
                    st.session_state.wizard_filters['sub1_categories'].append(sub1)
                else:
                    st.session_state.wizard_filters['sub1_categories'].remove(sub1)
                st.session_state.current_page = 1
            
            if st.session_state.wizard_filters['main_categories']:
                sub1_options = items_df[
                    items_df['Main Category'].isin(st.session_state.wizard_filters['main_categories'])
                ]['Sub Category 1'].dropna().unique().tolist()
            else:
                sub1_options = items_df['Sub Category 1'].dropna().unique().tolist()
            
            import re

            def extract_prefix_number(s):
                match = re.match(r"^\s*(\d+)\.", s)
                return int(match.group(1)) if match else float('inf')  # Non-numbered items go last
            
            # Sort using the numeric prefix
            sorted_sub1 = sorted(sub1_options, key=extract_prefix_number)
            
            for sub1 in sorted_sub1:
                label = f"{sub1}".replace(" ", "\u00A0")  # Preserve spacing in UI
                st.checkbox(
                    label,
                    key=f"sub1_{sub1}",
                    value=sub1 in st.session_state.wizard_filters['sub1_categories'],
                    on_change=update_sub1_category,
                    args=(sub1,)
                )
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # SUB CATEGORY 2 FILTER
            st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
            st.markdown("<div class='filter-header'>Sub Categories 2</div>", unsafe_allow_html=True)
            
            def update_sub2_category(sub2):
                if sub2 not in st.session_state.wizard_filters['sub2_categories']:
                    st.session_state.wizard_filters['sub2_categories'].append(sub2)
                else:
                    st.session_state.wizard_filters['sub2_categories'].remove(sub2)
                st.session_state.current_page = 1
            
            # Create a base query for Sub Category 2 filtering
            base_query = items_df.copy()
            
            # Apply Main Category filter if any are selected
            if st.session_state.wizard_filters['main_categories']:
                base_query = base_query[base_query['Main Category'].isin(st.session_state.wizard_filters['main_categories'])]
            
            # Apply Sub Category 1 filter if any are selected
            if st.session_state.wizard_filters['sub1_categories']:
                base_query = base_query[base_query['Sub Category 1'].isin(st.session_state.wizard_filters['sub1_categories'])]
            
            # Get the filtered Sub Category 2 options
            sub2_options = base_query['Sub Category 2'].dropna().unique().tolist()
            
            for sub2 in sorted(sub2_options):
                st.checkbox(
                    sub2,
                    key=f"sub2_{sub2}",
                    value=sub2 in st.session_state.wizard_filters['sub2_categories'],
                    on_change=update_sub2_category,
                    args=(sub2,)
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # ITEMS COLUMN
        with items_col:
            # Apply filters
            filtered_items = items_df.copy()
            
            # Category filters
            if st.session_state.wizard_filters['main_categories']:
                filtered_items = filtered_items[
                    filtered_items['Main Category'].isin(st.session_state.wizard_filters['main_categories'])
                ]
            if st.session_state.wizard_filters['sub1_categories']:
                filtered_items = filtered_items[
                    filtered_items['Sub Category 1'].isin(st.session_state.wizard_filters['sub1_categories'])
                ]
            if st.session_state.wizard_filters['sub2_categories']:
                filtered_items = filtered_items[
                    filtered_items['Sub Category 2'].isin(st.session_state.wizard_filters['sub2_categories'])
                ]
            
            # Search filter
            if search_term:
                search_terms = search_term.lower().split()
                
                def search_match(row):
                    # Combine all relevant fields into one searchable string
                    search_text = ' '.join([
                        str(row['Item Name']).lower(),
                        str(row['Main Category']).lower(),
                        str(row['Sub Category 1']).lower(),
                        str(row['Sub Category 2']).lower()
                    ])
                    
                    # Check if all search terms appear in any order
                    return all(term in search_text for term in search_terms)
                
                filtered_items = filtered_items[filtered_items.apply(search_match, axis=1)]
            
            # PAGINATION CONTROLS
            PAGE_SIZE = 50
            total_items = len(filtered_items)
            total_pages = max(1, (total_items // PAGE_SIZE) + (1 if total_items % PAGE_SIZE else 0))
            
            # Initialize current page in session state if not exists
            if 'current_page' not in st.session_state:
                st.session_state.current_page = 1
            
            # Navigation buttons
            if total_pages > 1:
                col1, col2, col3, col4, _ = st.columns([1, 1, 1, 1, 6])
                
                with col1:
                    if st.button("⏮️", disabled=st.session_state.current_page == 1, 
                               key="first_page", help="Go to first page"):
                        st.session_state.current_page = 1
                        st.rerun()
                
                with col2:
                    if st.button("◀️", disabled=st.session_state.current_page == 1, 
                               key="prev_page", help="Previous page"):
                        st.session_state.current_page -= 1
                        st.rerun()
                
                with col3:
                    st.markdown(f"<div class='pagination-info'>Page {st.session_state.current_page} of {total_pages}</div>", 
                               unsafe_allow_html=True)
                
                with col4:
                    if st.button("▶️", disabled=st.session_state.current_page == total_pages, 
                               key="next_page", help="Next page"):
                        st.session_state.current_page += 1
                        st.rerun()
            
            # Calculate which items to show
            start_idx = (st.session_state.current_page - 1) * PAGE_SIZE
            end_idx = min(start_idx + PAGE_SIZE, total_items)
            
            # Show results count
            st.markdown(
                f"<div class='results-count'>Showing items {start_idx + 1}-{end_idx} of {total_items}</div>", 
                unsafe_allow_html=True
            )
            
            # DISPLAY ITEMS
            for idx in range(start_idx, end_idx):
                row = filtered_items.iloc[idx]
                col1, col2 = st.columns([5, 1])
                from streamlit.components.v1 import html

                with col1:
                    item_name = row['Item Name']
                    uid = f"copy_{idx}"
                    html(f"""
                        <style>
                            body {{
                                font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                            }}
                            .item-card {{
                                padding: 0.7rem;
                                margin: 0.3rem 0;
                                border: 1px solid #ddd;
                                border-radius: 0.3rem;
                                background-color: white;
                            }}
                            .item-title {{
                                font-weight: 600;
                                font-size: 0.95rem;
                                margin-bottom: 0.2rem;
                            }}
                            .item-categories {{
                                color: #666;
                                font-size: 0.8rem;
                                margin-bottom: 0.3rem;
                            }}
                            .item-price {{
                                font-weight: 500;
                                color: #2e7d32;
                                font-size: 0.85rem;
                            }}
                            .copy-btn {{
                                margin-left: 8px;
                                background-color: transparent;
                                border: none;
                                cursor: pointer;
                                font-size: 1rem;
                            }}
                        </style>
                        <div class='item-card'>
                            <div class='item-title'>
                                {item_name}
                                <button class='copy-btn' onclick="navigator.clipboard.writeText('{item_name.replace("'", "\\'")}');
                                        let msg = document.getElementById('{uid}_msg');
                                        msg.style.display='inline';
                                        setTimeout(() => msg.style.display='none', 1500);">
                                    📋
                                </button>
                                <span id="{uid}_msg" style="color: green; font-size: 0.8rem; display: none;">Copied!</span>
                            </div>
                            <div class='item-categories'>
                                {row['Main Category']} » {row['Sub Category 1']} » {row['Sub Category 2']}
                            </div>
                            <div class='item-price'>
                                ₹{row['Unit Price']:.2f} per {row['Item Unit']}
                            </div>
                        </div>
                    """, height=120)

                with col2:
                    if st.button("Add", key=f"add_{idx}"):
                        add_callback(row['Item Name'])
                        st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close wizard-container

# 3. EXAMPLE USAGE
if __name__ == "__main__":
    st.title("Item Selection Demo")
    
    # This function will be called when "Add" is clicked
    def handle_add_item(item_name):
        st.success(f"Added: {item_name}")
        # Here you would typically add to a cart or list
        if 'selected_items' not in st.session_state:
            st.session_state.selected_items = []
        st.session_state.selected_items.append(item_name)
    
    # Load the data
    items_data = load_item_data()
    
    # Show the wizard
    show_item_wizard(items_data, handle_add_item)
    
    # Display selected items (for demo purposes)
    if 'selected_items' in st.session_state and st.session_state.selected_items:
        st.subheader("Your Selections")
        for item in st.session_state.selected_items:
            st.write(f"- {item}")
