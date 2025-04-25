import pandas as pd
import streamlit as st

def show_item_wizard(wizard_items_df, callback):
    """Display the item selection wizard inline in the main window"""
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
            .filter-option {
                margin-left: 0.3rem;
                margin-bottom: 0.2rem;
                font-size: 0.85rem;
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
            .search-box {
                margin-bottom: 0.5rem;
            }
            .results-count {
                color: #666;
                margin-bottom: 0.5rem;
                font-size: 0.85rem;
            }
            .stCheckbox > label {
                font-size: 0.85rem !important;
            }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='wizard-container'>", unsafe_allow_html=True)
        st.markdown("#### Item Selection Wizard")
        
        # Main layout columns (30% filters, 70% items)
        filter_col, items_col = st.columns([3, 7])

        with filter_col:
            # Search box at top of filters
            search_term = st.text_input("🔍 Search items", key="wizard_search")
            
            # Initialize selected filters in session state
            if 'selected_filters' not in st.session_state:
                st.session_state.selected_filters = {
                    'main_categories': [],
                    'sub1_categories': [],
                    'sub2_categories': []
                }

            # Always show all filter sections
            st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
            
            # Main Category filter (always visible)
            st.markdown("<div class='filter-header'>Main Categories</div>", unsafe_allow_html=True)
            main_categories = sorted(wizard_items_df['Main Category'].dropna().unique().tolist())
            for category in main_categories:
                checked = st.checkbox(
                    category, 
                    key=f"main_{category}",
                    value=category in st.session_state.selected_filters['main_categories']
                )
                if checked:
                    if category not in st.session_state.selected_filters['main_categories']:
                        st.session_state.selected_filters['main_categories'].append(category)
                else:
                    if category in st.session_state.selected_filters['main_categories']:
                        st.session_state.selected_filters['main_categories'].remove(category)
            
            st.markdown("</div>", unsafe_allow_html=True)  # Close filter-section

            # Sub Category 1 filter (always visible)
            st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
            st.markdown("<div class='filter-header'>Sub Categories 1</div>", unsafe_allow_html=True)
            
            # Determine available sub1 options based on selection
            if st.session_state.selected_filters['main_categories']:
                sub1_options = wizard_items_df[
                    wizard_items_df['Main Category'].isin(st.session_state.selected_filters['main_categories'])
                ]['Sub Category 1'].dropna().unique().tolist()
            else:
                sub1_options = wizard_items_df['Sub Category 1'].dropna().unique().tolist()
            
            for sub1 in sorted(sub1_options):
                checked = st.checkbox(
                    sub1, 
                    key=f"sub1_{sub1}",
                    value=sub1 in st.session_state.selected_filters['sub1_categories']
                )
                if checked:
                    if sub1 not in st.session_state.selected_filters['sub1_categories']:
                        st.session_state.selected_filters['sub1_categories'].append(sub1)
                else:
                    if sub1 in st.session_state.selected_filters['sub1_categories']:
                        st.session_state.selected_filters['sub1_categories'].remove(sub1)
            
            st.markdown("</div>", unsafe_allow_html=True)  # Close filter-section

            # Sub Category 2 filter (always visible)
            st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
            st.markdown("<div class='filter-header'>Sub Categories 2</div>", unsafe_allow_html=True)
            
            # Determine available sub2 options based on selection
            if st.session_state.selected_filters['sub1_categories']:
                sub2_options = wizard_items_df[
                    wizard_items_df['Sub Category 1'].isin(st.session_state.selected_filters['sub1_categories'])
                ]['Sub Category 2'].dropna().unique().tolist()
            else:
                sub2_options = wizard_items_df['Sub Category 2'].dropna().unique().tolist()
            
            for sub2 in sorted(sub2_options):
                checked = st.checkbox(
                    sub2, 
                    key=f"sub2_{sub2}",
                    value=sub2 in st.session_state.selected_filters['sub2_categories']
                )
                if checked:
                    if sub2 not in st.session_state.selected_filters['sub2_categories']:
                        st.session_state.selected_filters['sub2_categories'].append(sub2)
                else:
                    if sub2 in st.session_state.selected_filters['sub2_categories']:
                        st.session_state.selected_filters['sub2_categories'].remove(sub2)
            
            st.markdown("</div>", unsafe_allow_html=True)  # Close filter-section

        with items_col:
            # Apply filters to items
            filtered_items = wizard_items_df.copy()
            
            # Apply category filters
            if st.session_state.selected_filters['main_categories']:
                filtered_items = filtered_items[
                    filtered_items['Main Category'].isin(st.session_state.selected_filters['main_categories'])
                ]
            
            if st.session_state.selected_filters['sub1_categories']:
                filtered_items = filtered_items[
                    filtered_items['Sub Category 1'].isin(st.session_state.selected_filters['sub1_categories'])
                ]
            
            if st.session_state.selected_filters['sub2_categories']:
                filtered_items = filtered_items[
                    filtered_items['Sub Category 2'].isin(st.session_state.selected_filters['sub2_categories'])
                ]
            
            # Apply search term filter
            if search_term:
                filtered_items = filtered_items[
                    filtered_items['Item Name'].str.contains(search_term, case=False)
                ]
            
            # Display results count
            st.markdown(f"<div class='results-count'>Showing {len(filtered_items)} items</div>", unsafe_allow_html=True)
            
            # Display items in a compact grid
            for _, row in filtered_items.iterrows():
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
                    if st.button("Add", key=f"add_{row['Item Name']}_{_}"):
                        callback(row['Item Name'])
                        st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close wizard-container