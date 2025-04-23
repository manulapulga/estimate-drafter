import pandas as pd
import streamlit as st
from fpdf import FPDF
import math
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Side

# Load Excel Data
@st.cache_data
def load_data(file_path):
    return pd.read_excel(file_path)

data = load_data("items.xlsx")
item_names = data['Item Name'].tolist()
unit_prices = data['Unit Price'].tolist()
item_units = data['Item Unit'].tolist()

# UI for Estimate Drafting
st.title("ESTIMATE DRAFTER", anchor="center")
estimate_heading = st.text_input("Work Description")
st.markdown("<h3 style='text-align: center;'>ADD ITEMS TO ESTIMATE</h3>", unsafe_allow_html=True)

# Initialize session state for items if not exists
if 'selected_items' not in st.session_state:
    st.session_state.selected_items = []
if 'item_count' not in st.session_state:
    st.session_state.item_count = 0
if 'subheading_count' not in st.session_state:
    st.session_state.subheading_count = 0

# Function to add a new item
def add_item():
    st.session_state.item_count += 1

# Function to add a new subheading
def add_subheading():
    st.session_state.subheading_count += 1

# Function to remove an item
def remove_item(index):
    st.session_state.selected_items.pop(index)
    calculate_totals()

# Function to calculate totals
def calculate_totals():
    total_cost = 0
    for item in st.session_state.selected_items:
        if 'Cost' in item:
            total_cost += item['Cost']

    gst = round(total_cost * 0.18, 2)
    unforeseen = round(total_cost * 0.05, 2)
    final_total = math.ceil((total_cost + gst + unforeseen) / 1000) * 1000

    return total_cost, gst, unforeseen, final_total

# Display existing items/subheadings and allow editing/removal
for idx, item in enumerate(st.session_state.selected_items):
    if item.get('type') == 'subheading':
        with st.expander(f"📌 {item['text']}", expanded=True):
            new_text = st.text_input("Subheading Text", value=item['text'], key=f"edit_subheading_{idx}")
            if st.button(f"Update Subheading", key=f"update_subheading_{idx}"):
                st.session_state.selected_items[idx]['text'] = new_text
                st.success("Subheading updated successfully!")
            if st.button(f"❌ Remove Subheading", key=f"remove_subheading_{idx}"):
                remove_item(idx)
                st.rerun()
    else:
        with st.expander(f"Item {idx + 1}: {item['Item']}"):
            col1, col2 = st.columns([3, 1])
            with col1:
                item_name = st.selectbox("Select Item", [''] + item_names, index=item_names.index(item['Item']) + 1 if item['Item'] in item_names else 0, key=f"edit_item_{idx}")
                st.text(f"Item Description: {item_name}" if item_name else "")
            with col2:
                quantity = st.text_input("Quantity", str(item['Quantity']), key=f"edit_qty_{idx}", placeholder="Input Quantity")
                if item_name:
                    item_data = data[data['Item Name'] == item_name].iloc[0]
                    unit_price = item_data['Unit Price']
                    unit = item_data['Item Unit']
                    st.text(f"Rate: {unit_price:.2f}/{unit}")
                    if quantity:
                        try:
                            qty = float(quantity)
                            if qty > 0:
                                st.text(f"Amount: {qty * unit_price:.2f}")
                        except ValueError:
                            st.text("Invalid quantity")
            if st.button(f"Update Item {idx + 1}", key=f"update_{idx}"):
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
                                'Cost': cost
                            }
                            st.success("Item updated successfully!")
                    except ValueError:
                        st.error("Please enter a valid quantity")
            if st.button(f"❌ Remove Item {idx + 1}", key=f"remove_{idx}"):
                remove_item(idx)
                st.rerun()

# Add new item fields when "Add Item" is clicked
if st.session_state.item_count > sum(1 for item in st.session_state.selected_items if 'Item' in item):
    idx = len(st.session_state.selected_items)
    with st.expander(f"New Item {idx + 1}", expanded=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            item_name = st.selectbox("Select Item", [''] + item_names, key=f"new_item_{idx}")
            st.text(f"Item Description: {item_name}" if item_name else "")
        with col2:
            quantity = st.text_input("Quantity", "", key=f"new_qty_{idx}", placeholder="Input Quantity")
            if item_name:
                item_data = data[data['Item Name'] == item_name].iloc[0]
                unit_price = item_data['Unit Price']
                unit = item_data['Item Unit']
                st.text(f"Rate: {unit_price:.2f}/{unit}")
                if quantity:
                    try:
                        qty = float(quantity)
                        if qty > 0:
                            st.text(f"Amount: {qty * unit_price:.2f}")
                    except ValueError:
                        st.text("Invalid quantity")
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
                            'Cost': cost
                        })
                        st.success("Item added successfully!")
                        st.rerun()
                except ValueError:
                    st.error("Please enter a valid quantity")

