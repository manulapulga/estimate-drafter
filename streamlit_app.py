import pandas as pd
import streamlit as st
from fpdf import FPDF
import math
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Side
from item_wizard import show_item_wizard

# Set page config
st.set_page_config(layout="wide")

# Load user credentials from Sheet 2 of Excel
@st.cache_data
def load_credentials(file_path):
    return pd.read_excel(file_path, sheet_name=1)  # Sheet 2 is index 1

# Authentication function
def authenticate(username, password, credentials_df):
    user_row = credentials_df[credentials_df['username'] == username]
    if not user_row.empty:
        return user_row.iloc[0]['password'] == password
    return False

# Load data
try:
    credentials_df = load_credentials("items.xlsx")
    data = pd.read_excel("items.xlsx", sheet_name=0)  # Sheet 1 is index 0
    item_names = data['Item Name'].tolist()
    unit_prices = data['Unit Price'].tolist()
    item_units = data['Item Unit'].tolist()
except FileNotFoundError:
    st.error("Database file not found. Please contact administrator.")
    st.stop()
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Login screen
def login_page():
    st.markdown("<h1 style='text-align: center; color: #154c79;'>ESTIMATE DRAFTER LOGIN</h1>", unsafe_allow_html=True)
    
    username_input = st.text_input("Username", key="username_input")
    password_input = st.text_input("Password", type="password", key="password_input")
    
    if st.button("Login"):
        if authenticate(username_input, password_input, credentials_df):
            st.session_state.logged_in_username = username_input
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid username or password")

