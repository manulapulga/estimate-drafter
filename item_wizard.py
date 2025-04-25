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
        .pagination-container {
            display: flex;
            align-items: center;
            gap: 0;
            margin-bottom: 1rem;
            justify-content: center;
        }
        .pagination-btn {
            padding: 0.25rem 0.5rem;
            border-radius: 0;
            border: 1px solid #ddd;
            background: white;
            cursor: pointer;
            min-width: 2rem;
            text-align: center;
            margin: 0;
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
        .pagination-btn:first-child {
            border-radius: 0.25rem 0 0 0.25rem;
        }
        .pagination-btn:last-child {
            border-radius: 0 0.25rem 0.25rem 0;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        # Wizard container
        st.markdown("<div class='wizard-container'>", unsafe_allow_html=True)
        st.markdown("#### Item Selection Wizard")
        
        # Three column layout (filters on left, pagination in middle, items on right)
        filter_col, pagination_col, items_col = st.columns([3, 1, 7])

        # FILTERS COLUMN (same as before)
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

        # PAGINATION COLUMN (middle column)
        with pagination_col:
            # PAGINATION CONTROLS - ENHANCED VERSION
            PAGE_SIZE = 50
            total_items = len(filtered_items)
            total_pages = max(1, math.ceil(total_items / PAGE_SIZE))
            
            # Initialize current page in session state
            if 'current_page' not in st.session_state:
                st.session_state.current_page = 1
            
            # Calculate which items to show
            start_idx = (st.session_state.current_page - 1) * PAGE_SIZE
            end_idx = min(start_idx + PAGE_SIZE, total_items)
            
            # Show results count
            st.markdown(
                f"<div class='results-count'>Showing items {start_idx + 1}-{end_idx} of {total_items}</div>", 
                unsafe_allow_html=True
            )
            
            # PAGINATION CONTROLS - HORIZONTAL BUTTONS
            st.markdown("<div class='pagination-container'>", unsafe_allow_html=True)
            
            # First page button
            if st.button("⏮", key="first_page"):
                st.session_state.current_page = 1
                st.rerun()
            
            # Previous page button
            if st.button("◀", key="prev_page"):
                if st.session_state.current_page > 1:
                    st.session_state.current_page -= 1
                    st.rerun()
            
            # Page number buttons (show up to 5 pages around current page)
            max_visible_pages = 5
            half_visible = max_visible_pages // 2
            start_page = max(1, st.session_state.current_page - half_visible)
            end_page = min(total_pages, start_page + max_visible_pages - 1)
            
            # Adjust if we're at the end
            if end_page - start_page + 1 < max_visible_pages:
                start_page = max(1, end_page - max_visible_pages + 1)
            
            for p in range(start_page, end_page + 1):
                # Highlight current page
                is_active = p == st.session_state.current_page
                if st.button(str(p), key=f"page_{p}", 
                           type="primary" if is_active else "secondary"):
                    st.session_state.current_page = p
                    st.rerun()
            
            # Next page button
            if st.button("▶", key="next_page"):
                if st.session_state.current_page < total_pages:
                    st.session_state.current_page += 1
                    st.rerun()
            
            # Last page button
            if st.button("⏭", key="last_page"):
                st.session_state.current_page = total_pages
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)  # Close pagination-container

        # ITEMS COLUMN
        with items_col:
            # Display Items as before
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
