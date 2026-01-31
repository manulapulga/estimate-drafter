import io
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Side, Font


def generate_bill_excel(
    selected_items,
    tender_mode,
    tender_percent
):
    wb = Workbook()
    ws = wb.active
    ws.title = "Bill"

    # ------------------ STYLES ------------------
    thin = Side(style="thin")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    header_font = Font(bold=True)

    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_align = Alignment(horizontal="left", vertical="center", wrap_text=True)

    # ------------------ DYNAMIC HEADER ------------------
    if tender_mode == "Below":
        agreed_title = f"Agreed Rate (Below {tender_percent}% PAC)"
    elif tender_mode == "Above":
        agreed_title = f"Agreed Rate (Above {tender_percent}% PAC)"
    else:
        agreed_title = "Agreed Rate (At PAC)"

    headers = [
        "Sl No",
        "Description",
        "Qty",
        "Unit",
        "Estimate Rate",
        agreed_title,
        "Amount"
    ]

    ws.append(headers)

    # Header formatting
    for col in range(1, 8):
        cell = ws.cell(row=1, column=col)
        cell.font = header_font
        cell.alignment = center_align
        cell.border = border

    # ------------------ ITEMS ------------------
    row = 2
    sl_no = 1

    for item in selected_items:

        # ---- Subheading ----
        if item.get("Type") == "Subheading":
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)
            cell = ws.cell(row=row, column=1, value=item["Item"])
            cell.alignment = left_align
            cell.border = border
            row += 1
            continue

        ws.cell(row=row, column=1, value=sl_no)
        ws.cell(row=row, column=2, value=item["Item"])
        ws.cell(row=row, column=3, value=item["Quantity"])
        ws.cell(row=row, column=4, value=item["Item Unit"])
        ws.cell(row=row, column=5, value=item["Unit Price"])

        # ---- AGREED RATE (FORMULA, 2 decimals) ----
        if tender_mode == "Below":
            ws.cell(row=row, column=6).value = (
                f"=ROUND(E{row}*(100-{tender_percent})/100,2)"
            )
        elif tender_mode == "Above":
            ws.cell(row=row, column=6).value = (
                f"=ROUND(E{row}*(100+{tender_percent})/100,2)"
            )
        else:  # At
            ws.cell(row=row, column=6).value = f"=ROUND(E{row},2)"

        # ---- AMOUNT (2 decimals) ----
        ws.cell(row=row, column=7).value = f"=ROUND(C{row}*F{row},2)"

        sl_no += 1
        row += 1

    # ------------------ SUMMARY (0 DECIMALS) ------------------
    sub_total_row = row

    # Sub Total
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    ws.cell(row=row, column=1, value="Sub Total")
    ws.cell(row=row, column=7, value=f"=ROUND(SUM(G2:G{row-1}),0)")
    row += 1

    # GST
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    ws.cell(row=row, column=1, value="GST @18%")
    ws.cell(row=row, column=7, value=f"=ROUND(G{sub_total_row}*0.18,0)")
    gst_row = row
    row += 1

    # Grand Total
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    ws.cell(row=row, column=1, value="Grand Total")
    ws.cell(
        row=row,
        column=7,
        value=f"=ROUND(G{sub_total_row}+G{gst_row},0)"
    )

    # ------------------ FORMATTING ------------------
    for r in range(1, ws.max_row + 1):
        for c in range(1, 8):
            cell = ws.cell(row=r, column=c)
            cell.border = border

            # Vertical center for all
            if r == 1:
                cell.alignment = center_align
            else:
                # Row 2 onwards
                if c == 2:
                    cell.alignment = left_align
                else:
                    cell.alignment = center_align

    # ------------------ COLUMN WIDTHS ------------------
    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 45
    ws.column_dimensions["C"].width = 10
    ws.column_dimensions["D"].width = 10
    ws.column_dimensions["E"].width = 15
    ws.column_dimensions["F"].width = 18
    ws.column_dimensions["G"].width = 15

    # ------------------ OUTPUT ------------------
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output
