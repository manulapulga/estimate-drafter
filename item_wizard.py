def show_item_wizard(items_df, add_callback):
    """Displays the item selection wizard with middle column for pagination"""
    
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
        .pagination-container {
            display: flex;
            justify-content: center;
            gap: 0.2rem;
            margin: 0.5rem 0;
        }
        .pagination-btn {
            padding: 0.25rem 0.5rem;
            border: 1px solid #ddd;
            background: white;
            cursor: pointer;
            min-width: 2rem;
            text-align: center;
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
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='wizard-container'>", unsafe_allow_html=True)
        st.markdown("#### Item Selection Wizard")
        
        # Three column layout (filters | items | pagination)
        filter_col, items_col, pagination_col = st.columns([3, 6, 1])

        # FILTERS COLUMN
        with filter_col:
            # Search box
            search_term = st.text_input("🔍 Search items", key="wizard_search")
            
            # Initialize filters
            if 'wizard_filters' not in st.session_state:
                st.session_state.wizard_filters = {
                    'main_categories': [],
                    'sub1_categories': [],
                    'sub2_categories': []
                }

            # Main Category filter
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

            # Sub Category 1 filter
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

            # Sub Category 2 filter
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

        # Apply filters
        filtered_items = items_df.copy()
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
        if search_term:
            filtered_items = filtered_items[
                filtered_items['Item Name'].str.contains(search_term, case=False)
            ]

        # ITEMS COLUMN (middle column)
        with items_col:
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

        # PAGINATION COLUMN (last column)
        with pagination_col:
            PAGE_SIZE = 50
            total_items = len(filtered_items)
            total_pages = max(1, math.ceil(total_items / PAGE_SIZE))
            
            if 'current_page' not in st.session_state:
                st.session_state.current_page = 1
            
            start_idx = (st.session_state.current_page - 1) * PAGE_SIZE
            end_idx = min(start_idx + PAGE_SIZE, total_items)
            
            # Vertical space for alignment
            st.write(" ")
            st.write(" ")
            
            # Pagination controls
            st.markdown("<div class='pagination-container'>", unsafe_allow_html=True)
            
            if st.button("⏮", key="first_page"):
                st.session_state.current_page = 1
                st.rerun()
            
            if st.button("◀", key="prev_page"):
                if st.session_state.current_page > 1:
                    st.session_state.current_page -= 1
                    st.rerun()
            
            max_visible_pages = 5
            half_visible = max_visible_pages // 2
            start_page = max(1, st.session_state.current_page - half_visible)
            end_page = min(total_pages, start_page + max_visible_pages - 1)
            
            if end_page - start_page + 1 < max_visible_pages:
                start_page = max(1, end_page - max_visible_pages + 1)
            
            for p in range(start_page, end_page + 1):
                if st.button(str(p), key=f"page_{p}", 
                           type="primary" if p == st.session_state.current_page else "secondary"):
                    st.session_state.current_page = p
                    st.rerun()
            
            if st.button("▶", key="next_page"):
                if st.session_state.current_page < total_pages:
                    st.session_state.current_page += 1
                    st.rerun()
            
            if st.button("⏭", key="last_page"):
                st.session_state.current_page = total_pages
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Results count below pagination
            st.markdown(
                f"<div style='text-align: center; margin-top: 0.5rem;'>"
                f"Page {st.session_state.current_page} of {total_pages}<br>"
                f"{total_items} items</div>", 
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)
