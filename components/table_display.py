"""Table display component"""

import streamlit as st
import os
from pdf_generator import generate_pdf


def render_table():
    """Render the data table with edit/delete buttons and PDF export"""
    if not st.session_state.table_data:
        return
    
    # Table title
    st.markdown("### 📊 Quotation Table")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Table header row - responsive column widths
    header_cols = st.columns([0.8, 1.5, 1.2, 1, 0.8, 1, 1.5, 1, 2])
    headers = ["#", "Brand", "Length", "Voltage", "LED", "Wattage", "Driver", "Discount", "Actions"]
    for i, header in enumerate(headers):
        with header_cols[i]:
            st.markdown(f"<strong style='color: #f1f5f9; font-size: 0.85rem; white-space: nowrap;'>{header}</strong>", unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 0.5rem 0; border-color: #334155;'>", unsafe_allow_html=True)
    
    # Table rows - responsive column widths
    for idx, row in enumerate(st.session_state.table_data):
        col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([0.8, 1.5, 1.2, 1, 0.8, 1, 1.5, 1, 2])
        
        with col1:
            st.markdown(f"<div style='color: #cbd5e1; white-space: nowrap;'>{idx + 1}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div style='color: #f1f5f9; white-space: nowrap;'>{row.get('Brand', '-')}</div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div style='color: #f1f5f9; white-space: nowrap;'>{row.get('Length', '-')}</div>", unsafe_allow_html=True)
        with col4:
            st.markdown(f"<div style='color: #f1f5f9; white-space: nowrap;'>{row.get('Voltage', '-')}</div>", unsafe_allow_html=True)
        with col5:
            st.markdown(f"<div style='color: #f1f5f9; white-space: nowrap;'>{row.get('LED', '-')}</div>", unsafe_allow_html=True)
        with col6:
            st.markdown(f"<div style='color: #f1f5f9; font-weight: 600; white-space: nowrap;'>{row.get('Wattage', '-')}</div>", unsafe_allow_html=True)
        with col7:
            st.markdown(f"<div style='color: #f1f5f9; white-space: nowrap;'>{row.get('Driver', '-')}</div>", unsafe_allow_html=True)
        with col8:
            st.markdown(f"<div style='color: #f1f5f9; white-space: nowrap;'>{row.get('Discount', '-')}</div>", unsafe_allow_html=True)
        with col9:
            col_edit, col_del = st.columns(2)
            with col_edit:
                if st.button("✏️", key=f"edit_{idx}", type="secondary", use_container_width=True, help="Edit this row"):
                    st.session_state.editing_row = row
                    st.rerun()
            with col_del:
                if st.button("🗑️", key=f"delete_{idx}", type="secondary", use_container_width=True, help="Delete this row"):
                    deleted_item = st.session_state.table_data.pop(idx)
                    if st.session_state.editing_row == row:
                        st.session_state.editing_row = None
                    st.success(f"✅ Deleted: {deleted_item.get('Driver', 'item')}")
                    st.rerun()
        
        if idx < len(st.session_state.table_data) - 1:
            st.markdown("<hr style='margin: 0.5rem 0; border-color: #334155;'>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # PDF Export section
    st.markdown("### Export Options")
    
    # Stack buttons on mobile
    col1, col2 = st.columns([1, 1], gap="small")
    
    with col1:
        if st.button("📄 Generate PDF", type="primary", use_container_width=True, help="Generate a PDF document from the table data"):
            try:
                with st.spinner("🔄 Generating PDF..."):
                    filename = generate_pdf(st.session_state.table_data)
                    with open(filename, "rb") as pdf_file:
                        st.download_button(
                            label="⬇️ Download PDF",
                            data=pdf_file.read(),
                            file_name=filename,
                            mime="application/pdf",
                            use_container_width=True,
                            type="primary"
                        )
                    os.remove(filename)
                    st.success("✅ PDF generated successfully!")
            except Exception as e:
                st.error(f"❌ Error generating PDF: {e}")
    
    with col2:
        if st.button("🗑️ Clear PDF", type="secondary", use_container_width=True, help="Remove all entries from the PDF"):
            if st.session_state.table_data:
                count = len(st.session_state.table_data)
                st.session_state.table_data = []
                st.session_state.editing_row = None
                st.success(f"✅ Cleared {count} entries from PDF!")
                st.rerun()
            else:
                st.info("PDF is already empty")

