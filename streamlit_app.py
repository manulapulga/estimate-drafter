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
item_names = data['Item Name'].tolist()  # Assuming column name is "Item Name"
unit_prices = data['Unit Price'].tolist()  # Assuming column name is "Unit Price"
item_units = data['Item Unit'].tolist()  # Assuming column name is "Item Unit"

# UI for Estimate Drafting
st.title("ESTIMATE DRAFTER", anchor="center")  # Center-align title and make it uppercase
estimate_heading = st.text_input("Work Description")  # Changed label to "Work Description"

# Center-align subheading in uppercase
st.markdown("<h3 style='text-align: center;'>ADD ITEMS TO ESTIMATE</h3>", unsafe_allow_html=True)

selected_items = []
total_cost = 0

# Limit to 50 items
max_items = 50

# Loop to allow item selection up to 50 items
for i in range(max_items):
    # Create two columns: one for item selection and one for quantity input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Selectbox for item selection
        item_name = st.selectbox("", [''] + item_names, key=f"item_{i}")
        
        # ✅ Show full item name below the dropdown
        if item_name:
            st.text(f"Full Item Name: {item_name}")  # Display full content in plain text
        
        # Show unit price if item is selected
        if item_name != '':
            unit_price = data.loc[data['Item Name'] == item_name, 'Unit Price'].values[0]
            st.text(f"Unit Price: {unit_price}")
        else:
            st.text("Unit Price: N/A")
    
    with col2:
        # Display the quantity input with no label
        quantity = st.text_input("", "", key=f"qty_{i}", placeholder="Input Quantity")
        
        # Display unit next to quantity field
        if item_name != '':
            item_unit = data.loc[data['Item Name'] == item_name, 'Item Unit'].values[0]
            st.text(f"Unit: {item_unit}")
        else:
            st.text("Unit: N/A")
    
    if item_name != '' and quantity:  # Proceed only if a valid item is selected and quantity is entered
        try:
            quantity = float(quantity)
            if quantity > 0:  # Only process if quantity is greater than 0
                unit_price = data.loc[data['Item Name'] == item_name, 'Unit Price'].values[0]
                cost = round(quantity * unit_price, 2)  # Round to two decimals
                total_cost += cost
                selected_items.append({'Item': item_name, 'Quantity': quantity, 'Unit Price': unit_price, 'Item Unit': item_units[i], 'Cost': cost})
        except ValueError:
            pass  # If the input is not a valid number, ignore it

    # Stop if 50 items are selected
    if len(selected_items) >= max_items:
        break

# Subtotal, GST, Unforeseen, and Final Total
gst = round(total_cost * 0.18, 2)
unforeseen = round(total_cost * 0.05, 2)
final_total = math.ceil((total_cost + gst + unforeseen) / 1000) * 1000

# Display the key amounts (Subtotal, GST, Unforeseen, and Final Total)
st.subheader("Estimate Breakdown")
st.write(f"Subtotal: {total_cost}")
st.write(f"GST (18%): {gst}")
st.write(f"Unforeseen (5%): {unforeseen}")
st.write(f"Final Total (Rounded): {final_total}")

# Excel Generation
if st.button("Generate Excel"):
    # Prepare Data for Excel
    items_data = []
    for idx, item in enumerate(selected_items, start=1):
        items_data.append([idx, item['Item'], item['Unit Price'], item['Item Unit'], item['Quantity'], item['Cost']])

    # Add Subtotal, GST, Unforeseen, and Grand Total
    items_data.append(["Subtotal", "", "", "", "", total_cost])
    items_data.append(["GST (18%)", "", "", "", "", gst])
    items_data.append(["Unforeseen (5%)", "", "", "", "", unforeseen])
    items_data.append(["Grand Total", "", "", "", "", final_total])

    # Create a DataFrame
    df = pd.DataFrame(items_data, columns=["S.No", "Item Name", "Item Rate", "Item Unit", "Quantity", "Total"])
    
    # Create an Excel workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Estimate"
    
    # Merging Heading
    ws.merge_cells('A1:F1')
    ws['A1'] = estimate_heading
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws['A1'].font = ws['A1'].font.copy(bold=True, size=14)

    # Write the DataFrame to Excel (excluding index)
    for row_idx, row in df.iterrows():
        for col_idx, value in enumerate(row):
            cell = ws.cell(row=row_idx+2, column=col_idx+1, value=value)
            # Set text wrap and center alignment
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    
    # Apply Borders to All Cells
    thin_border = Border(left=Side(style='thin'),
                         right=Side(style='thin'),
                         top=Side(style='thin'),
                         bottom=Side(style='thin'))
    
    # Apply border to all rows and columns
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
        for cell in row:
            cell.border = thin_border

    # Merge Cells for Subtotal, GST, Unforeseen, and Grand Total
    for row_idx in range(len(items_data)-4, len(items_data)):
        ws.merge_cells(f'A{row_idx+2}:E{row_idx+2}')
        ws[f'A{row_idx+2}'] = items_data[row_idx][0]
        ws[f'A{row_idx+2}'].alignment = Alignment(horizontal='center', vertical='center')
    
    # Set the width of "Item Name" column to 70
    ws.column_dimensions['B'].width = 70

    # Save the Excel file
    excel_file = "estimate.xlsx"
    wb.save(excel_file)

    # Provide download link for Excel file
    with open(excel_file, "rb") as f:
        st.download_button(
            label="Download Excel",
            data=f,
            file_name=excel_file,
            mime="application/vnd.ms-excel"
        )

