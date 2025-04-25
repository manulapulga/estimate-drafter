import pandas as pd
import streamlit as st

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
    Displays the item selection wizard with filters and pagination
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
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        # Wizard container
        st.markdown("<div class='wizard-container'>", unsafe_allow_html=True)
        st.markdown("#### Item Selection Wizard")
        
        # Two column layout (filters on left, items on right)
        filter_col, items_col = st.columns([3, 7])

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

            # MAIN CATEGORY FILTER
            st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
            st.markdown("<div class='filter-header'>Main Categories</div>", unsafe_allow_html=True)
            main_categories = sorted(items_df['Main Category'].dropna().unique().tolist())
            for category in main_categories:
                if st.checkbox(
                    category, 
                    key=f"main_{category}",
                    value=category in st.session_state.wizard_filters['main_categories']
                ):
                    if category not in st.session_state.wizard_filters['main_categories']:
                        st.session_state.wizard_filters['main_categories'].append(category)
                else:
                    if category in st.session_state.wizard_filters['main_categories']:
                        st.session_state.wizard_filters['main_categories'].remove(category)
            st.markdown("</div>", unsafe_allow_html=True)

            # SUB CATEGORY 1 FILTER
            st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
            st.markdown("<div class='filter-header'>Sub Categories 1</div>", unsafe_allow_html=True)
            if st.session_state.wizard_filters['main_categories']:
                sub1_options = items_df[
                    items_df['Main Category'].isin(st.session_state.wizard_filters['main_categories'])
                ]['Sub Category 1'].dropna().unique().tolist()
            else:
                sub1_options = items_df['Sub Category 1'].dropna().unique().tolist()
            
            for sub1 in sorted(sub1_options):
                if st.checkbox(
                    sub1, 
                    key=f"sub1_{sub1}",
                    value=sub1 in st.session_state.wizard_filters['sub1_categories']
                ):
                    if sub1 not in st.session_state.wizard_filters['sub1_categories']:
                        st.session_state.wizard_filters['sub1_categories'].append(sub1)
                else:
                    if sub1 in st.session_state.wizard_filters['sub1_categories']:
                        st.session_state.wizard_filters['sub1_categories'].remove(sub1)
            st.markdown("</div>", unsafe_allow_html=True)

            # SUB CATEGORY 2 FILTER
            st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
            st.markdown("<div class='filter-header'>Sub Categories 2</div>", unsafe_allow_html=True)
            if st.session_state.wizard_filters['sub1_categories']:
                sub2_options = items_df[
                    items_df['Sub Category 1'].isin(st.session_state.wizard_filters['sub1_categories'])
                ]['Sub Category 2'].dropna().unique().tolist()
            else:
                sub2_options = items_df['Sub Category 2'].dropna().unique().tolist()
            
            for sub2 in sorted(sub2_options):
                if st.checkbox(
                    sub2, 
                    key=f"sub2_{sub2}",
                    value=sub2 in st.session_state.wizard_filters['sub2_categories']
                ):
                    if sub2 not in st.session_state.wizard_filters['sub2_categories']:
                        st.session_state.wizard_filters['sub2_categories'].append(sub2)
                else:
                    if sub2 in st.session_state.wizard_filters['sub2_categories']:
                        st.session_state.wizard_filters['sub2_categories'].remove(sub2)
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
                filtered_items = filtered_items[
                    filtered_items['Item Name'].str.contains(search_term, case=False)
                ]
            
            # PAGINATION CONTROLS
            PAGE_SIZE = 50
            total_items = len(filtered_items)
            total_pages = max(1, (total_items // PAGE_SIZE) + (1 if total_items % PAGE_SIZE else 0))
            page = 1  # Default page
            
            if total_pages > 1:
                col1, col2, _ = st.columns([1, 1, 6])
                with col1:
                    page = st.number_input(
                        "Page", 
                        min_value=1, 
                        max_value=total_pages, 
                        value=1,
                        key="wizard_page"
                    )
                with col2:
                    st.markdown(f"<div class='pagination-info'>of {total_pages}</div>", unsafe_allow_html=True)
            
            # Calculate which items to show
            start_idx = (page - 1) * PAGE_SIZE
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
                with col1:
                    st.markdown(f"""
                        <div class='item-card'>
                            <div class='item-title'>{row['Item Name']}</div>
                            <div class='item-categories'>
                                {row['Main Category']} » {row['Sub Category 1']} » {row['Sub Category 2']}
                            </div>
                            <div class='item-price'>
                                ₹{row['Unit Price']:.2f} per {row['Item Unit']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
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
