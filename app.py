import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Mi Presupuesto", page_icon="💰", layout="wide")

st.markdown("""
<style>
    .main {background: linear-gradient(to bottom right, #eff6ff, #f5f3ff);}
</style>
""", unsafe_allow_html=True)

if 'expenses' not in st.session_state:
    st.session_state.expenses = []
if 'incomes' not in st.session_state:
    st.session_state.incomes = []
if 'installments' not in st.session_state:
    st.session_state.installments = []
if 'dollar_rate' not in st.session_state:
    st.session_state.dollar_rate = 1200

col1, col2 = st.columns([3, 1])
with col1:
    st.title("💰 Mi Presupuesto")
    st.caption("Gestión inteligente de finanzas personales")

with col2:
    st.session_state.dollar_rate = st.number_input("💵 Cotización USD", value=st.session_state.dollar_rate, step=10)

selected_month = st.date_input("📅 Seleccionar Mes", value=datetime.now()).strftime("%Y-%m")

tabs = st.tabs(["📊 Resumen", "💳 Gastos", "💰 Ingresos", "📆 Cuotas"])

with tabs[0]:
    df_expenses = pd.DataFrame(st.session_state.expenses)
    df_incomes = pd.DataFrame(st.session_state.incomes)
    
    if not df_expenses.empty:
        df_expenses['month'] = pd.to_datetime(df_expenses['date']).dt.strftime('%Y-%m')
        month_expenses = df_expenses[df_expenses['month'] == selected_month]['amount'].sum()
        future_installments = df_expenses[df_expenses.get('type', '') == 'installment']['amount'].sum()
    else:
        month_expenses = 0
        future_installments = 0
    
    if not df_incomes.empty:
        df_incomes['month'] = pd.to_datetime(df_incomes['date']).dt.strftime('%Y-%m')
        month_incomes = df_incomes[df_incomes['month'] == selected_month]['amount'].sum()
    else:
        month_incomes = 0
    
    balance = month_incomes - month_expenses
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Ingresos", f"${month_incomes:,.2f}")
    with col2:
        st.metric("Gastos", f"${month_expenses:,.2f}")
    with col3:
        st.metric("Balance", f"${balance:,.2f}")
    with col4:
        st.metric("Cuotas Futuras", f"${future_installments:,.2f}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Gastos por Categoría")
        if not df_expenses.empty and not df_expenses[df_expenses['month'] == selected_month].empty:
            category_data = df_expenses[df_expenses['month'] == selected_month].groupby('category')['amount'].sum()
            st.bar_chart(category_data)
        else:
            st.info("No hay datos para mostrar este mes")
    
    with col2:
        st.subheader("💹 Comparación Mensual")
        if not df_expenses.empty or not df_incomes.empty:
            comparison_data = pd.DataFrame({'Ingresos': [month_incomes], 'Gastos': [month_expenses]})
            st.bar_chart(comparison_data)
        else:
            st.info("No hay datos para mostrar")

with tabs[1]:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.expander("➕ Agregar Gasto Manual", expanded=False):
            with st.form("add_expense"):
                date = st.date_input("Fecha", value=datetime.now())
                description = st.text_input("Descripción")
                amount = st.number_input("Monto", min_value=0.0, step=100.0)
                category = st.selectbox("Categoría", ['Alimentación', 'Transporte', 'Vivienda', 'Servicios', 'Entretenimiento', 'Salud', 'Educación', 'Compras', 'Tecnología', 'Otros'])
                
                if st.form_submit_button("💾 Guardar"):
                    st.session_state.expenses.append({'date': date.strftime('%Y-%m-%d'), 'description': description, 'amount': amount, 'category': category, 'type': 'manual'})
                    st.success("✅ Gasto agregado!")
                    st.rerun()
    
    with col2:
        with st.expander("📤 Importar CSV de Movimientos", expanded=False):
            uploaded_file = st.file_uploader("Seleccionar archivo CSV", type=['csv'])
            
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8')
                    
                    if 'Cuotas Pendientes' not in df.columns:
                        for _, row in df.iterrows():
                            fecha_partes = str(row.get('Fecha Origen', '')).split('/')
                            if len(fecha_partes) == 3:
                                fecha = f"{fecha_partes[2]}-{fecha_partes[1].zfill(2)}-{fecha_partes[0].zfill(2)}"
                            else:
                                fecha = datetime.now().strftime('%Y-%m-%d')
                            
                            importe_str = str(row.get('Importe', '0')).replace(',', '')
                            importe = abs(float(importe_str))
                            
                            moneda = str(row.get('Moneda', '')).lower()
                            is_dollar = 'dolar' in moneda or 'usd' in moneda
                            
                            if is_dollar:
                                importe = importe * st.session_state.dollar_rate
                            
                            descripcion = str(row.get('Establecimiento', 'Sin descripción')).strip()
                            if is_dollar:
                                descripcion += " (USD)"
                            
                            st.session_state.expenses.append({'date': fecha, 'description': descripcion, 'amount': importe, 'category': 'Compras', 'type': 'imported'})
                        
                        st.success(f"✅ {len(df)} gastos importados!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al importar: {str(e)}")
    
    st.divider()
    st.subheader(f"Gastos del Mes - {selected_month}")
    
    if df_expenses.empty or df_expenses[df_expenses['month'] == selected_month].empty:
        st.info("No hay gastos registrados para este mes")
    else:
        month_df = df_expenses[df_expenses['month'] == selected_month].sort_values('date', ascending=False)
        
        for idx, row in month_df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 4, 2, 2, 1])
            with col1:
                st.text(row['date'])
            with col2:
                st.text(row['description'])
            with col3:
                st.text(row['category'])
            with col4:
                st.text(f"${row['amount']:,.2f}")
            with col5:
                if st.button("🗑️", key=f"del_exp_{idx}"):
                    st.session_state.expenses = [e for i, e in enumerate(st.session_state.expenses) if i != idx]
                    st.rerun()

