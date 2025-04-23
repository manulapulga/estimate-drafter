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

selected_items = []
total_cost = 0
max_items = 50

for i in range(max_items):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        item_name = st.selectbox("", [''] + item_names, key=f"item_{i}")
        
        if item_name:
            st.text(f"Item Description: {item_name}")
        else:
            st.text("")  # Empty space when no item selected
    
    with col2:
        quantity = st.text_input("", "", key=f"qty_{i}", placeholder="Input Quantity")
        
        if item_name != '':
            item_data = data[data['Item Name'] == item_name].iloc[0]
            unit_price = item_data['Unit Price']
            unit = item_data['Item Unit']
            
            # Display unit price with unit below quantity field
            st.text(f"Rate: {unit_price:.2f}/{unit}")
            
            if quantity:
                try:
                    qty = float(quantity)
                    if qty > 0:
                        total = qty * unit_price
                        # Display total amount below unit price
                        st.text(f"Amount: {total:.2f}")
                except ValueError:
                    st.text("Invalid quantity")
            else:
                st.text("")  # Empty space when no quantity
        else:
            st.text("")  # Empty space when no item selected
    
    if item_name != '' and quantity:
        try:
            quantity = float(quantity)
            if quantity > 0:
                item_data = data[data['Item Name'] == item_name].iloc[0]
                unit_price = item_data['Unit Price']
                unit = item_data['Item Unit']
                cost = round(quantity * unit_price, 2)
                total_cost += cost
                selected_items.append({
                    'Item': item_name,
                    'Quantity': quantity,
                    'Unit Price': unit_price,
                    'Item Unit': unit,
                    'Cost': cost
                })
        except ValueError:
            pass

    if len(selected_items) >= max_items:
        break

# Calculate totals
gst = round(total_cost * 0.18, 2)
unforeseen = round(total_cost * 0.05, 2)
final_total = math.ceil((total_cost + gst + unforeseen) / 1000) * 1000

# Display the key amounts
st.subheader("Estimate Breakdown")
st.write(f"Subtotal: {total_cost:.2f}")
st.write(f"GST (18%): {gst:.2f}")
st.write(f"Unforeseen (5%): {unforeseen:.2f}")
st.write(f"Final Total (Rounded): {final_total:.2f}")

# Excel Generation (unchanged)
if st.button("Generate Excel"):
    items_data = []
    for idx, item in enumerate(selected_items, start=1):
        items_data.append([idx, item['Item'], item['Unit Price'], item['Item Unit'], item['Quantity'], item['Cost']])

    items_data.append(["Subtotal", "", "", "", "", total_cost])
    items_data.append(["GST (18%)", "", "", "", "", gst])
    items_data.append(["Unforeseen (5%)", "", "", "", "", unforeseen])
    items_data.append(["Grand Total", "", "", "", "", final_total])

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
    
    thin_border = Border(left=Side(style='thin'),
                         right=Side(style='thin'),
                         top=Side(style='thin'),
                         bottom=Side(style='thin'))
    
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
        st.download_button(
            label="Download Excel",
            data=f,
            file_name=excel_file,
            mime="application/vnd.ms-excel"
        )

# PDF Generation (unchanged)
if st.button("Generate PDF"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font("Arial", style='I', size=60)
    pdf.set_text_color(200, 200, 200)
    pdf.rotate(45, 60, 60)
    pdf.text(30, 120, "Kerala Ground Water Department")
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
        max_lines = 1
        for i, text in enumerate(row_data):
            lines = split_text(str(text), col_widths[i])
            if len(lines) > max_lines:
                max_lines = len(lines)
        return max_lines
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    headers = ["Sl.No", "Item Name", "Rate", "Unit", "Qty", "Total"]
    
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
    
    for idx, item in enumerate(selected_items, start=1):
        pdf.set_font("Arial", '', 10)
        row_data = [
            str(idx),
            item['Item'],
            f"{item['Unit Price']:.2f}",
            item['Item Unit'],
            f"{item['Quantity']:.2f}",
            f"{item['Cost']:.2f}"
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
            label="Download PDF",
            data=f,
            file_name=pdf_file,
            mime="application/pdf"
        )
