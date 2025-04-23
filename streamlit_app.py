# PDF Generation
if st.button("Generate PDF"):
    # Create PDF document
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Add watermark
    pdf.set_font("Arial", style='I', size=60)
    pdf.set_text_color(200, 200, 200)
    pdf.rotate(45, 60, 60)
    pdf.text(30, 120, "Watermark")
    pdf.rotate(0)
    
    # Add Heading
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, txt=estimate_heading, ln=True, align='C')
    
    # Calculate column widths
    col_widths = [10, 70, 20, 20, 20, 20]  # S.No, Item Name, Rate, Unit, Qty, Total
    
    # Function to split text into multiple lines
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
    
    # Function to calculate maximum lines needed for a row
    def calculate_max_lines(row_data):
        max_lines = 1
        for i, text in enumerate(row_data):
            lines = split_text(str(text), col_widths[i])
            if len(lines) > max_lines:
                max_lines = len(lines)
        return max_lines
    
    # Add Table Header
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    headers = ["Sl.No", "Item Name", "Rate", "Unit", "Qty", "Total"]
    
    # Draw header cells
    x_start = pdf.get_x()
    y_start = pdf.get_y()
    
    for i, header in enumerate(headers):
        pdf.set_xy(x_start + sum(col_widths[:i]), y_start)
        pdf.cell(col_widths[i], 6, header, border=1, align='C')
    
    pdf.set_y(y_start + 6)  # Move down by header height
    
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
        
        # Calculate maximum lines needed for this row
        max_lines = calculate_max_lines(row_data)
        row_height = 6 * max_lines
        
        x_row_start = pdf.get_x()
        y_row_start = pdf.get_y()
        
        # Draw each cell with the same height
        for i, text in enumerate(row_data):
            pdf.set_xy(x_row_start + sum(col_widths[:i]), y_row_start)
            
            # Get lines for this specific cell
            cell_lines = split_text(str(text), col_widths[i])
            
            # Center text vertically by calculating offset
            vertical_offset = (row_height - (6 * len(cell_lines))) / 2
            
            # Draw border first (full height)
            pdf.cell(col_widths[i], row_height, border=1)
            
            # Reset position to add text
            pdf.set_xy(x_row_start + sum(col_widths[:i]), y_row_start + vertical_offset)
            
            # Draw each line of text
            for line in cell_lines:
                pdf.cell(col_widths[i], 6, line, 0, 0, 'C')
                pdf.set_xy(x_row_start + sum(col_widths[:i]), pdf.get_y() + 6)
        
        # Move to next row position
        pdf.set_y(y_row_start + row_height)
    
    # Add Subtotal, GST, Unforeseen, and Grand Total
    summary_data = [
        ("Subtotal", f"{total_cost:.2f}"),
        ("GST (18%)", f"{gst:.2f}"),
        ("Unforeseen (5%)", f"{unforeseen:.2f}"),
        ("Grand Total", f"{final_total:.2f}")
    ]
    
    for label, value in summary_data:
        # Calculate position
        x = pdf.get_x()
        y = pdf.get_y()
        
        # Draw left cell (merged)
        pdf.multi_cell(sum(col_widths[:-1]), 8, label, border=1, align='C')
        pdf.set_xy(x + sum(col_widths[:-1]), y)
        
        # Draw right cell
        pdf.multi_cell(col_widths[-1], 8, value, border=1, align='C')
        
        # Move to next line
        pdf.set_xy(x, y + 8)
    
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
