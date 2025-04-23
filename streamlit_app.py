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

# Function to add a new item
def add_item():
    st.session_state.item_count += 1

# Function to remove an item
def remove_item(index):
    st.session_state.selected_items.pop(index)
    calculate_totals()

# Function to calculate totals
def calculate_totals():
    total_cost = 0
    for item in st.session_state.selected_items:
        total_cost += item['Cost']

    gst = round(total_cost * 0.18, 2)
    unforeseen = round(total_cost * 0.05, 2)
    final_total = math.ceil((total_cost + gst + unforeseen) / 1000) * 1000

    return total_cost, gst, unforeseen, final_total

# Display existing items and allow editing/removal
for idx, item in enumerate(st.session_state.selected_items):
    with st.expander(f"Item {idx + 1}: {item['Item']}"):
        col1, col2 = st.columns([3, 1])

        with col1:
            item_name = st.selectbox(
                "Select Item", 
                [''] + item_names,
                index=item_names.index(item['Item']) + 1 if item['Item'] in item_names else 0,
                key=f"edit_item_{idx}"
            )
            st.text(f"Item Description: {item_name}") if item_name else st.text("")

        with col2:
            quantity = st.text_input(
                "Quantity", 
                str(item['Quantity']), 
                key=f"edit_qty_{idx}", 
                placeholder="Input Quantity"
            )
            if item_name:
                item_data = data[data['Item Name'] == item_name].iloc[0]
                unit_price = item_data['Unit Price']
                unit = item_data['Item Unit']
                st.text(f"Rate: {unit_price:.2f}/{unit}")
                try:
                    qty = float(quantity)
                    if qty > 0:
                        total = qty * unit_price
                        st.text(f"Amount: {total:.2f}")
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

# Show Add Item button just after the last item block
if len(st.session_state.selected_items) > 0:
    st.markdown("---")
    st.button("➕ Add Item", on_click=add_item)

# Add new item fields when "Add Item" is clicked
if st.session_state.item_count > len(st.session_state.selected_items):
    idx = len(st.session_state.selected_items)
    with st.expander(f"New Item {idx + 1}", expanded=True):
        col1, col2 = st.columns([3, 1])

        with col1:
            item_name = st.selectbox("Select Item", [''] + item_names, key=f"new_item_{idx}")
            st.text(f"Item Description: {item_name}") if item_name else st.text("")

        with col2:
            quantity = st.text_input("Quantity", "", key=f"new_qty_{idx}", placeholder="Input Quantity")
            if item_name:
                item_data = data[data['Item Name'] == item_name].iloc[0]
                unit_price = item_data['Unit Price']
                unit = item_data['Item Unit']
                st.text(f"Rate: {unit_price:.2f}/{unit}")
                try:
                    qty = float(quantity)
                    if qty > 0:
                        total = qty * unit_price
                        st.text(f"Amount: {total:.2f}")
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

