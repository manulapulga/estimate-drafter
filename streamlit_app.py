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

# Initialize session state
if 'selected_items' not in st.session_state:
    st.session_state.selected_items = []
if 'item_count' not in st.session_state:
    st.session_state.item_count = 0
if 'adding_subheading' not in st.session_state:
    st.session_state.adding_subheading = False

# Functions
def add_item():
    st.session_state.item_count += 1

def remove_item(index):
    st.session_state.selected_items.pop(index)

def calculate_totals():
    total_cost = sum(item['Cost'] for item in st.session_state.selected_items if item.get('Type') != 'Subheading')
    gst = round(total_cost * 0.18, 2)
    unforeseen = round(total_cost * 0.05, 2)
    final_total = math.ceil((total_cost + gst + unforeseen) / 1000) * 1000
    return total_cost, gst, unforeseen, final_total

# Display added items and subheadings
for idx, item in enumerate(st.session_state.selected_items):
    if item.get('Type') == 'Subheading':
        st.markdown(f"### 📌 {item['Item']}")
        if st.button(f"❌ Remove Subheading {idx + 1}", key=f"remove_sub_{idx}"):
            remove_item(idx)
            st.rerun()
        continue

    with st.expander(f"Item {idx + 1}: {item['Item']}"):
        col1, col2 = st.columns([3, 1])
        with col1:
            item_name = st.selectbox("Select Item", [''] + item_names, index=item_names.index(item['Item']) + 1 if item['Item'] in item_names else 0, key=f"edit_item_{idx}")
            st.text(f"Item Description: {item_name}" if item_name else "")
        with col2:
            quantity = st.text_input("Quantity", str(item['Quantity']), key=f"edit_qty_{idx}", placeholder="Input Quantity")
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

# Add New Item or Subheading
colA, colB = st.columns([1, 1])
with colA:
    st.button("➕ Add Item", on_click=add_item)
with colB:
    if st.button("➕ Add Sub Heading"):
        st.session_state.adding_subheading = True

# Subheading input form
if st.session_state.adding_subheading:
    subheading = st.text_input("Enter Sub Heading", key="new_subheading")
    if st.button("Add Sub Heading to Estimate"):
        if subheading.strip():
            st.session_state.selected_items.append({
                'Item': subheading.strip(),
                'Type': 'Subheading'
            })
            st.success("Subheading added!")
            st.session_state.adding_subheading = False
            st.rerun()
        else:
            st.warning("Please enter a valid subheading.")

# New item input form
if st.session_state.item_count > len([i for i in st.session_state.selected_items if i.get("Type") != "Subheading"]):
    idx = len([i for i in st.session_state.selected_items if i.get("Type") != "Subheading"])
    with st.expander(f"New Item {idx + 1}", expanded=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            item_name = st.selectbox("Select Item", [''] + item_names, key=f"new_item_{idx}")
            st.text(f"Item Description: {item_name}" if item_name else "")
        with col2:
            quantity = st.text_input("Quantity", "", key=f"new_qty_{idx}", placeholder="Input Quantity")
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

# Totals and file generation
if any(i.get("Type") != "Subheading" for i in st.session_state.selected_items):
    total_cost, gst, unforeseen, final_total = calculate_totals()
    st.subheader("Estimate Breakdown")
    st.write(f"Subtotal: {total_cost:.2f}")
    st.write(f"GST (18%): {gst:.2f}")
    st.write(f"Unforeseen (5%): {unforeseen:.2f}")
    st.write(f"Final Total (Rounded): {final_total:.2f}")

    if st.button("Generate Excel"):
        wb = Workbook()
        ws = wb.active
        ws.title = "Estimate"
        ws.merge_cells('A1:F1')
        ws['A1'] = estimate_heading
        ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
        ws['A1'].font = ws['A1'].font.copy(bold=True, size=14)
        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'),
                             top=Side(style='thin'), bottom=Side(style='thin'))

        row_num = 2
        serial = 1
        for item in st.session_state.selected_items:
            if item.get("Type") == "Subheading":
                ws.merge_cells(f'A{row_num}:F{row_num}')
                ws[f'A{row_num}'] = f"📌 {item['Item']}"
                row_num += 1
            else:
                ws.append([serial, item['Item'], item['Unit Price'], item['Item Unit'], item['Quantity'], item['Cost']])
                serial += 1
                row_num += 1

        for label, val in [("Subtotal", total_cost), ("GST (18%)", gst), ("Unforeseen (5%)", unforeseen), ("Grand Total", final_total)]:
            ws.merge_cells(f'A{row_num}:E{row_num}')
            ws[f'A{row_num}'] = label
            ws[f'F{row_num}'] = val
            row_num += 1

        for row in ws.iter_rows(min_row=1, max_row=row_num, min_col=1, max_col=6):
            for cell in row:
                cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
                cell.border = thin_border

        ws.column_dimensions['B'].width = 70
        excel_file = "estimate.xlsx"
        wb.save(excel_file)

        with open(excel_file, "rb") as f:
            st.download_button("Download Excel", f, file_name=excel_file, mime="application/vnd.ms-excel")
            
    if st.button("Generate PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, estimate_heading, ln=True, align='C')

        pdf.set_font("Arial", "B", 12)
        pdf.cell(10, 10, "Sl", 1, 0, 'C')
        pdf.cell(80, 10, "Item", 1, 0, 'C')
        pdf.cell(25, 10, "Rate", 1, 0, 'C')
        pdf.cell(20, 10, "Unit", 1, 0, 'C')
        pdf.cell(25, 10, "Qty", 1, 0, 'C')
        pdf.cell(30, 10, "Cost", 1, 1, 'C')

        pdf.set_font("Arial", "", 11)
        serial = 1
        for item in st.session_state.selected_items:
            if item.get("Type") == "Subheading":
                pdf.set_font("Arial", "B", 11)
                pdf.cell(190, 10, f"📌 {item['Item']}", 1, 1, 'L')
                pdf.set_font("Arial", "", 11)
            else:
                pdf.cell(10, 10, str(serial), 1, 0, 'C')
                pdf.cell(80, 10, item['Item'], 1, 0)
                pdf.cell(25, 10, f"{item['Unit Price']:.2f}", 1, 0, 'R')
                pdf.cell(20, 10, item['Item Unit'], 1, 0, 'C')
                pdf.cell(25, 10, str(item['Quantity']), 1, 0, 'R')
                pdf.cell(30, 10, f"{item['Cost']:.2f}", 1, 1, 'R')
                serial += 1

        # Totals
        pdf.set_font("Arial", "B", 11)
        for label, val in [("Subtotal", total_cost), ("GST (18%)", gst), ("Unforeseen (5%)", unforeseen), ("Grand Total", final_total)]:
            pdf.cell(160, 10, label, 1, 0, 'R')
            pdf.cell(30, 10, f"{val:.2f}", 1, 1, 'R')

        pdf_output = "estimate.pdf"
        pdf.output(pdf_output)

        with open(pdf_output, "rb") as f:
            st.download_button("Download PDF", f, file_name=pdf_output, mime="application/pdf")
else:
    st.info("No items added to the estimate yet.")
