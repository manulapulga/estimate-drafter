import pandas as pd
import streamlit as st
from streamlit.components.v1 import html
from difflib import SequenceMatcher
from difflib import SequenceMatcher

def compute_relevance_score(row, search_phrase, search_terms):
    text = ' '.join([
        str(row['Item Name']).lower(),
        str(row['Main Category']).lower(),
        str(row['Sub Category 1']).lower(),
        str(row['Sub Category 2']).lower()
    ])
    text = ' '.join(text.split())  # normalize spaces

    score = 0

    # High boost for exact phrase
    if search_phrase in text:
        score += 5

    # Boost for individual term presence
    score += sum(1 for term in search_terms if term in text)

    # Extra boost for important phrase (example: "2 hp")
    if "2 hp" in search_phrase and "2 hp" in text:
        score += 3

    # Add fuzzy similarity
    similarity = SequenceMatcher(None, search_phrase, text).ratio()
    score += similarity  # typically 0–1

    return score

def smart_search_match(row, search_phrase, search_terms, strict=False, fuzzy=False):
    combined_text = ' '.join([
        str(row['Item Name']).lower(),
        str(row['Main Category']).lower(),
        str(row['Sub Category 1']).lower(),
        str(row['Sub Category 2']).lower()
    ])
    combined_text = ' '.join(combined_text.split())  # Normalize spacing

    if strict:
        return search_phrase in combined_text

    if fuzzy:
        ratio = SequenceMatcher(None, search_phrase, combined_text).ratio()
        return ratio > 0.5  # Threshold can be tuned

    return all(term in combined_text for term in search_terms)

