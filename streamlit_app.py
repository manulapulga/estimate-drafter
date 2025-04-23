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

# In your item display loop:
for idx, item in enumerate(st.session_state.selected_items):
    if item.get('type') == 'subheading':
        with st.expander(f"📌 {item['text']}", expanded=True):
            new_text = st.text_input("Subheading Text", value=item['text'], key=f"subheading_text_{idx}")
            if st.button(f"Update Subheading", key=f"update_subheading_btn_{idx}"):
                st.session_state.selected_items[idx]['text'] = new_text
                st.success("Subheading updated successfully!")
            if st.button(f"❌ Remove Subheading", key=f"remove_subheading_btn_{idx}"):
                remove_item(idx)
                st.rerun()
    else:
        with st.expander(f"Item {idx + 1}: {item['Item']}"):
            col1, col2 = st.columns([3, 1])
            with col1:
                item_name = st.selectbox("Select Item", [''] + item_names, 
                                       index=item_names.index(item['Item']) + 1 if item['Item'] in item_names else 0, 
                                       key=f"item_select_{idx}")
                st.text(f"Item Description: {item_name}" if item_name else "")
            with col2:
                quantity = st.text_input("Quantity", str(item['Quantity']), key=f"quantity_input_{idx}", placeholder="Input Quantity")
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
            if st.button(f"Update Item {idx + 1}", key=f"update_item_btn_{idx}"):
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
            if st.button(f"❌ Remove Item {idx + 1}", key=f"remove_item_btn_{idx}"):
                remove_item(idx)
                st.rerun()

# For the "Add Item" section
if st.session_state.item_count > sum(1 for item in st.session_state.selected_items if 'Item' in item):
    idx = len(st.session_state.selected_items)
    with st.expander(f"New Item {idx + 1}", expanded=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            item_name = st.selectbox("Select Item", [''] + item_names, key=f"new_item_select_{idx}")
            st.text(f"Item Description: {item_name}" if item_name else "")
        with col2:
            quantity = st.text_input("Quantity", "", key=f"new_quantity_input_{idx}", placeholder="Input Quantity")
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
        if st.button(f"Add to Estimate", key=f"add_item_confirm_{idx}"):
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

# For the "Add Subheading" section
if st.session_state.subheading_count > sum(1 for item in st.session_state.selected_items if item.get('type') == 'subheading'):
    idx = len(st.session_state.selected_items)
    with st.expander("New Subheading", expanded=True):
        subheading_text = st.text_input("Subheading Text", key=f"new_subheading_text_{idx}", placeholder="Enter subheading text")
        if st.button("Add Subheading", key=f"add_subheading_confirm_{idx}"):
            if subheading_text:
                st.session_state.selected_items.append({'type': 'subheading', 'text': subheading_text})
                st.success("Subheading added successfully!")
                st.rerun()
            else:
                st.error("Please enter subheading text")