with tabs[2]:
    with st.expander("➕ Agregar Ingreso", expanded=False):
        with st.form("add_income"):
            date = st.date_input("Fecha", value=datetime.now())
            description = st.text_input("Descripción")
            amount = st.number_input("Monto", min_value=0.0, step=1000.0)
            income_type = st.selectbox("Tipo", ['Salario', 'Freelance', 'Inversiones', 'Bonus', 'Otros'])
            
            if st.form_submit_button("💾 Guardar"):
                st.session_state.incomes.append({'date': date.strftime('%Y-%m-%d'), 'description': description, 'amount': amount, 'type': income_type})
                st.success("✅ Ingreso agregado!")
                st.rerun()
    
    st.divider()
    st.subheader(f"Ingresos del Mes - {selected_month}")
    
    if df_incomes.empty or df_incomes[df_incomes['month'] == selected_month].empty:
        st.info("No hay ingresos registrados para este mes")
    else:
        month_df = df_incomes[df_incomes['month'] == selected_month].sort_values('date', ascending=False)
        
        for idx, row in month_df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 4, 2, 2, 1])
            with col1:
                st.text(row['date'])
            with col2:
                st.text(row['description'])
            with col3:
                st.text(row['type'])
            with col4:
                st.text(f"${row['amount']:,.2f}")
            with col5:
                if st.button("🗑️", key=f"del_inc_{idx}"):
                    st.session_state.incomes = [i for j, i in enumerate(st.session_state.incomes) if j != idx]
                    st.rerun()

with tabs[3]:
    with st.expander("📤 Importar CSV de Cuotas Pendientes", expanded=False):
        uploaded_file = st.file_uploader("Seleccionar archivo CSV de cuotas", type=['csv'], key="cuotas")
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8')
                
                if 'Cuotas Pendientes' in df.columns:
                    for _, row in df.iterrows():
                        fecha_partes = str(row.get('Fecha Origen', '')).split('/')
                        if len(fecha_partes) == 3:
                            fecha = f"{fecha_partes[2]}-{fecha_partes[1].zfill(2)}-{fecha_partes[0].zfill(2)}"
                        else:
                            fecha = datetime.now().strftime('%Y-%m-%d')
                        
                        descripcion = str(row.get('Establecimiento', '')).strip()
                        importe_str = str(row.get('Importe', '0')).replace(',', '')
                        importe = float(importe_str)
                        total_cuotas = int(row.get('Codigo Plan', 0))
                        cuotas_pendientes = int(row.get('Cuotas Pendientes', 0))
                        
                        st.session_state.installments.append({'date': fecha, 'description': descripcion, 'amount': importe, 'total': total_cuotas, 'pending': cuotas_pendientes})
                        
                        monto_mensual = importe / cuotas_pendientes
                        cuotas_pagadas = total_cuotas - cuotas_pendientes
                        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
                        
                        for i in range(cuotas_pendientes):
                            nueva_fecha = fecha_obj.replace(month=((fecha_obj.month + cuotas_pagadas + i - 1) % 12) + 1, year=fecha_obj.year + (fecha_obj.month + cuotas_pagadas + i - 1) // 12)
                            numero_cuota = cuotas_pagadas + i + 1
                            st.session_state.expenses.append({'date': nueva_fecha.strftime('%Y-%m-%d'), 'description': f"{descripcion} (Cuota {numero_cuota}/{total_cuotas})", 'amount': monto_mensual, 'category': 'Compras', 'type': 'installment'})
                    
                    st.success(f"✅ {len(df)} cuotas importadas!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.divider()
    st.subheader("Todas las Cuotas Pendientes")
    
    if not st.session_state.installments:
        st.info("No hay cuotas pendientes")
    else:
        for idx, inst in enumerate(st.session_state.installments):
            col1, col2, col3, col4, col5 = st.columns([2, 4, 2, 2, 1])
            with col1:
                st.text(inst['date'])
            with col2:
                st.text(inst['description'])
            with col3:
                st.text(f"{inst['pending']}/{inst['total']}")
            with col4:
                st.text(f"${inst['amount']:,.2f}")
            with col5:
                if st.button("🗑️", key=f"del_inst_{idx}"):
                    st.session_state.installments.pop(idx)
                    st.rerun()

st.divider()
st.caption("💡 Aplicación de Presupuesto Personal - Streamlit Cloud")