# 2. ITEM WIZARD COMPONENT
def show_item_wizard(items_df, add_callback, selected_items=None):
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
            border-top: 1px solid white;
            margin: 0rem 0;
            background-color: white;
            border-radius: 0px;
            padding: 0px;
        }
        .filter-section {
            border-top: 1px solid #ddd;
            padding: 0rem;
            margin: 0rem 0;
            background-color: #ddd;
            border-radius: 0px;
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
            border: 1px solid #d6eaf4;
            border-radius: 0.3rem;
            background: linear-gradient(135deg, #e9f8ff, #effff4); /* Soft blue to pale green */
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
        .copy-btn {
            background-color: #f0f2f6;
            border: none;
            color: #262730;
            padding: 0.5rem 1rem;
            margin-top: 0.25rem;
            margin-bottom: 0.25rem;
            border-radius: 0.5rem;
            font-size: 0.875rem;
            cursor: pointer;
            width: 100%;
            text-align: center;
            transition: background-color 0.2s ease;
        }
        .copy-btn:hover {
            background-color: #e4e8ef;
        }
        .item-title-container {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        /* ... existing styles ... */
        .item-card.selected {
            border: 2px solid #4CAF50;
            background-color: #f8fff8;
        }
        .add-btn {
            background-color: #4CAF50 !important;
            color: white !important;
            border: none !important;
        }
        .add-btn.added {
            background-color: #f44336 !important;
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
            
            # In the FILTERS COLUMN section, replace the sort_options and selected_sort with this:
            sort_options = {
                "Default": "default",
                "A to Z": "name_asc",
                "Z to A": "name_desc",
                "Price Low to High": "price_asc",
                "Price High to Low": "price_desc"
            }
            selected_sort = st.selectbox(
                "Sort by",
                options=list(sort_options.keys()),
                key="wizard_sort",
                help="Sort items by name or price"
            )
            
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
            
            # Apply sorting
            sort_key = sort_options[selected_sort]
            if sort_key == "name_asc":
                filtered_items = filtered_items.sort_values('Item Name', ascending=True)
            elif sort_key == "name_desc":
                filtered_items = filtered_items.sort_values('Item Name', ascending=False)
            elif sort_key == "price_asc":
                filtered_items = filtered_items.sort_values('Unit Price', ascending=True)
            elif sort_key == "price_desc":
                filtered_items = filtered_items.sort_values('Unit Price', ascending=False)
            # For "default", we don't apply any sorting - keep the original order
            
            # Reset index after sorting for proper pagination
            filtered_items = filtered_items.reset_index(drop=True)
            
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
            # Improved intelligent search
            if search_term:
                search_input = search_term.strip().lower()
                search_terms = search_input.split()
                search_phrase = ' '.join(search_terms)
            
                # Add score column
                filtered_items['__score__'] = filtered_items.apply(
                    lambda row: compute_relevance_score(row, search_phrase, search_terms), axis=1
                )
            
                # Filter items with any match
                filtered_items = filtered_items[filtered_items['__score__'] > 0]
            
                # Sort by descending score
                filtered_items = filtered_items.sort_values(by='__score__', ascending=False)
            
                # Remove helper column
                filtered_items.drop(columns='__score__', inplace=True)
            
            
            
            # PAGINATION CONTROLS
            PAGE_SIZE = 30
            total_items = len(filtered_items)
            total_pages = max(1, (total_items // PAGE_SIZE) + (1 if total_items % PAGE_SIZE else 0))
            
            # Initialize current page in session state if not exists
            if 'current_page' not in st.session_state:
                st.session_state.current_page = 1
            
            # Navigation buttons
            if total_pages > 1:
                col1, col2, col3, col4, col5 = st.columns([1, 1, 3, 1, 1.5],)
                
                with col1:
                    if st.button("⏮️", disabled=st.session_state.current_page == 1, 
                               key="first_page", help="Go to first page",  use_container_width=True):
                        st.session_state.current_page = 1
                        st.rerun()
                
                with col2:
                    if st.button("◀️", disabled=st.session_state.current_page == 1, 
                               key="prev_page", help="Previous page",  use_container_width=True):
                        st.session_state.current_page -= 1
                        st.rerun()
                
                with col3:
                    st.markdown(f"""
                        <div style='text-align: center;' class='pagination-info'>
                            Page {st.session_state.current_page} of {total_pages}
                        </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    if st.button("▶️", disabled=st.session_state.current_page == total_pages, 
                               key="next_page", help="Next page",  use_container_width=True):
                        st.session_state.current_page += 1
                        st.rerun()
                with col5:
                    if st.button("✕ Close", key="close_wizard2", type="primary",  use_container_width=True):
                        if st.session_state.get("wizard_target_index") is not None:
                            st.session_state["wizard_target_index"] = None
                            st.switch_page("streamlit_app.py")  # Redirect to main page
                        else:
                            st.session_state.show_wizard = False
                            st.session_state.pop("show_wizard_for_edit", None)
                            st.rerun()
       
            
            # Calculate which items to show
            start_idx = (st.session_state.current_page - 1) * PAGE_SIZE
            end_idx = min(start_idx + PAGE_SIZE, total_items)
            
            # Show results count
            st.markdown(
                f"<div class='results-count'>Showing items {start_idx + 1}-{end_idx} of {total_items}</div>", 
                unsafe_allow_html=True
            )
            def copy_buttons(item_name, unit_price, item_unit):
                # Prepare the texts
                text1 = item_name
                text2 = f"{item_name}\t{unit_price}\t{item_unit}"
                text3 = str(unit_price)
            
                # Escape backticks and backslashes to use safely in JavaScript backtick strings
                import html
                import json
                
                def js_escape(text):
                    # Escape for HTML (prevents breaking HTML attributes)
                    html_escaped = html.escape(text)
                    # Escape for JavaScript (within backtick string)
                    return json.dumps(html_escaped)[1:-1]
                
            
                escaped_text1 = js_escape(text1)
                escaped_text2 = js_escape(text2)
                escaped_text3 = js_escape(text3)
            
                st.components.v1.html(f"""
                    <style>
                    .copy-btn {{
                        background-color: #f0f2f6;
                        border: none;
                        color: #262730;
                        padding: 0.5rem 1rem;
                        margin-top: 0.25rem;
                        margin-bottom: 0.25rem;
                        border-radius: 0.5rem;
                        font-size: 0.875rem;
                        cursor: pointer;
                        width: 100%;
                        text-align: center;
                        transition: background-color 0.2s ease;
                        use_container_width=True;
                    }}
                    .copy-btn:hover {{
                        background-color: #e4e8ef;
                    }}
                    </style>
                    <script>
                    function copyToClipboard(text) {{
                        navigator.clipboard.writeText(text);
                    }}
                    </script>
                    <div style="display: flex; flex-direction: row; gap: 8px; margin-top: 5px;">
                        <button type="button" onclick="copyToClipboard(`{escaped_text1}`)"
                                class="copy-btn" title="Copy Item Name">⧉ Copy Name</button>
                        <button type="button" onclick="copyToClipboard(`{escaped_text2}`)"
                                class="copy-btn" title="Copy All Details">📋 Copy Details</button>
                        <button type="button" onclick="copyToClipboard(`{escaped_text3}`)"
                                class="copy-btn" title="Copy Item Price">₹ Copy Price</button>        
                    </div>
                """, height=70)

            
            # DISPLAY ITEMS
            for idx in range(start_idx, end_idx):
                row = filtered_items.iloc[idx]
                is_selected = selected_items and any(
                    item.get('Item') == row['Item Name'] 
                    for item in selected_items 
                    if isinstance(item, dict) and 'Item' in item
                )
                
                col1, col2 = st.columns([5, 1])
                with col1:
                    # Add 'selected' class if item is already in estimate
                    card_class = "item-card selected" if is_selected else "item-card"
                    st.markdown(f"""
                        <div class='{card_class}'>
                            <div class='item-title-container'>
                                <div class='item-title'>{row['Item Name']}</div>
                            </div>
                            <div class='item-categories'>
                                {row['Main Category']} » {row['Sub Category 1']} » {row['Sub Category 2']}
                            </div>
                            <div class='item-price'>
                                ₹{row['Unit Price']:.2f} per {row['Item Unit']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    copy_buttons(row['Item Name'], row['Unit Price'], row['Item Unit'])
                
                # In the ITEMS COLUMN section, modify the button display logic:

                with col2:
                    # Check if Sub Category 1 has prefix and suffix *
                    sub1 = row['Sub Category 1']
                    is_restricted = isinstance(sub1, str) and sub1.startswith('*') and sub1.endswith('*')
                    
                    if not is_restricted:
                        # Check if we're in edit mode
                        is_edit_mode = st.session_state.get("wizard_target_index") is not None
                        
                        # Change button text based on mode
                        if is_edit_mode:
                            btn_text = "Update" if is_selected else "Replace"
                            btn_color = "#2196F3"  # Blue for update/replace
                        else:
                            btn_text = "Remove" if is_selected else "Add"
                            btn_color = "#f44336" if is_selected else "#4CAF50"  # Red for remove, green for add
                        
                        st.markdown(f"""
                            <style>
                                #{btn_text}_{idx} {{
                                    background-color: {btn_color} !important;
                                    color: white !important;
                                    border: none !important;
                                }}
                            </style>
                        """, unsafe_allow_html=True)
                        
                        if st.button(btn_text, key=f"{btn_text}_{idx}",  use_container_width=True):
                            if is_selected and not is_edit_mode:
                                # Find and remove the item from selected_items
                                for i, item in enumerate(selected_items):
                                    if isinstance(item, dict) and item.get('Item') == row['Item Name']:
                                        selected_items.pop(i)
                                        break
                            else:
                                add_callback(row['Item Name'])
                            st.rerun()
                    else:
                        st.markdown("<div style='height: 42px;'></div>", unsafe_allow_html=True)  # Empty space for alignment

            # Navigation buttons
            if total_pages > 1:
                col1, col2, col3, col4, col5 = st.columns([1, 1, 3, 1, 1.5],)
                
                with col1:
                    if st.button("⏮️", disabled=st.session_state.current_page == 1, 
                               key="first_page2", help="Go to first page",  use_container_width=True):
                        st.session_state.current_page = 1
                        st.rerun()
                
                with col2:
                    if st.button("◀️", disabled=st.session_state.current_page == 1, 
                               key="prev_page2", help="Previous page",  use_container_width=True):
                        st.session_state.current_page -= 1
                        st.rerun()
                
                with col3:
                    st.markdown(f"""
                        <div style='text-align: center;' class='pagination-info'>
                            Page {st.session_state.current_page} of {total_pages}
                        </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    if st.button("▶️", disabled=st.session_state.current_page == total_pages, 
                               key="next_page2", help="Next page",  use_container_width=True):
                        st.session_state.current_page += 1
                        st.rerun()
                with col5:
                    if st.button("✕ Close", key="close_wizard3", type="primary",  use_container_width=True):
                        if st.session_state.get("wizard_target_index") is not None:
                            st.session_state["wizard_target_index"] = None
                            st.switch_page("streamlit_app.py")  # Redirect to main page
                        else:
                            st.session_state.show_wizard = False
                            st.session_state.pop("show_wizard_for_edit", None)
                            st.rerun()
        
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