# Calculate and display totals
if st.session_state.selected_items:
    total_cost, gst, unforeseen, final_total = calculate_totals()

    st.subheader("Estimate Breakdown")
    st.write(f"Subtotal: {total_cost:.2f}")
    st.write(f"GST (18%): {gst:.2f}")
    st.write(f"Unforeseen (5%): {unforeseen:.2f}")
    st.write(f"Final Total (Rounded): {final_total:.2f}")

    if st.button("Generate Excel"):
        items_data = [[idx, item['Item'], item['Unit Price'], item['Item Unit'], item['Quantity'], item['Cost']] for idx, item in enumerate(st.session_state.selected_items, start=1)]
        items_data += [["Subtotal", "", "", "", "", total_cost],
                       ["GST (18%)", "", "", "", "", gst],
                       ["Unforeseen (5%)", "", "", "", "", unforeseen],
                       ["Grand Total", "", "", "", "", final_total]]
        df = pd.DataFrame(items_data, columns=["S.No", "Item Name", "Item Rate", "Item Unit", "Quantity", "Total"])
        wb = Workbook()
        ws = wb.active
        ws.title = "Estimate"
        ws.merge_cells('A1:F1')
        ws['A1'] = estimate_heading
        ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
        ws['A1'].font = ws['A1'].font.copy(bold=True, size=14)
        for row_idx, row in df.iterrows():
            for col_idx, value in enumerate(row):
                cell = ws.cell(row=row_idx+2, column=col_idx+1, value=value)
                cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
            for cell in row:
                cell.border = thin_border
        for row_idx in range(len(items_data)-4, len(items_data)):
            ws.merge_cells(f'A{row_idx+2}:E{row_idx+2}')
            ws[f'A{row_idx+2}'] = items_data[row_idx][0]
            ws[f'A{row_idx+2}'].alignment = Alignment(horizontal='center', vertical='center')
        ws.column_dimensions['B'].width = 70
        excel_file = "estimate.xlsx"
        wb.save(excel_file)
        with open(excel_file, "rb") as f:
            st.download_button("Download Excel", f, file_name=excel_file, mime="application/vnd.ms-excel")

    if st.button("Generate PDF"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", style='B', size=72)
        pdf.set_text_color(230, 230, 230)
        text = "KERALA GROUND WATER DEPARTMENT"
        text_width = pdf.get_string_width(text)
        x = (pdf.w - text_width) / 2
        y = pdf.h / 2 - 20
        pdf.rotate(45, pdf.w/2, pdf.h/2)
        pdf.text(x, y, text)
        pdf.rotate(0)
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(200, 10, txt=estimate_heading, ln=True, align='C')
        col_widths = [10, 70, 20, 20, 20, 20]

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
            return max(len(split_text(str(text), col_widths[i])) for i, text in enumerate(row_data))

        pdf.ln(10)
        pdf.set_font("Arial", 'B', 10)
        headers = ["Sl.No", "Item Name", "Rate", "Unit", "Qty", "Total"]
        x_start = pdf.get_x()
        y_start = pdf.get_y()
        pdf.rect(x_start, y_start, sum(col_widths), 6)
        for i in range(1, len(col_widths)):
            pdf.line(x_start + sum(col_widths[:i]), y_start, x_start + sum(col_widths[:i]), y_start + 6)
        for i, header in enumerate(headers):
            pdf.set_xy(x_start + sum(col_widths[:i]), y_start)
            pdf.cell(col_widths[i], 6, header, 0, 0, 'C')
        pdf.set_y(y_start + 6)

        for idx, item in enumerate(st.session_state.selected_items, start=1):
            pdf.set_font("Arial", '', 10)
            row_data = [str(idx), item['Item'], f"{item['Unit Price']:.2f}", item['Item Unit'], f"{item['Quantity']:.2f}", f"{item['Cost']:.2f}"]
            x_row_start = pdf.get_x()
            y_row_start = pdf.get_y()
            max_lines = calculate_max_lines(row_data)
            row_height = 6 * max_lines
            for i, text in enumerate(row_data):
                pdf.set_xy(x_row_start + sum(col_widths[:i]), y_row_start)
                pdf.cell(col_widths[i], row_height, border=1)
                pdf.set_xy(x_row_start + sum(col_widths[:i]), y_row_start)
                for line in split_text(text, col_widths[i]):
                    pdf.cell(col_widths[i], 6, line, 0, 0, 'C')
                    pdf.set_xy(x_row_start + sum(col_widths[:i]), pdf.get_y() + 6)
            pdf.set_y(y_row_start + row_height)

        summary_data = [("Subtotal", f"{total_cost:.2f}"), ("GST (18%)", f"{gst:.2f}"), ("Unforeseen (5%)", f"{unforeseen:.2f}"), ("Grand Total", f"{final_total:.2f}")]
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
            st.download_button("Download PDF", f, file_name=pdf_file, mime="application/pdf")
else:
    st.info("No items added to the estimate yet. Click 'Add Item' to get started.")
    st.button("➕ Add Item", on_click=add_item)
