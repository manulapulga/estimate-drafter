import pandas as pd
import streamlit as st
from fpdf import FPDF
import math
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Side
from item_wizard import show_item_wizard
import base64


# Set page config
st.set_page_config(layout="wide")

# Load user credentials from Sheet 2 of Excel
@st.cache_data
def load_credentials(file_path):
    return pd.read_excel(file_path, sheet_name=1)  # Sheet 2 is index 1

def toggle_section(section_key):
    """Toggle a section and properly collapse all others"""
    # Get current state of the clicked section
    current_state = st.session_state.get(section_key, False)
    
    # List of all expandable section keys
    all_sections = [
        'show_dsr_options',
        'show_price_options',
        'show_dsr21basicrates_options',
        'show_priceapprovedmr_options',
        'show_costindex_options',
        'show_gwd_options',
        'show_pump_selector'
    ]
    
    # If we're opening this section (it was previously closed)
    if not current_state:
        # Close all other sections
        for key in all_sections:
            if key != section_key:
                st.session_state[key] = False
    
    # Toggle the current section
    st.session_state[section_key] = not current_state           
            
# Authentication function
def authenticate(username, password, credentials_df):
    user_row = credentials_df[credentials_df['username'] == username]
    if not user_row.empty:
        return user_row.iloc[0]['password'] == password
    return False

# Load main items data
@st.cache_data
def load_main_items(username):
    try:
        data = pd.read_excel("items.xltm", sheet_name=username)
        return data['Item Name'].tolist(), data['Unit Price'].tolist(), data['Item Unit'].tolist(), data
    except Exception as e:
        st.error(f"Error loading main items data for {username}: {str(e)}")
        st.stop()
        
# Add this with the other data loading functions
@st.cache_data
def load_templates():
    try:
        template_data = pd.read_excel("Templates.xlsx", sheet_name=None)
        return template_data
    except Exception as e:
        st.error(f"Error loading template data: {str(e)}")
        st.stop()
        
# Load wizard items data
@st.cache_data
def load_wizard_items(username):
    try:
        wizard_data = pd.read_excel("items.xltm", sheet_name=username)
        return wizard_data
    except Exception as e:
        st.error(f"Error loading wizard items data for {username}: {str(e)}")
        st.stop()

# Login screen
import streamlit as st

