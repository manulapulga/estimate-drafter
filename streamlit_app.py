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
            st.text(f"Full Item Name: {item_name}")
        else:
            st.text("")  # Empty space for alignment
    
    with col2:
        if item_name != '':
            # Get item details
            item_data = data[data['Item Name'] == item_name].iloc[0]
            unit_price = item_data['Unit Price']
            unit = item_data['Item Unit']
            
            # Display unit price with unit in the right column
            st.text(f"Price: {unit_price:.2f}/{unit}")
            
            # Quantity input
            quantity = st.text_input("", "", key=f"qty_{i}", placeholder="Qty")
            
            # Calculate and display total when quantity is entered
            if quantity:
                try:
                    qty = float(quantity)
                    if qty > 0:
                        total = qty * unit_price
                        st.text(f"Total: {total:.2f}")
                except ValueError:
                    st.text("Invalid Qty")
            else:
                st.text("")  # Empty space when no quantity
        else:
            # Empty column when no item selected
            quantity = st.text_input("", "", key=f"qty_{i}", placeholder="Qty")
            st.text("")  # Empty space
    
    # Add to selected items if valid
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
    # ... [rest of Excel generation code] ...

# PDF Generation (unchanged)
if st.button("Generate PDF"):
    # ... [rest of PDF generation code] ...