# PDF Generation with proper cell formatting
if st.button("Generate PDF"):
    # Create PDF document
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Set default monospaced font
    pdf.set_font("Courier", size=10)
    
    # Add watermark
    pdf.set_font("Arial", style='I', size=60)
    pdf.set_text_color(200, 200, 200)
    pdf.rotate(45, 60, 60)
    pdf.text(30, 120, "Kerala Ground Water Department")
    pdf.rotate(0)
    
    # Add Heading
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, txt=estimate_heading, ln=True, align='C')
    
    # Calculate column widths
    col_widths = [10, 70, 20, 20, 20, 20]  # Adjusted widths for better fit
    
    # Function to split text into multiple lines
    def split_text(text, max_width):
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
    
    # Function to draw multi-cell with borders
    def multi_cell_with_border(w, h, txt, border=0, align='L', fill=False):
        lines = split_text(txt, w)
        x = pdf.get_x()
        y = pdf.get_y()
        
        # Calculate total height needed
        total_height = len(lines) * h
        
        # Draw each line
        for line in lines:
            pdf.cell(w, h, line, border=0, align=align)
            pdf.ln(h)
            pdf.set_x(x)
        
        # Draw border around entire cell
        if border:
            pdf.rect(x, y, w, total_height)
        
        # Return to original position (bottom of cell)
        pdf.set_xy(x, y + total_height)
    
    # Add Table Header
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    headers = ["S.No", "Item Name", "Rate", "Unit", "Qty", "Total"]
    
    # Draw header cells
    x = pdf.get_x()
    y = pdf.get_y()
    
    for i, header in enumerate(headers):
        pdf.set_xy(x + sum(col_widths[:i]), y)
        multi_cell_with_border(col_widths[i], 6, header, border=1, align='C')
    
    pdf.set_y(y + 6)  # Move down by header height
    
    # Add Table Rows
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
        
        x = pdf.get_x()
        y = pdf.get_y()
        
        # Find the maximum number of lines needed for this row
        max_lines = 1
        for i, text in enumerate(row_data):
            lines = split_text(str(text), col_widths[i])
            if len(lines) > max_lines:
                max_lines = len(lines)
        
        # Draw each cell in the row
        for i, text in enumerate(row_data):
            pdf.set_xy(x + sum(col_widths[:i]), y)
            # Calculate cell height based on max_lines
            cell_height = 6 * max_lines
            pdf.multi_cell(col_widths[i], 6, str(text), border=1, align='C')
            pdf.set_xy(x + sum(col_widths[:i+1]), y)
        
        # Move to next row position
        pdf.set_y(y + (6 * max_lines))
    
    # Add Subtotal, GST, Unforeseen, and Grand Total
    summary_data = [
        ("Subtotal", f"{total_cost:.2f}"),
        ("GST (18%)", f"{gst:.2f}"),
        ("Unforeseen (5%)", f"{unforeseen:.2f}"),
        ("Grand Total", f"{final_total:.2f}")
    ]
    
    for label, value in summary_data:
        pdf.cell(sum(col_widths[:-1]), 8, label, border=1, align='C')
        pdf.cell(col_widths[-1], 8, value, border=1, align='C')
        pdf.ln()
    
    # Save PDF to file
    pdf_file = "estimate.pdf"
    pdf.output(pdf_file)
    
    # Provide download link for PDF file
    with open(pdf_file, "rb") as f:
        st.download_button(
            label="Download PDF",
            data=f,
            file_name=pdf_file,
            mime="application/pdf"
        )