def login_page(credentials_df):
    st.markdown("""
    <div style='text-align: center; margin-top: 0px; margin-bottom: 0px;'>
        <h1 style='color: #103f66; font-size: 36px; font-weight: 700; margin-top: 0px; margin-bottom: 0px;'>
            Ground Water Department
        </h1>
        <h2 style='color: #1a6fa3; font-size: 24px; font-weight: 600; margin-top: 0px; margin-bottom: 0px;'>
            Civil Works Estimate Drafter
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # Create columns to control the width of the input fields
    col1, col2, col3 = st.columns([2, 1, 2])  # 50% width for each input field

    with col2:
        username_input = st.text_input("Username", key="username_input")
        password_input = st.text_input("Password", type="password", key="password_input")
    
    # Login button logic
        if st.button("Login"):
            if authenticate(username_input, password_input, credentials_df):
                st.session_state.logged_in_username = username_input
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    # Add the "Powered by DSR 2021" at the bottom
    st.markdown("""
    <div style='text-align: center; margin-top: 0px; margin-bottom: 0px; color: #3b7ca5; font-size: 14px;'>
        Powered by DSR 2021
        <p style='color: #555; font-size: 15px; margin-top: 0px; margin-bottom: 0px;'>
            Sign in to create, preview, and download professional estimates in Excel and PDF format.
        </p>
    </div>
    """, unsafe_allow_html=True)
# Main app
def main_app():
    # Load data
    username = st.session_state.logged_in_username
    item_names, unit_prices, item_units, data = load_main_items(username)
    wizard_data = load_wizard_items(username)
    
    # UI for Estimate Drafting with updated styles
    st.markdown("<h1 style='text-align: center; color: #154c79;'>ESTIMATE DRAFTER</h1>", unsafe_allow_html=True)
    username = st.session_state.logged_in_username
    # Get the index value for the logged-in user
    user_row = credentials_df[credentials_df['username'] == username]
    cost_index = f"{user_row.iloc[0]['index'] + 1:.4f}" if not user_row.empty and 'index' in user_row.columns else "N/A"
    
    st.markdown(f"""
        <div style='text-align: right; color: #666;'>
            <p>Logged in as: {username}</p>
            <p>Cost Index: {cost_index}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <style>
            .stTextInput input {
                font-size: 100%;
                color: #1e81b0;
            }
            button {
                height: 50% !important;
            }
            .stSelectbox select {
                font-size: 18px;
            }
            .wizard-btn {
                background-color: #4CAF50 !important;
                color: white !important;
            }
            .estimate-item {
                margin-bottom: 1rem;
                padding: 1rem;
                border-radius: 0.5rem;
                background-color: #f8f9fa;
            }
            .item-actions {
                margin-top: 0.5rem;
            }
            .subheading-expander > .streamlit-expanderHeader {
                font-weight: bold !important;
            }
            .wizard-container {
                border: 1px solid #ddd;
                border-radius: 0.5rem;
                padding: 1rem;
                margin: 1rem 0;
                background-color: #f8f9fa;
            }
            .section-cancel-btn {
                background-color: #f44336 !important;
                color: white !important;
            }
            .other-item-btn {
                background-color: #FFA500 !important;
                color: white !important;
            }
        </style>
    """, unsafe_allow_html=True)

    estimate_heading = st.text_input(" ", placeholder="Work Description", key="work_desc")
    st.markdown("<h3 style='text-align: center; color: #76b5c5; font-size: 125%;'>ADD ITEMS TO ESTIMATE</h3>", unsafe_allow_html=True)

    # Initialize session state
    if 'selected_items' not in st.session_state:
        st.session_state.selected_items = []
    if 'item_count' not in st.session_state:
        st.session_state.item_count = 0
    if 'adding_subheading' not in st.session_state:
        st.session_state.adding_subheading = False
    if 'show_wizard' not in st.session_state:
        st.session_state.show_wizard = False
    if 'show_add_item' not in st.session_state:
        st.session_state.show_add_item = False
    if 'show_add_other' not in st.session_state:
        st.session_state.show_add_other = False
    if 'wizard_item_added' not in st.session_state:
        st.session_state.wizard_item_added = False
    if 'show_templates' not in st.session_state:
        st.session_state.show_templates = False    
    if 'show_upload' not in st.session_state:
        st.session_state.show_upload = False
    # Functions
    def add_item():
        st.session_state.item_count += 1

    def remove_item(index):
        st.session_state.selected_items.pop(index)
        st.session_state.item_count = max(0, st.session_state.item_count - 1)
        st.rerun()

    def calculate_totals():
        # Calculate total cost (including all items)
        total_cost = sum(item['Cost'] for item in st.session_state.selected_items if item.get('Type') != 'Subheading')
        
        # Calculate GST only for items where GST is applicable
        taxable_amount = sum(
            item['Cost'] for item in st.session_state.selected_items 
            if item.get('Type') != 'Subheading' and item.get('GST_Applicable', True)
        )
        gst = round(taxable_amount * 0.18, 2)
        
        unforeseen = round(total_cost * 0.05, 2)
        final_total = math.ceil((total_cost + gst + unforeseen) / 1000) * 1000
        return total_cost, gst, unforeseen, final_total
    
    def move_item_up(index):
        if index > 0:
            st.session_state.selected_items[index], st.session_state.selected_items[index - 1] = \
                st.session_state.selected_items[index - 1], st.session_state.selected_items[index]
            st.rerun()
    
    def move_item_down(index):
        if index < len(st.session_state.selected_items) - 1:
            st.session_state.selected_items[index], st.session_state.selected_items[index + 1] = \
                st.session_state.selected_items[index + 1], st.session_state.selected_items[index]
            st.rerun()

    def handle_item_selection(selected_item):
        # Find the item in wizard data first
        wizard_item = wizard_data[wizard_data['Item Name'] == selected_item].iloc[0]
        
        # Try to find matching item in main data for unit price and unit
        main_item = data[data['Item Name'] == selected_item]
        
        if not main_item.empty:
            main_item = main_item.iloc[0]
            unit_price = main_item['Unit Price']
            unit = main_item['Item Unit']
        else:
            # Use wizard data if not found in main data
            unit_price = wizard_item['Unit Price']
            unit = wizard_item['Item Unit']
        
        st.session_state.selected_items.append({
            'Item': selected_item,
            'Quantity': 1.0,
            'Unit Price': unit_price,
            'Item Unit': unit,
            'Cost': unit_price,
            'Type': 'Standard',
            'GST_Applicable': True,
            'Quantity_Remarks': ""
        })
        st.session_state.show_wizard = False
        st.success(f"Item '{selected_item}' added successfully!")
        st.rerun()

    # Display added items and subheadings
    for idx, item in enumerate(st.session_state.selected_items):
        if item.get('Type') == 'Subheading':
            # Modified expander with controlled state
            expanded = st.session_state.get(f"expander_{idx}", False)
            with st.expander(f"📌 {item['Item']}", expanded=expanded):
                # Editable text input for subheading
                new_heading = st.text_input("Edit Subheading", value=item['Item'], key=f"edit_subheading_{idx}")
        
                # Update and Remove buttons
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 6])
                with col1:
                    if st.button("🔁 Update", key=f"update_sub_{idx}"):
                        if new_heading.strip():
                            st.session_state.selected_items[idx]['Item'] = new_heading.strip()
                            st.session_state[f"expander_{idx}"] = False  # Collapse the expander
                            st.success("Subheading updated successfully!")
                            st.rerun()
                with col2:
                    if st.button(f"❌ Remove", key=f"remove_sub_{idx}"):
                        remove_item(idx)
                with col3:    
                    if st.button("⬆️ Move Up", key=f"move_up_sub_{idx}"):
                        move_item_up(idx)
                with col4:
                    if st.button("⬇️ Move Down", key=f"move_down_sub_{idx}"):
                        move_item_down(idx)
            continue


        item_type = item.get('Type', 'Standard')
        item_title = f"💧 Item {idx + 1}: {item['Item']} (₹{item['Cost']:.2f})"
        if item_type == 'Other':
            item_title += " [Other" + (" +GST" if item.get('GST_Applicable', False) else "") + "]"
        
        # Modified expander with controlled state
        expanded = st.session_state.get(f"expander_{idx}", False)
        with st.expander(item_title, expanded=expanded):
                    
            if item_type == 'Other':
                # Enhanced display for "Other" type items with editing capability
                col1, col2 = st.columns([3, 1])
                with col1:
                    # Editable item description
                    new_desc = st.text_input(
                        "Item Description", 
                        value=item['Item'],
                        key=f"other_desc_{idx}"
                    )
                with col2:
                    # Editable total price
                    new_price = st.text_input(
                        "Total Price", 
                        value=f"{item['Cost']:.2f}",
                        key=f"other_price_{idx}"
                    )
                    # Editable GST checkbox
                    new_gst = st.checkbox(
                        "GST Applicable?", 
                        value=item.get('GST_Applicable', False),
                        key=f"other_gst_{idx}"
                    )
                    # Remark Section for 'Other' Items
                    remark = item.get('Quantity_Remarks', '')
                    button_label = "✏️ Edit Remark" if remark else "➕ Add Remark"
                    
                    if st.button(button_label, key=f"edit_remark_other_{idx}"):
                        st.session_state.selected_items[idx]['show_remark_input'] = True
                    
                    if remark and not item.get('show_remark_input', False):
                        st.info(f"📋 Quantity Remark: {remark}")
                    
                    if item.get('show_remark_input', False):
                        new_remark = st.text_input("Edit Remark", value=remark, key=f"remark_input_other_{idx}", max_chars=100)
                        if st.button("Save Remark", key=f"save_remark_other_{idx}"):
                            st.session_state.selected_items[idx]['Quantity_Remarks'] = new_remark
                            st.session_state.selected_items[idx]['show_remark_input'] = False
                            st.rerun()

                    
                # Action buttons
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 6])
                with col1:
                    if st.button(f"🔁 Update", key=f"update_other_{idx}"):
                        if new_desc and new_price:
                            try:
                                price = float(new_price)
                                if price > 0:
                                    st.session_state.selected_items[idx] = {
                                        'Item': new_desc,
                                        'Cost': price,
                                        'Type': 'Other',
                                        'GST_Applicable': new_gst,
                                        'Quantity_Remarks': item.get('Quantity_Remarks', ''),
                                        'show_remark_input': False  # Add this line
                                    }
                                    st.session_state[f"expander_{idx}"] = False  # Add this line to collapse
                                    st.success("Custom item updated successfully!")
                                    st.rerun()
                            except ValueError:
                                st.error("Please enter a valid price")
                with col2:
                    if st.button(f"❌ Remove", key=f"remove_{idx}"):
                        remove_item(idx)
                        
                with col3:
                    if st.button("⬆️ Move Up", key=f"move_up_sub_{idx}"):
                        move_item_up(idx)
                with col4:
                    if st.button("⬇️ Move Down", key=f"move_down_sub_{idx}"):
                        move_item_down(idx)
            else:
                # Display for standard items
                col1, col2 = st.columns([3, 1])
                with col1:
                    item_name = st.selectbox(
                        "Select Item", 
                        [''] + item_names, 
                        index=item_names.index(item['Item']) + 1 if item['Item'] in item_names else 0, 
                        key=f"edit_item_{idx}"
                    )
                    st.text(f"Item Description: {item_name}" if item_name else "")
                with col2:
                    quantity = st.text_input(
                        "Quantity", 
                        str(item['Quantity']), 
                        key=f"edit_qty_{idx}", 
                        placeholder="Input Quantity"
                    )
                    gst_applicable = st.checkbox(
                        "GST Applicable?", 
                        value=item.get('GST_Applicable', True), 
                        key=f"edit_standard_gst_{idx}"
                    )
                    
                    # Show unit rate below quantity
                    st.markdown(f"**Rate:** ₹{item['Unit Price']:.2f} per {item['Item Unit']}")
                    # Quantity Remarks section (for standard items)

                    # Check if a remark already exists
                    remark = item.get('Quantity_Remarks', '')
                    
                    # Change button label based on whether remark exists
                    button_label = "✏️ Edit Remark" if remark else "➕ Add Remark"                    
                    if st.button(button_label, key=f"add_qty_remark_{idx}"):
                        st.session_state.selected_items[idx]['show_remark_input'] = True
                    
                    # Show saved remark always (read-only view)
                    if remark and not item.get('show_remark_input', False):
                        st.info(f"📋 Quantity Remark: {remark}")
                    
                    # Show input box if editing
                    if item.get('show_remark_input', False):
                        new_remark = st.text_input("Edit Remark", value=remark, key=f"qty_remark_{idx}", max_chars=100)
                        if st.button("Save Remark", key=f"save_remark_{idx}"):
                            st.session_state.selected_items[idx]['Quantity_Remarks'] = new_remark
                            st.session_state.selected_items[idx]['show_remark_input'] = False
                            st.session_state[f"expander_{idx}"] = False  # Collapse after saving remark
                            st.rerun()

                # Action buttons inside expander
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 6])
                with col1:
                    if st.button(f"🔁 Update", key=f"update_{idx}"):
                        if item_name and quantity:
                            try:
                                quantity = float(quantity)
                                if quantity > 0:
                                    item_data = data[data['Item Name'] == item_name].iloc[0]
                                    unit_price = item_data['Unit Price']
                                    unit = item_data['Item Unit']
                                    cost = round(quantity * unit_price, 2)
                                    st.session_state.selected_items[idx] = {
                                        'Item': item_name,
                                        'Quantity': quantity,
                                        'Unit Price': unit_price,
                                        'Item Unit': unit,
                                        'Cost': cost,
                                        'Type': 'Standard',
                                        'GST_Applicable': gst_applicable,
                                        'Quantity_Remarks': item.get('Quantity_Remarks', ''),  # Preserve existing remarks
                                        'show_remark_input': False  # Add this line
                                    }
                                    st.session_state[f"expander_{idx}"] = False  # Add this line to collapse
                                    st.success("Item updated successfully!")
                                    st.rerun()
                            except ValueError:
                                st.error("Please enter a valid quantity")
                with col2:
                    if st.button(f"❌ Remove", key=f"remove_{idx}"):
                        remove_item(idx)
                with col3:
                    if st.button("⬆️ Move Up", key=f"move_up_sub_{idx}"):
                        move_item_up(idx)
                with col4:
                    if st.button("⬇️ Move Down", key=f"move_down_sub_{idx}"):
                        move_item_down(idx)
    # Add New Item or Subheading buttons
    button_col1, button_col2, button_col3, button_col4, button_col5, button_col6 = st.columns([2, 2, 2, 2, 2, 2])
    with button_col1:
        if st.button("➕ Add Item", key="add_item_btn"):
            # Toggle add item section and hide others
            st.session_state.show_add_item = not st.session_state.get('show_add_item', False)
            st.session_state.show_wizard = False
            st.session_state.adding_subheading = False
            st.session_state.show_add_other = False
            st.session_state.show_templates = False  # Add this line
            st.session_state.show_upload = False    # Add this line
            st.rerun()
    with button_col2:
        if st.button("🔍 Smart Filter", key="open_wizard"):
            # Toggle wizard and hide others
            st.session_state.show_wizard = not st.session_state.get('show_wizard', False)
            st.session_state.show_add_item = False
            st.session_state.adding_subheading = False
            st.session_state.show_add_other = False
            st.session_state.show_templates = False  # Add this line
            st.session_state.show_upload = False    # Add this line
            st.rerun()
    with button_col3:
        if st.button("➕ Add Subheading", key="add_subheading_btn"):
            # Toggle subheading and hide others
            st.session_state.adding_subheading = not st.session_state.get('adding_subheading', False)
            st.session_state.show_add_item = False
            st.session_state.show_wizard = False
            st.session_state.show_add_other = False
            st.session_state.show_templates = False  # Add this line
            st.session_state.show_upload = False    # Add this line
            st.rerun()
    with button_col4:
        if st.button("➕ Add Other", key="add_other_btn", type="secondary", 
                    help="Add custom items not in database"):
            # Toggle other items section and hide others
            st.session_state.show_add_other = not st.session_state.get('show_add_other', False)
            st.session_state.show_add_item = False
            st.session_state.show_wizard = False
            st.session_state.adding_subheading = False
            st.session_state.show_templates = False  # Add this line
            st.session_state.show_upload = False    # Add this line
            st.rerun()
    with button_col5:
        if st.button("📘 Templates", key="show_templates_btn"):
            st.session_state.show_templates = not st.session_state.get('show_templates', False)
            st.session_state.show_add_item = False
            st.session_state.show_wizard = False
            st.session_state.adding_subheading = False
            st.session_state.show_add_other = False
            st.session_state.show_upload = False    # Add this line
            st.rerun()
    with button_col6:
        # Replace your existing upload button with this:
        if st.button("⬆️ Upload Excel", key="show_upload_btn"):
            st.session_state.show_upload = not st.session_state.get('show_upload', False)
            st.session_state.show_templates = False
            st.session_state.show_add_item = False
            st.session_state.show_wizard = False
            st.session_state.adding_subheading = False
            st.session_state.show_add_other = False
            st.rerun()
    # Show Add Item section if toggled on
    if st.session_state.get('show_add_item', False):
        idx = len([i for i in st.session_state.selected_items if i.get("Type") != "Subheading"])
        with st.container():
            st.markdown(f"<div class='estimate-item'>", unsafe_allow_html=True)
            col1, col2 = st.columns([3, 1])
            with col1:
                item_name = st.selectbox(
                    "Select Item", 
                    [''] + item_names, 
                    key=f"new_item_{idx}"
                )
                st.text(f"Item Description: {item_name}" if item_name else "")
            with col2:
                quantity = st.text_input(
                    "Quantity", 
                    "1", 
                    key=f"new_qty_{idx}", 
                    placeholder="Input Quantity"
                )
                gst_applicable = st.checkbox(
                    "GST Applicable?", 
                    value=True, 
                    key=f"new_item_gst_{idx}"
                )
                if item_name != '':
                    item_data = data[data['Item Name'] == item_name].iloc[0]
                    unit_price = item_data['Unit Price']
                    unit = item_data['Item Unit']
                    st.text(f"Rate: {unit_price:.2f}/{unit}")
                    if quantity:
                        try:
                            qty = float(quantity)
                            if qty > 0:
                                total = qty * unit_price
                                st.text(f"Amount: {total:.2f}")
                        except ValueError:
                            st.text("Invalid quantity")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"Add to Estimate", key=f"add_{idx}"):
                    if item_name and quantity:
                        try:
                            quantity = float(quantity)
                            if quantity > 0:
                                item_data = data[data['Item Name'] == item_name].iloc[0]
                                unit_price = item_data['Unit Price']
                                unit = item_data['Item Unit']
                                cost = round(quantity * unit_price, 2)
                                st.session_state.selected_items.append({
                                    'Item': item_name,
                                    'Quantity': quantity,
                                    'Unit Price': unit_price,
                                    'Item Unit': unit,
                                    'Cost': cost,
                                    'Type': 'Standard',
                                    'GST_Applicable': gst_applicable,
                                    'Quantity_Remarks': ""
                                })
                                st.session_state.show_add_item = False
                                st.success(f"Item '{item_name}' added successfully!")
                                st.rerun()
                        except ValueError:
                            st.error("Please enter a valid quantity")
            with col2:
                if st.button("✕ Cancel", key=f"cancel_add_{idx}", type="primary", 
                            help="Close without adding item"):
                    st.session_state.show_add_item = False
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # Show Smart Filter if toggled on
    if st.session_state.get('show_wizard', False):
        show_item_wizard(wizard_data, handle_item_selection)
        if st.button("✕ Close Wizard", key="close_wizard", type="primary"):
            st.session_state.show_wizard = False
            st.rerun()
        # Show Templates section if toggled on
    if st.session_state.get('show_templates', False):
        template_data = load_templates()
        template_names = list(template_data.keys())
        
        selected_template = st.selectbox("Select a Template", template_names, key="template_select")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Add Template Items", key="add_template_items"):
                template_df = template_data[selected_template]
                main_items_data = data  # From your existing load_main_items()
                
                for _, row in template_df.iterrows():
                    item_name = row['Item Name']
                    quantity = row['Quantity']
                    
                    # Find the item in main data
                    main_item = main_items_data[main_items_data['Item Name'] == item_name]
                    
                    if not main_item.empty:
                        main_item = main_item.iloc[0]
                        st.session_state.selected_items.append({
                            'Item': item_name,
                            'Quantity': quantity,
                            'Unit Price': main_item['Unit Price'],
                            'Item Unit': main_item['Item Unit'],
                            'Cost': quantity * main_item['Unit Price'],
                            'Type': 'Standard',
                            'GST_Applicable': True,
                            'Quantity_Remarks': ""
                        })
                    else:
                        # If item not found in main data, add as "Other"
                        st.session_state.selected_items.append({
                            'Item': item_name,
                            'Cost': 0,  # Or you could prompt for price
                            'Type': 'Other',
                            'GST_Applicable': True
                        })
                
                st.success(f"Added {len(template_df)} items from '{selected_template}' template!")
                st.session_state.show_templates = False
                st.rerun()
        
        with col2:
            if st.button("✕ Cancel", key="cancel_template", type="primary"):
                st.session_state.show_templates = False
                st.rerun()
    # Excel upload section            
    if st.session_state.get('show_upload', False):
        # Add this error handling block FIRST
        try:
            sample_data = base64.b64encode(open("Sample.xlsx", "rb").read()).decode("utf-8")
        except FileNotFoundError:
            st.error("Sample file not found")
            sample_data = ""
        st.markdown("""
        <div style="background-color:#f0f2f6; padding:12px; border-radius:8px; margin-bottom:16px;">
            <p style="margin:0 0 12px 0; font-size:14px; color:#333;">
            <b>Upload Guide:</b> You can upload either:<br>
            1. Estimates generated by this app (auto-detected), OR<br>
            2. Custom Excel files with item names in first column and quantities in second column, including column titles </p>
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size:13px; color:#555;">Download sample format:</span>
                <a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{0}" download="Sample_Format.xlsx" style="text-decoration: none;">
                    <button style="background-color:#4CAF50; color:white; border:none; padding:6px 12px; 
                                border-radius:4px; font-size:13px; cursor:pointer;">
                        ⬇️ Download Sample Excel
                    </button>
                </a>
            </div>
        </div>
        """.format(base64.b64encode(open("Sample.xlsx", "rb").read()).decode("utf-8")), 
        unsafe_allow_html=True)
    
        uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx'], key="excel_uploader")
        
        if uploaded_file is not None:
            try:
                # Read the uploaded file with openpyxl to handle merged cells
                from openpyxl import load_workbook
                wb = load_workbook(uploaded_file)
                ws = wb.active
                
                # Check if it's an estimate generated by this app
                is_app_estimate = False
                try:
                    # Check for the specific format of our app's estimate
                    if (ws['B2'].value == "Item Name" and
                        ws['E2'].value == "Qty"):
                        is_app_estimate = True
                except:
                    pass
                
                if is_app_estimate:
                    # Find the "Subtotal" row by checking merged cells
                    subtotal_row = None
                    for merge in ws.merged_cells.ranges:
                        if merge.min_row == merge.max_row:  # Only consider row merges
                            first_cell = ws.cell(row=merge.min_row, column=merge.min_col)
                            if first_cell.value == "Subtotal":
                                subtotal_row = merge.min_row
                                break
                    
                    if subtotal_row is None:
                        st.error("Could not find 'Subtotal' row in the uploaded estimate")
                        return
                    
                    # Collect items between row 3 (first item) and subtotal_row
                    items = []
                    current_subheading = None
                    
                    for row in range(3, subtotal_row):
                        # Check if this row has any horizontal merged cells (subheading)
                        is_subheading = False
                        for merge in ws.merged_cells.ranges:
                            if merge.min_row == row and merge.max_row == row:  # Horizontal merge only
                                if merge.min_col <= 2 and merge.max_col >= 2:  # Merge includes column B
                                    current_subheading = ws.cell(row=row, column=merge.min_col).value
                                    is_subheading = True
                                    break
                        
                        if is_subheading:
                            # Add the subheading to our items list
                            items.append({
                                'Item Name': current_subheading,
                                'Type': 'Subheading',
                                'Merged': True
                            })
                            continue
                        
                        # Process regular items
                        item_name = ws.cell(row=row, column=2).value  # Column B
                        quantity_cell = ws.cell(row=row, column=5).value  # Column E
                        total_price_cell = ws.cell(row=row, column=6).value  # Column F (Total)
                        
                        # Skip empty rows
                        if not item_name:
                            continue
                        
                        # Process quantity cell to extract remarks
                        quantity_str = str(quantity_cell).strip() if quantity_cell is not None else ""
                        remarks = ""
                        
                        if "(" in quantity_str and ")" in quantity_str:
                            parts = quantity_str.split("(", 1)
                            remarks = parts[1].split(")", 1)[0].strip()
                        
                        quantity = None
                        if quantity_str and quantity_str != "-":
                            try:
                                quantity = float(quantity_str.split("(")[0].strip())
                            except ValueError:
                                pass
                        
                        total_price = 0.0
                        if total_price_cell is not None:
                            try:
                                total_price = float(total_price_cell)
                            except (ValueError, TypeError):
                                pass
                        
                        items.append({
                            'Item Name': item_name, 
                            'Quantity': quantity,
                            'Remarks': remarks,
                            'Total Price': total_price,
                            'Subheading': current_subheading  # Track which subheading this item belongs to
                        })
                    
                    items_df = pd.DataFrame(items)
                else:
                    # Original behavior for regular Excel files using pandas
                    uploaded_df = pd.read_excel(uploaded_file)
                    if len(uploaded_df.columns) < 2:
                        st.error("The Excel file must have at least 2 columns (Item Name and Quantity)")
                        return
                    
                    # Get the first two columns plus the third column if available (for total price)
                    if len(uploaded_df.columns) >= 3:
                        items_df = uploaded_df.iloc[:, [0, 1, 2]]
                        items_df.columns = ['Item Name', 'Quantity', 'Total Price']
                    else:
                        items_df = uploaded_df.iloc[:, [0, 1]]
                        items_df.columns = ['Item Name', 'Quantity']
                        items_df['Total Price'] = 0.0  # Add default total price column
                    
                    # Process quantity column to extract remarks
                    def process_quantity(qty):
                        if pd.isna(qty):
                            return None, ""
                        
                        qty_str = str(qty).strip()
                        remarks = ""
                        
                        if "(" in qty_str and ")" in qty_str:
                            parts = qty_str.split("(", 1)
                            remarks = parts[1].split(")", 1)[0].strip()
                        
                        quantity = None
                        if qty_str and qty_str != "-":
                            try:
                                quantity = float(qty_str.split("(")[0].strip())
                            except ValueError:
                                pass
                        
                        return quantity, remarks
                    
                    # Apply processing to quantity column
                    processed = items_df['Quantity'].apply(process_quantity)
                    items_df['Quantity'] = [x[0] for x in processed]
                    items_df['Remarks'] = [x[1] for x in processed]
                    
                    # Process total price column
                    items_df['Total Price'] = items_df['Total Price'].apply(
                        lambda x: float(x) if pd.notna(x) and str(x).replace('.','',1).isdigit() else 0.0
                    )
                
                if items_df.empty:
                    st.error("No valid items found in the uploaded file")
                    return
                
                # Display preview
                st.markdown("**Preview of uploaded items:**")
                st.dataframe(items_df.head())
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Add Uploaded Items", key="add_uploaded_items"):
                        main_items_data = data
                        added_count = 0
                        
                        for _, row in items_df.iterrows():
                            if row.get('Type') == 'Subheading':
                                # Add subheading to the estimate
                                st.session_state.selected_items.append({
                                    'Item': row['Item Name'],
                                    'Type': 'Subheading'
                                })
                                continue
                                
                            item_name = row['Item Name']
                            quantity = row['Quantity']
                            remarks = row.get('Remarks', '')
                            total_price = row.get('Total Price', 0.0)
                            
                            # Find the item in main data
                            main_item = main_items_data[main_items_data['Item Name'] == item_name]
                            
                            if not main_item.empty and quantity is not None:
                                # Standard item
                                main_item = main_item.iloc[0]
                                st.session_state.selected_items.append({
                                    'Item': item_name,
                                    'Quantity': float(quantity),
                                    'Unit Price': main_item['Unit Price'],
                                    'Item Unit': main_item['Item Unit'],
                                    'Cost': float(quantity) * main_item['Unit Price'],
                                    'Type': 'Standard',
                                    'GST_Applicable': True,
                                    'Quantity_Remarks': remarks
                                })
                                added_count += 1
                            else:
                                # Other item
                                st.session_state.selected_items.append({
                                    'Item': item_name,
                                    'Cost': float(total_price),
                                    'Type': 'Other',
                                    'GST_Applicable': True,
                                    'Quantity_Remarks': remarks
                                })
                                added_count += 1
                        
                        st.success(f"Added {added_count} items from uploaded file!")
                        st.session_state.show_upload = False
                        st.rerun()
                
                with col2:
                    if st.button("✕ Cancel", key="cancel_upload", type="primary"):
                        st.session_state.show_upload = False
                        st.rerun()
            except Exception as e:
                st.error(f"Error reading Excel file: {str(e)}")
        else:
            if st.button("✕ Cancel", key="cancel_upload_no_file", type="primary"):
                st.session_state.show_upload = False
                st.rerun()         
    # Show Subheading section if toggled on
    if st.session_state.get('adding_subheading', False):
        subheading = st.text_input("Enter Subheading", key="new_subheading")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Add Subheading to Estimate", key="confirm_subheading"):
                if subheading.strip():
                    st.session_state.selected_items.append({
                        'Item': subheading.strip(),
                        'Type': 'Subheading'
                    })
                    st.session_state.adding_subheading = False
                    st.success(f"Subheading '{subheading.strip()}' added!")
                    st.rerun()
                else:
                    st.warning("Please enter a valid subheading.")
        with col2:
            if st.button("✕ Cancel", key="cancel_subheading", type="primary"):
                st.session_state.adding_subheading = False
                st.rerun()

    # Show Add Other section if toggled on
    if st.session_state.get('show_add_other', False):
        with st.container():
            st.markdown(f"<div class='estimate-item'>", unsafe_allow_html=True)
            col1, col2 = st.columns([3, 1])
            with col1:
                item_name = st.text_input(
                    "Item Description", 
                    key=f"other_item_name",
                    placeholder="Enter custom item description"
                )
            with col2:
                total_price = st.text_input(
                    "Total Price", 
                    key=f"other_item_price",
                    placeholder="Enter total price"
                )
                gst_applicable = st.checkbox(
                    "GST Applicable?", 
                    value=True,
                    key=f"other_item_gst"
                )

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"Add Custom Item", key=f"add_other_item"):
                    if item_name and total_price:
                        try:
                            price = float(total_price)
                            if price > 0:
                                st.session_state.selected_items.append({
                                    'Item': item_name,
                                    'Cost': price,
                                    'Type': 'Other',
                                    'GST_Applicable': gst_applicable
                                })
                                st.session_state.show_add_other = False
                                st.success(f"Custom item '{item_name}' added successfully!")
                                st.rerun()
                        except ValueError:
                            st.error("Please enter a valid price")
            with col2:
                if st.button("✕ Cancel", key=f"cancel_other_item", type="primary", 
                            help="Close without adding item"):
                    st.session_state.show_add_other = False
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # Totals and file generation
    if any(i.get("Type") != "Subheading" for i in st.session_state.selected_items):
        total_cost, gst, unforeseen, final_total = calculate_totals()
        st.subheader("Estimate Breakdown")
        st.write(f"Subtotal: ₹{total_cost:,.2f}")
        st.write(f"GST (18% on taxable items): ₹{gst:,.2f}")
        st.write(f"Unforeseen (5%): ₹{unforeseen:,.2f}")
        st.write(f"Final Total (Rounded): ₹{final_total:,.2f}")

        # File generation buttons
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            if st.button("📄 Generate Excel", key="generate_excel"):
                wb = Workbook()
                ws = wb.active
                ws.title = "Estimate"
                
                # Header
                ws.merge_cells('A1:G1')
                ws['A1'] = estimate_heading
                ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
                ws['A1'].font = ws['A1'].font.copy(bold=True, size=14)
                
                # Table headers
                headers = ["Sl.No", "Item Name", "Rate", "Unit", "Qty", "Total", "GST"]
                ws.append(headers)
                
                # Add items
                row_num = 3
                serial = 1
                for item in st.session_state.selected_items:
                    if item.get("Type") == "Subheading":
                        ws.merge_cells(f'A{row_num}:G{row_num}')
                        ws[f'A{row_num}'] = f" {item['Item']}"
                        row_num += 1
                    elif item.get("Type") == "Other":
                        remark = item.get('Quantity_Remarks', '')
                        qty_field = f"- ({remark})" if remark else "-"
                        ws.append([
                            serial,
                            item['Item'],
                            "-",
                            "-",
                            qty_field,
                            item['Cost'],
                            "Yes" if item.get('GST_Applicable', False) else "No"
                        ])
                        serial += 1
                        row_num += 1
                    else:
                        ws.append([
                            serial,
                            item['Item'],
                            item['Unit Price'],
                            item['Item Unit'],
                            f"{item['Quantity']} ({item['Quantity_Remarks']})" if item.get('Quantity_Remarks') else item['Quantity'],
                            item['Cost'],
                            "Yes" if item.get('GST_Applicable', True) else "No"
                        ])
                        serial += 1
                        row_num += 1

                # Add totals
                for label, val in [
                    ("Subtotal", total_cost),
                    ("GST (18%)", gst),
                    ("Unforeseen (5%)", unforeseen),
                    ("Grand Total Rounded To Next 1000", final_total)
                ]:
                    ws.merge_cells(f'A{row_num}:E{row_num}')
                    ws[f'A{row_num}'] = label
                    ws[f'F{row_num}'] = val
                    row_num += 1

                # Apply styling
                thin_border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
                
                for row in ws.iter_rows(min_row=1, max_row=row_num-1, min_col=1, max_col=7):
                    for cell in row:
                        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
                        cell.border = thin_border

                ws.column_dimensions['B'].width = 70
                excel_file = "estimate.xlsx"
                wb.save(excel_file)

                with open(excel_file, "rb") as f:
                    st.download_button(
                        "⬇️ Download Excel",
                        f,
                        file_name=excel_file,
                        mime="application/vnd.ms-excel",
                        key="download_excel"
                    )
        with col2:
              if st.button("Generate PDF"):
                  from fpdf import FPDF
              
                  pdf = FPDF()
                  def add_watermark(pdf):
                      """Function to add a diagonal watermark to every page"""
                      pdf.set_font("Arial", style='B', size=72)
                      pdf.set_text_color(230, 230, 230)  # Light grey color for watermark
                  
                      text = "GROUND WATER DEPARTMENT"
                      text_width = pdf.get_string_width(text)
                      text_height = 72  # Approximate height of the text
                  
                      # Set the rotation angle for the watermark (diagonal, bottom-left to top-right)
                      pdf.rotate(54.8, x=0, y=pdf.h)  # Rotate around the bottom-left corner
                  
                      # Position the text starting from the bottom-left corner with a little padding
                      x = 0  # Padding from the left
                      y = pdf.h  # Padding from the bottom
                  
                      # Print the watermark diagonally
                      pdf.text(x, y, text)
                  
                      # Reset rotation to avoid affecting other content
                      pdf.rotate(0)
                      
                      pdf.set_text_color(0, 0, 0)  # Black color for the main content
                        
                  pdf.set_auto_page_break(auto=True, margin=15)
                  pdf.add_page()
                  add_watermark(pdf)
                  # Main content
                  pdf.set_font("Arial", 'B', 16)
                  pdf.set_text_color(0, 0, 0)
                  
                  # Add user info at top right
                  pdf.set_font("Arial", '', 10)
                  user_info = f"User: {username}\nCost Index: {cost_index}"
                  pdf.set_xy(pdf.w - 60, 15)  # Position at top right with some margin
                  pdf.multi_cell(50, 5, user_info, 0, 'R')  # Right-aligned multi-cell for multiple lines
                  
                  # Center the main heading below the user info
                  pdf.set_y(40)  # Move down a bit from top
                  pdf.set_font("Arial", 'B', 16)
                  
                  # Calculate width of heading text
                  heading_width = pdf.get_string_width(estimate_heading)
                  
                  # If heading is too wide for page (with 20mm margins on each side)
                  if heading_width > (pdf.w - 40):
                      # Split heading into multiple lines
                      words = estimate_heading.split()
                      lines = []
                      current_line = ""
                      
                      for word in words:
                          test_line = f"{current_line} {word}" if current_line else word
                          if pdf.get_string_width(test_line) < (pdf.w - 40):
                              current_line = test_line
                          else:
                              lines.append(current_line)
                              current_line = word
                      if current_line:
                          lines.append(current_line)
                      
                      # Write each line centered
                      for line in lines:
                          pdf.cell(200, 10, txt=line, ln=True, align='C')
                  else:
                      # Single line if it fits
                      pdf.cell(200, 10, txt=estimate_heading, ln=True, align='C')

              
                  col_widths = [10, 70, 20, 20, 20, 30]
                  headers = ["Sl.No", "Item Name", "Rate", "Unit", "Qty", "Total"]
              
                  def split_text(text, max_width):
                      """Split text into multiple lines based on available width"""
                      if not isinstance(text, str):
                          text = str(text)
                      lines = []
                      words = text.split()
                      current_line = ""
              
                      for word in words:
                          test_line = current_line + " " + word if current_line else word
                          if pdf.get_string_width(test_line) < max_width - 2:
                              current_line = test_line
                          else:
                              lines.append(current_line)
                              current_line = word
                      if current_line:
                          lines.append(current_line)
                      return lines
              
                  def calculate_max_lines(row_data):
                      """Calculate maximum lines needed for any cell in the row"""
                      max_lines = 1
                      for i, text in enumerate(row_data):
                          lines = split_text(str(text), col_widths[i])
                          if len(lines) > max_lines:
                              max_lines = len(lines)
                      return max_lines
              
                  def draw_table_header():
                      """Draw the table header on new pages"""
                      pdf.set_font("Arial", 'B', 10)
                      x_start = pdf.get_x()
                      y_start = pdf.get_y()
                      pdf.rect(x_start, y_start, sum(col_widths), 6)  # Header border
              
                      for i in range(1, len(col_widths)):
                          pdf.line(
                              x_start + sum(col_widths[:i]), y_start,
                              x_start + sum(col_widths[:i]), y_start + 6
                          )
              
                      for i, header in enumerate(headers):
                          pdf.set_xy(x_start + sum(col_widths[:i]), y_start)
                          pdf.cell(col_widths[i], 6, header, 0, 0, 'C')
              
                      pdf.set_y(y_start + 6)
              
                  pdf.ln(10)
                  draw_table_header()
                  pdf.set_font("Arial", '', 10)
              
                  serial = 1
                  for item in st.session_state.selected_items:
                      # Check if we need a new page (with buffer for row height)
                      if pdf.get_y() + 20 > pdf.h - 30:  # Increased buffer to 20
                          pdf.add_page()
                          add_watermark(pdf)
                          draw_table_header()
                          pdf.set_font("Arial", '', 10)  # Reset font after header
              
                      if item.get("Type") == "Subheading":
                          pdf.set_font("Arial", 'B', 10)  # Subheading bold
                          pdf.set_xy(pdf.get_x(), pdf.get_y())
                          pdf.cell(sum(col_widths), 6, f" {item['Item']}", border=1, align='C')
                          pdf.ln(6)
                          pdf.set_font("Arial", '', 10)
                          continue  # Skip to next item after subheading
                      
                      gst_applicable = item.get('GST_Applicable', True)
              
                      if item.get("Type") == "Other":
                          rate_text = "-"
                          unit_text = "-"
                          remark = item.get('Quantity_Remarks', '')
                          qty_text = f"- ({remark})" if remark else "-"
                      else:
                          rate_text = f"{item['Unit Price']:.2f}"
                          unit_text = item['Item Unit']
                          remark = item.get('Quantity_Remarks', '')
                          if remark:
                              qty_text = f"{item['Quantity']:.2f} ({remark})"
                          else:
                              remark = item.get('Quantity_Remarks', '')
                              if remark:
                                  qty_text = f"{item['Quantity']:.2f} ({remark})"
                              else:
                                  qty_text = f"{item['Quantity']:.2f}"
              
                      total_text = f"{item['Cost']:.2f}"
                      if not gst_applicable:
                          total_text += " (No GST)"
              
                      row_data = [
                          str(serial),
                          item['Item'],
                          rate_text,
                          unit_text,
                          qty_text,
                          total_text
                      ]
              
                      x_row_start = pdf.get_x()
                      y_row_start = pdf.get_y()
              
                      max_lines = calculate_max_lines(row_data)
                      row_height = 6 * max_lines
                      
                      # Ensure we have space for this row
                      if pdf.get_y() + row_height > pdf.h - 30:
                          pdf.add_page()
                          add_watermark(pdf)
                          draw_table_header()
                          pdf.set_font("Arial", '', 10)
                          x_row_start = pdf.get_x()
                          y_row_start = pdf.get_y()
              
                      # Draw the row border
                      pdf.rect(x_row_start, y_row_start, sum(col_widths), row_height)
                      
                      # Draw vertical lines
                      for i in range(1, len(col_widths)):
                          pdf.line(
                              x_row_start + sum(col_widths[:i]), y_row_start,
                              x_row_start + sum(col_widths[:i]), y_row_start + row_height
                          )
              
                      # If the item type is "Other", round the serial number
                      if item.get("Type") == "Other":
                          # Draw a circle for serial number
                          x = x_row_start + col_widths[0] / 2
                          y = y_row_start + row_height / 2
                          r = 4  # radius
                          pdf.ellipse(x - r, y - r, r * 2, r * 2)
                  
                          # Set the serial number for the first column and round it
                          pdf.set_xy(x_row_start, y_row_start)
                          pdf.cell(col_widths[0], row_height, str(round(serial)), 0, 0, 'C')
                      else:
                          pdf.set_xy(x_row_start, y_row_start)
                          pdf.cell(col_widths[0], row_height, str(serial), 0, 0, 'C')  # Normal serial number
              
                      for i, text in enumerate(row_data[1:], 1):  # Start from index 1 (skip serial number)
                          pdf.set_xy(x_row_start + sum(col_widths[:i]), y_row_start)
              
                          cell_lines = split_text(str(text), col_widths[i])
              
                          vertical_offset = (row_height - (6 * len(cell_lines))) / 2
              
                          for line in cell_lines:
                              pdf.set_xy(x_row_start + sum(col_widths[:i]), y_row_start + vertical_offset)
                              pdf.cell(col_widths[i], 6, line, 0, 0, 'C')
                              vertical_offset += 6
              
                      pdf.set_y(y_row_start + row_height)
                      serial += 1
              
                  # Summary Section
                  summary_data = [
                      ("Subtotal", f"{total_cost:.2f}"),
                      ("GST (18%)", f"{gst:.2f}"),
                      ("Unforeseen (5%)", f"{unforeseen:.2f}"),
                      ("Grand Total Rounded To Next 1000", f"{final_total:.2f}")
                  ]
              
                  for label, value in summary_data:
                      row_height = 8
                      if pdf.get_y() + row_height > pdf.h - 30:
                          pdf.add_page()
                          add_watermark(pdf)
                          pdf.set_font("Arial", '', 10)  # Reset the correct font and size
                  
                      x = pdf.get_x()
                      y = pdf.get_y()
                      
                      # Set bold font for summary items
                      pdf.set_font("Arial", 'B', 10)  # Changed to bold

                      # Draw both label and value in the same row
                      pdf.set_xy(x, y)
                      pdf.cell(sum(col_widths[:-1]), row_height, label, border=1, align='C')
                  
                      pdf.set_xy(x + sum(col_widths[:-1]), y)
                      pdf.cell(col_widths[-1], row_height, value, border=1, align='C')
                  
                      # Move to next line
                      pdf.set_y(y + row_height)
              
                  # Signature Area
                  if pdf.get_y() + 20 > pdf.h - 30:
                      pdf.add_page()
              
                  pdf.set_font("Arial", 'B', 12)
                  pdf.set_xy(pdf.w - 70, pdf.h - 40)
                  pdf.cell(60, 10, "District Officer", ln=True, align='C')
                  pdf.set_xy(pdf.w - 70, pdf.h - 30)
                  pdf.cell(60, 10, "(Seal & Signature)", ln=True, align='C')
              
                  # Save and offer download
                  pdf_file = "estimate.pdf"
                  pdf.output(pdf_file)
              
                  with open(pdf_file, "rb") as f:
                      st.download_button(
                          label="⬇️ Download PDF",
                          data=f,
                          file_name=pdf_file,
                          mime="application/pdf"
                      )
        with col3:
            if st.button("🗑️ Clear All", key="clear_all", 
                        help="Remove all items and start fresh"):
                st.session_state.selected_items = []
                st.session_state.item_count = 0
                st.session_state.adding_subheading = False
                st.session_state.show_wizard = False
                st.session_state.show_add_item = False
                st.session_state.show_add_other = False
                st.rerun()        
    else:
        st.info("No items added to the estimate yet.")
# Check authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.logged_in_username = None

# Load credentials
try:
    credentials_df = load_credentials("items.xltm")
except Exception as e:
    st.error(f"Error loading credentials: {str(e)}")
    st.stop()

if st.session_state.authenticated:
    main_app()
else:
    login_page(credentials_df)
    
st.sidebar.markdown("""
<style>
    /* Main buttons - keep existing style */
    section[data-testid="stSidebar"] button:not(.stDownloadButton button, .pump-selector-btn button) {
        width: 100% !important;
        margin: 5px 0 !important;
        padding: 10px !important;
        font-size: 14px !important;
        border-radius: 5px !important;
        border: 1px solid #2387eb !important;
        background-color: #e8f2fc !important;
        color: black !important;
        transition: all 0.3s !important;
    }
    
    /* Download/secondary buttons - green style */
    section[data-testid="stSidebar"] .stDownloadButton button,
    section[data-testid="stSidebar"] .pump-selector-btn button {
        background-color: #4CAF50 !important;
        color: white !important;
        border: 1px solid #2E7D32 !important;
        width: 100% !important;
        margin: 5px 0 !important;
        padding: 10px !important;
        font-size: 14px !important;
        border-radius: 5px !important;
        transition: all 0.3s !important;
    }
    
    /* Hover states */
    section[data-testid="stSidebar"] button:not(.stDownloadButton button, .pump-selector-btn button):hover {
        color: white !important;
        background-color: #154c79 !important;
        border-color: #154c79 !important;
    }
    
    section[data-testid="stSidebar"] .stDownloadButton button:hover,
    section[data-testid="stSidebar"] .pump-selector-btn button:hover {
        background-color: #388E3C !important;
        border-color: #1B5E20 !important;
    }
    
    /* Active states */
    section[data-testid="stSidebar"] button:not(.stDownloadButton button, .pump-selector-btn button):active {
        background-color: #103f66 !important;
        border-color: #103f66 !important;
    }
    
    section[data-testid="stSidebar"] .stDownloadButton button:active,
    section[data-testid="stSidebar"] .pump-selector-btn button:active {
        background-color: #2E7D32 !important;
    }
</style>
""", unsafe_allow_html=True)


if st.session_state.get('authenticated', False):
    # Add the DSR download button and dropdowns
    # DSR/DAR button
    if st.sidebar.button("Download DSR/DAR"):
        toggle_section('show_dsr_options')
        st.rerun()  # Force immediate update

    if st.session_state.get('show_dsr_options', False):
        # Year selection
        selected_year = st.sidebar.selectbox("Select Year", ["2018", "2021"])
        
        # Document type selection
        doc_type = st.sidebar.selectbox("Select Document Type", ["DSR", "DAR"])
        
        # Volume selection
        volume = st.sidebar.selectbox("Select Volume", ["Vol 1", "Vol 2"])
        
        # Construct the file path
        file_path = f"DSR/{selected_year}/{doc_type}/{volume}.pdf"
        
        # Display download button
        try:
            with open(file_path, "rb") as file:
                st.sidebar.download_button(
                    label=f"⬇️ Download {selected_year} {doc_type} {volume}",
                    data=file,
                    file_name=f"{selected_year}_{doc_type}_{volume}.pdf",
                    mime="application/pdf"
                )
        except FileNotFoundError:
            st.sidebar.error("Requested file not found")
        except Exception as e:
            st.sidebar.error(f"Error downloading file: {str(e)}")
    if 'show_price_options' not in st.session_state:
        st.session_state.show_price_options = False
    # Add PRICE Rates download button
    # PRICE Rates button
    if st.sidebar.button("Download PRICE Rates"):
        toggle_section('show_price_options')
        st.rerun()

    if st.session_state.get('show_price_options', False):
        try:
            with open("PRICE Rates (DSR 21).xlsx", "rb") as file:
                st.sidebar.download_button(
                    label="⬇️ Download PRICE Rates (DSR 21) Excel",
                    data=file,
                    file_name="PRICE Rates (DSR 21).xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except FileNotFoundError:
            st.sidebar.error("PRICE Rates file not found")
        except Exception as e:
            st.sidebar.error(f"Error downloading PRICE Rates: {str(e)}")
            
    if 'show_dsr21basicrates_options' not in st.session_state:
        st.session_state.show_dsr21basicrates_options = False
    # Add DSR 21 Basic Rates download button
    # Basic Rates button
    if st.sidebar.button("Download Basic Rates"):
        toggle_section('show_dsr21basicrates_options')
        st.rerun()

    
    if st.session_state.get('show_dsr21basicrates_options', False):
        try:
            with open("DSR 21 Basic Rates.xlsx", "rb") as file:
                st.sidebar.download_button(
                    label="⬇️ Download Basic Rates (DSR 21) Excel",
                    data=file,
                    file_name="DSR 21 Basic Rates.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except FileNotFoundError:
            st.sidebar.error("DSR 21 Basic Rates file not found")
        except Exception as e:
            st.sidebar.error(f"Error downloading DSR 21 Basic Rates: {str(e)}")
        try:
            with open("DSR 21 Basic Rates.pdf", "rb") as file:
                st.sidebar.download_button(
                    label="⬇️ Download Basic Rates (DSR 21) PDF",
                    data=file,
                    file_name="DSR 21 Basic Rates.pdf",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except FileNotFoundError:
            st.sidebar.error("DSR 21 Basic Rates file not found")
        except Exception as e:
            st.sidebar.error(f"Error downloading DSR 21 Basic Rates: {str(e)}")    
    if 'show_priceapprovedmr_options' not in st.session_state:
        st.session_state.show_priceapprovedmr_options = False
    
    # Add PRICE Approved MR download button
    # PRICE Approved MR button
    if st.sidebar.button("PRICE Approved MR"):
        toggle_section('show_priceapprovedmr_options')
        st.rerun()
    
    if st.session_state.get('show_priceapprovedmr_options', False):
        try:
            with open("PRICE Approved MR.pdf", "rb") as file:
                st.sidebar.download_button(
                    label="⬇️ Download PRICE Approved MR PDF",
                    data=file,
                    file_name="PRICE Approved MR.pdf",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except FileNotFoundError:
            st.sidebar.error("PRICE Approved MR file not found")
        except Exception as e:
            st.sidebar.error(f"Error downloading PRICE Approved MR: {str(e)}")
    if 'show_gwd_options' not in st.session_state:
        st.session_state.show_gwd_options = False
    if 'show_costindex_options' not in st.session_state:
        st.session_state.show_costindex_options = False
    
    # Add Cost Index 2021 download button
    # Cost Index 2021 button
    if st.sidebar.button("Cost Index 2021"):
        toggle_section('show_costindex_options')
        st.rerun()
    
    if st.session_state.get('show_costindex_options', False):
        try:
            with open("Cost Index 2021.pdf", "rb") as file:
                st.sidebar.download_button(
                    label="⬇️ Download Cost Index 2021 PDF",
                    data=file,
                    file_name="Cost Index 2021.pdf",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except FileNotFoundError:
            st.sidebar.error("Cost Index 2021 file not found")
        except Exception as e:
            st.sidebar.error(f"Error downloading Cost Index 2021: {str(e)}")
    if 'show_gwd_options' not in st.session_state:
        st.session_state.show_gwd_options = False
        
    # Add GWD Data download button - similar to DSR download
    # GWD Data button
    if st.sidebar.button("Download GWD Data"):
        toggle_section('show_gwd_options')
        st.rerun()

    if st.session_state.get('show_gwd_options', False):
        try:
            # List files in the GWD Data directory
            import os
            gwd_files = []
            gwd_dir = "GWD Data"
            
            if os.path.exists(gwd_dir) and os.path.isdir(gwd_dir):
                gwd_files = [f for f in os.listdir(gwd_dir) if os.path.isfile(os.path.join(gwd_dir, f))]
            
            if not gwd_files:
                st.sidebar.warning("No files found in GWD Data directory")
            else:
                # Sort files alphabetically
                gwd_files.sort()
                
                # Create dropdown to select file
                selected_file = st.sidebar.selectbox(
                    "Select GWD Data File",
                    gwd_files,
                    key="gwd_file_select"
                )
                
                # Create download button for selected file
                file_path = os.path.join(gwd_dir, selected_file)
                
                # Determine MIME type based on file extension
                file_ext = os.path.splitext(selected_file)[1].lower()
                mime_types = {
                    '.pdf': 'application/pdf',
                    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    '.xls': 'application/vnd.ms-excel',
                    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    '.doc': 'application/msword',
                    '.txt': 'text/plain',
                    '.csv': 'text/csv'
                }
                mime_type = mime_types.get(file_ext, 'application/octet-stream')
                
                with open(file_path, "rb") as file:
                    st.sidebar.download_button(
                        label=f"⬇️ Download {selected_file}",
                        data=file,
                        file_name=selected_file,
                        mime=mime_type
                    )
                    
        except Exception as e:
            st.sidebar.error(f"Error accessing GWD Data: {str(e)}")    
    # Add to your session state initialization (if not already present)
    if 'show_pump_selector' not in st.session_state:
        st.session_state.show_pump_selector = False
    
    # In your sidebar section:
    # Pump Selector button
    if st.sidebar.button("Pump Selector"):
        toggle_section('show_pump_selector')
        st.rerun()
    
    if st.session_state.show_pump_selector:
        # In your Pump Selector section, change the button HTML to:
        st.sidebar.markdown("""
        <div style="background-color:#f0f2f6; padding:10px; border-radius:5px; margin-top:10px;">
            <p style="margin-bottom:10px;">Pump Selector will open in a new tab</p>
            <a href="https://gwdpumpdesign.streamlit.app/" target="_blank" class="pump-selector-btn" style="text-decoration:none;">
                <button style="background-color:#4CAF50; color:white; border:none; padding:8px 16px; 
                            text-align:center; display:inline-block; font-size:14px; margin:4px 2px; 
                            cursor:pointer; border-radius:4px;">
                    Open Pump Selector
                </button>
            </a>
            <p style="font-size:12px; color:#666; margin-top:10px;">
                If blocked, right-click → "Open in new tab"
            </p>
        </div>
        """, unsafe_allow_html=True)
    # Add logout button if authenticated  
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.logged_in_username = None
        st.rerun()        