import streamlit as st
from item_wizard import show_item_wizard
import pandas as pd

# This page is only useful when accessed from main_app with wizard_target_index set
if "wizard_target_index" not in st.session_state or st.session_state["wizard_target_index"] is None:
    st.warning("No item selected to update.")
    st.stop()

wizard_data = pd.read_excel("Data Base/items.xltm", sheet_name=st.session_state.logged_in_username)
main_data = wizard_data  # You can load separately if needed

def handle_item_selection(selected_item):
    idx = st.session_state["wizard_target_index"]

    # Get data
    wizard_item = wizard_data[wizard_data['Item Name'] == selected_item].iloc[0]
    main_item = main_data[main_data['Item Name'] == selected_item]
    
    unit_price = main_item['Unit Price'].iloc[0] if not main_item.empty else wizard_item['Unit Price']
    unit = main_item['Item Unit'].iloc[0] if not main_item.empty else wizard_item['Item Unit']

    # Preserve quantity & remarks
    existing = st.session_state.selected_items[idx]
    st.session_state.selected_items[idx] = {
        'Item': selected_item,
        'Quantity': existing['Quantity'],
        'Unit Price': unit_price,
        'Item Unit': unit,
        'Cost': existing['Quantity'] * unit_price,
        'Type': 'Standard',
        'GST_Applicable': True,
        'Quantity_Remarks': existing.get('Quantity_Remarks', '')
    }

    # Clear wizard state and go back
    st.session_state["wizard_target_index"] = None
    st.success(f"Item updated to '{selected_item}'")
    st.switch_page("streamlit_app.py")

st.markdown("""
<div style="text-align: center; font-size:22px; font-weight:600; padding: 0.5rem 0;">
🔍 Change Item Wizard
</div>
""", unsafe_allow_html=True)
show_item_wizard(wizard_data, handle_item_selection, st.session_state.selected_items)