# Main app
def main_app():
    # UI for Estimate Drafting with updated styles
    st.markdown("<h1 style='text-align: center; color: #154c79;'>ESTIMATE DRAFTER</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: right; color: #666;'>Logged in as: {st.session_state.logged_in_username}</p>", unsafe_allow_html=True)
    
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
            if item.get('Type') not in ['Subheading', 'Other'] or 
               (item.get('Type') == 'Other' and item.get('GST_Applicable', True))
        )
        gst = round(taxable_amount * 0.18, 2)
        
        unforeseen = round(total_cost * 0.05, 2)
        final_total = math.ceil((total_cost + gst + unforeseen) / 1000) * 1000
        return total_cost, gst, unforeseen, final_total

    def handle_item_selection(selected_item):
        item_data = data[data['Item Name'] == selected_item].iloc[0]
        st.session_state.selected_items.append({
            'Item': selected_item,
            'Quantity': 1.0,
            'Unit Price': item_data['Unit Price'],
            'Item Unit': item_data['Item Unit'],
            'Cost': item_data['Unit Price'],
            'Type': 'Standard',
            'GST_Applicable': True
        })
        st.session_state.show_wizard = False
        st.success(f"Item '{selected_item}' added successfully!")
        st.rerun()

    # Display added items and subheadings
    for idx, item in enumerate(st.session_state.selected_items):
        if item.get('Type') == 'Subheading':
            with st.expander(f"📌 {item['Item']}", expanded=False):
                st.markdown(f"**{item['Item']}**")
                if st.button(f"❌ Remove Subheading", key=f"remove_sub_{idx}"):
                    remove_item(idx)
            continue

        item_type = item.get('Type', 'Standard')
        item_title = f"📦 Item {idx + 1}: {item['Item']} (₹{item['Cost']:.2f})"
        if item_type == 'Other':
            item_title += " [Other" + (" +GST" if item.get('GST_Applicable', False) else "") + "]"
        
        with st.expander(item_title, expanded=False):
            if item_type == 'Other':
                # Display for "Other" type items
                st.markdown(f"**Custom Item:** {item['Item']}")
                st.markdown(f"**Total Price:** ₹{item['Cost']:.2f}")
                st.markdown(f"**GST Applicable:** {'Yes' if item.get('GST_Applicable', False) else 'No'}")
                
                if st.button(f"❌ Remove", key=f"remove_{idx}"):
                    remove_item(idx)
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

                # Action buttons inside expander
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"🔄 Update", key=f"update_{idx}"):
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
                                        'GST_Applicable': True
                                    }
                                    st.success("Item updated successfully!")
                                    st.rerun()
                            except ValueError:
                                st.error("Please enter a valid quantity")
                with col2:
                    if st.button(f"❌ Remove", key=f"remove_{idx}"):
                        remove_item(idx)

    # Add New Item or Subheading buttons
    button_col1, button_col2, button_col3, button_col4 = st.columns([1, 2, 1, 1])
    with button_col1:
        if st.button("➕ Add Item", key="add_item_btn"):
            # Toggle add item section and hide others
            st.session_state.show_add_item = not st.session_state.get('show_add_item', False)
            st.session_state.show_wizard = False
            st.session_state.adding_subheading = False
            st.session_state.show_add_other = False
            st.rerun()
    with button_col2:
        if st.button("🔍 Item Selection Wizard", key="open_wizard"):
            # Toggle wizard and hide others
            st.session_state.show_wizard = not st.session_state.get('show_wizard', False)
            st.session_state.show_add_item = False
            st.session_state.adding_subheading = False
            st.session_state.show_add_other = False
            st.rerun()
    with button_col3:
        if st.button("➕ Add Heading", key="add_subheading_btn"):
            # Toggle subheading and hide others
            st.session_state.adding_subheading = not st.session_state.get('adding_subheading', False)
            st.session_state.show_add_item = False
            st.session_state.show_wizard = False
            st.session_state.show_add_other = False
            st.rerun()
    with button_col4:
        if st.button("➕ Add Other", key="add_other_btn", type="secondary", 
                    help="Add custom items not in database"):
            # Toggle other items section and hide others
            st.session_state.show_add_other = not st.session_state.get('show_add_other', False)
            st.session_state.show_add_item = False
            st.session_state.show_wizard = False
            st.session_state.adding_subheading = False
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
                                    'GST_Applicable': True
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

    # Show Item Selection Wizard if toggled on
    if st.session_state.get('show_wizard', False):
        show_item_wizard(data, handle_item_selection)
        if st.button("✕ Close Wizard", key="close_wizard", type="primary"):
            st.session_state.show_wizard = False
            st.rerun()

    # Show Subheading section if toggled on
    if st.session_state.get('adding_subheading', False):
        subheading = st.text_input("Enter Sub Heading", key="new_subheading")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Add Sub Heading to Estimate", key="confirm_subheading"):
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
                        ws.append([
                            serial,
                            item['Item'],
                            "-",
                            "-",
                            "-",
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
                            item['Quantity'],
                            item['Cost'],
                            "Yes"
                        ])
                        serial += 1
                        row_num += 1

                # Add totals
                for label, val in [
                    ("Subtotal", total_cost),
                    ("GST (18%)", gst),
                    ("Unforeseen (5%)", unforeseen),
                    ("Grand Total", final_total)
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
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()

                # Watermark
                pdf.set_font("Arial", style='B', size=72)
                pdf.set_text_color(230, 230, 230)
                text = "KERALA GROUND WATER DEPARTMENT"
                text_width = pdf.get_string_width(text)
                x = (pdf.w - text_width) / 2
                y = pdf.h / 2 - 20
                pdf.rotate(45, pdf.w/2, pdf.h/2)
                pdf.text(x, y, text)
                pdf.rotate(0)

                # Main content
                pdf.set_font("Arial", 'B', 16)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(200, 10, txt=estimate_heading, ln=True, align='C')
                
                col_widths = [10, 60, 20, 20, 20, 20, 20]

                def split_text(text, max_width):
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
                    max_lines = 1
                    for i, text in enumerate(row_data):
                        lines = split_text(str(text), col_widths[i])
                        if len(lines) > max_lines:
                            max_lines = len(lines)
                    return max_lines

                pdf.ln(10)
                pdf.set_font("Arial", 'B', 10)
                headers = ["Sl.No", "Item Name", "Rate", "Unit", "Qty", "Total", "GST"]

                x_start = pdf.get_x()
                y_start = pdf.get_y()

                pdf.rect(x_start, y_start, sum(col_widths), 6)

                for i in range(1, len(col_widths)):
                    pdf.line(
                        x_start + sum(col_widths[:i]), y_start,
                        x_start + sum(col_widths[:i]), y_start + 6
                    )

                for i, header in enumerate(headers):
                    pdf.set_xy(x_start + sum(col_widths[:i]), y_start)
                    pdf.cell(col_widths[i], 6, header, 0, 0, 'C')

                pdf.set_y(y_start + 6)

                serial = 1 
                for item in st.session_state.selected_items:
                    pdf.set_font("Arial", '', 10)
                
                    if item.get("Type") == "Subheading":
                        pdf.set_xy(x_start, pdf.get_y())
                        pdf.cell(sum(col_widths), 6, f" {item['Item']}", border=1, align='C')
                        pdf.ln(6)
                    elif item.get("Type") == "Other":
                        row_data = [
                            str(serial),
                            item['Item'],
                            "-",
                            "-",
                            "-",
                            f"{item['Cost']:.2f}",
                            "Yes" if item.get('GST_Applicable', False) else "No"
                        ]
                    
                        x_row_start = pdf.get_x()
                        y_row_start = pdf.get_y()
                    
                        max_lines = calculate_max_lines(row_data)
                        row_height = 6 * max_lines
                    
                        for i, text in enumerate(row_data):
                            pdf.set_xy(x_row_start + sum(col_widths[:i]), y_row_start)
                        
                            cell_lines = split_text(str(text), col_widths[i])
                        
                            vertical_offset = (row_height - (6 * len(cell_lines))) / 2
                        
                            pdf.cell(col_widths[i], row_height, border=1)
                        
                            pdf.set_xy(x_row_start + sum(col_widths[:i]), y_row_start + vertical_offset)
                        
                            for line in cell_lines:
                                pdf.cell(col_widths[i], 6, line, 0, 0, 'C')
                                pdf.set_xy(x_row_start + sum(col_widths[:i]), pdf.get_y() + 6)
                    
                        pdf.set_y(y_row_start + row_height)
                        serial += 1
                    else:
                        row_data = [
                            str(serial),
                            item['Item'],
                            f"{item['Unit Price']:.2f}",
                            item['Item Unit'],
                            f"{item['Quantity']:.2f}",
                            f"{item['Cost']:.2f}",
                            "Yes"
                        ]
                    
                        x_row_start = pdf.get_x()
                        y_row_start = pdf.get_y()
                    
                        max_lines = calculate_max_lines(row_data)
                        row_height = 6 * max_lines
                    
                        for i, text in enumerate(row_data):
                            pdf.set_xy(x_row_start + sum(col_widths[:i]), y_row_start)
                        
                            cell_lines = split_text(str(text), col_widths[i])
                        
                            vertical_offset = (row_height - (6 * len(cell_lines))) / 2
                        
                            pdf.cell(col_widths[i], row_height, border=1)
                        
                            pdf.set_xy(x_row_start + sum(col_widths[:i]), y_row_start + vertical_offset)
                        
                            for line in cell_lines:
                                pdf.cell(col_widths[i], 6, line, 0, 0, 'C')
                                pdf.set_xy(x_row_start + sum(col_widths[:i]), pdf.get_y() + 6)
                    
                        pdf.set_y(y_row_start + row_height)
                        serial += 1

                summary_data = [
                    ("Subtotal", f"{total_cost:.2f}"),
                    ("GST (18%)", f"{gst:.2f}"),
                    ("Unforeseen (5%)", f"{unforeseen:.2f}"),
                    ("Grand Total", f"{final_total:.2f}")
                ]
            
                for label, value in summary_data:
                    x = pdf.get_x()
                    y = pdf.get_y()
                
                    pdf.multi_cell(sum(col_widths[:-1]), 8, label, border=1, align='C')
                    pdf.set_xy(x + sum(col_widths[:-1]), y)
                
                    pdf.multi_cell(col_widths[-1], 8, value, border=1, align='C')
                
                    pdf.set_xy(x, y + 8)
            
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

if st.session_state.authenticated:
    main_app()
else:
    login_page()
    
# Add logout button if authenticated
if st.session_state.get('authenticated', False):
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.logged_in_username = None
        st.rerun()