# Add new subheading when "Add Subheading" is clicked
if st.session_state.subheading_count > sum(1 for item in st.session_state.selected_items if item.get('type') == 'subheading'):
    idx = len(st.session_state.selected_items)
    with st.expander("New Subheading", expanded=True):
        subheading_text = st.text_input("Subheading Text", key=f"new_subheading_{idx}", placeholder="Enter subheading text")
        if st.button("Add Subheading", key=f"add_subheading_{idx}"):
            if subheading_text:
                st.session_state.selected_items.append({'type': 'subheading', 'text': subheading_text})
                st.success("Subheading added successfully!")
                st.rerun()
            else:
                st.error("Please enter subheading text")

if len(st.session_state.selected_items) > 0 or st.session_state.item_count > 0 or st.session_state.subheading_count > 0:
    col1, col2 = st.columns(2)
    with col1:
        st.button("➕ Add Item", on_click=add_item)
    with col2:
        st.button("📌 Add Subheading", on_click=add_subheading)

if any('Cost' in item for item in st.session_state.selected_items):
    total_cost, gst, unforeseen, final_total = calculate_totals()
    st.subheader("Estimate Breakdown")
    st.write(f"Subtotal: {total_cost:.2f}")
    st.write(f"GST (18%): {gst:.2f}")
    st.write(f"Unforeseen (5%): {unforeseen:.2f}")
    st.write(f"Final Total (Rounded): {final_total:.2f}")

    if st.button("Generate PDF"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", style='B', size=72)
        pdf.set_text_color(230, 230, 230)
        watermark = "KERALA GROUND WATER DEPARTMENT"
        text_width = pdf.get_string_width(watermark)
        pdf.rotate(45, pdf.w / 2, pdf.h / 2)
        pdf.text((pdf.w - text_width) / 2, pdf.h / 2 - 20, watermark)
        pdf.rotate(0)

        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(200, 10, txt=estimate_heading, ln=True, align='C')
        pdf.ln(10)

        col_widths = [10, 70, 20, 20, 20, 20]
        headers = ["Sl.No", "Item Name", "Rate", "Unit", "Qty", "Total"]

        def split_text(text, max_width):
            if not isinstance(text, str): text = str(text)
            words, lines, line = text.split(), [], ""
            for word in words:
                if pdf.get_string_width((line + ' ' + word).strip()) < max_width - 2:
                    line = (line + ' ' + word).strip()
                else:
                    lines.append(line)
                    line = word
            lines.append(line)
            return lines

        def calculate_max_lines(row_data):
            return max(len(split_text(str(txt), col_widths[i])) for i, txt in enumerate(row_data))

        item_counter, show_header = 1, True
for item in st.session_state.selected_items:
    if item.get('type') == 'subheading':
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(sum(col_widths), 8, item['text'], 0, 1, 'L')
        pdf.ln(2)
        show_header = True
    else:
        if show_header:
            pdf.set_font("Arial", 'B', 10)
            x, y = pdf.get_x(), pdf.get_y()
            pdf.rect(x, y, sum(col_widths), 6)
            for i in range(1, len(col_widths)):
                pdf.line(x + sum(col_widths[:i]), y, x + sum(col_widths[:i]), y + 6)
            for i, h in enumerate(headers):
                pdf.set_xy(x + sum(col_widths[:i]), y)
                pdf.cell(col_widths[i], 6, h, 0, 0, 'C')
            pdf.set_y(y + 6)
            show_header = False

        pdf.set_font("Arial", '', 10)
        row_data = [
            str(item_counter),
            item['Item'],
            f"{item['Unit Price']:.2f}",
            item['Item Unit'],
            f"{item['Quantity']:.2f}",
            f"{item['Cost']:.2f}"
        ]
        item_counter += 1

        max_lines = calculate_max_lines(row_data)
        row_height = 6 * max_lines
        x, y = pdf.get_x(), pdf.get_y()

        for i, val in enumerate(row_data):
            pdf.set_xy(x + sum(col_widths[:i]), y)
            lines = split_text(val, col_widths[i])
            padded_lines = lines + [''] * (max_lines - len(lines))  # pad with blank lines if needed
            cell_text = "\n".join(padded_lines)
            pdf.multi_cell(col_widths[i], 6, cell_text, border=1, align='C')
        pdf.set_y(y + row_height)

        if item_counter > 1:
            summary_data = [("Subtotal", f"{total_cost:.2f}"), ("GST (18%)", f"{gst:.2f}"), ("Unforeseen (5%)", f"{unforeseen:.2f}"), ("Grand Total", f"{final_total:.2f}")]
            for label, val in summary_data:
                x, y = pdf.get_x(), pdf.get_y()
                pdf.multi_cell(sum(col_widths[:-1]), 8, label, border=1, align='C')
                pdf.set_xy(x + sum(col_widths[:-1]), y)
                pdf.multi_cell(col_widths[-1], 8, val, border=1, align='C')
                pdf.set_y(y + 8)

        pdf_file = "estimate.pdf"
        pdf.output(pdf_file)
        with open(pdf_file, "rb") as f:
            st.download_button("Download PDF", data=f, file_name=pdf_file, mime="application/pdf")
else:
    st.info("No items added to the estimate yet. Click 'Add Item' to get started.")
    col1, col2 = st.columns(2)
    with col1:
        st.button("➕ Add Item", on_click=add_item)
    with col2:
        st.button("📌 Add Subheading", on_click=add_subheading)
