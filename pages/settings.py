import streamlit as st
import pandas as pd

def show():
    st.title("⚙️ Конфигурация системы")
    st.caption("Справочник ТЭР, тарифы и метеотеги")
    
    tabs = st.tabs(["📋 Активные ресурсы", "🏷️ Теги"])
    
    with tabs[0]:
        df_res = pd.DataFrame(st.session_state.resources)
        edited = st.data_editor(
            df_res[["name", "unit", "coefTUT", "tariff", "active"]],
            column_config={
                "name": "Вид энергоресурса",
                "unit": "Ед. изм.",
                "coefTUT": st.column_config.NumberColumn("Коэф. (т.у.т.)", format="%.4f"),
                "tariff": st.column_config.NumberColumn("Тариф, ₸", format="%.2f"),
                "active": st.column_config.CheckboxColumn("Учёт")
            },
            use_container_width=True
        )
        if st.button("💾 Сохранить", type="primary"):
            for i, row in edited.iterrows():
                if i < len(st.session_state.resources):
                    st.session_state.resources[i]["name"] = row["name"]
                    st.session_state.resources[i]["unit"] = row["unit"]
                    st.session_state.resources[i]["coefTUT"] = row["coefTUT"]
                    st.session_state.resources[i]["tariff"] = row["tariff"]
                    st.session_state.resources[i]["active"] = row["active"]
            st.success("Сохранено!")
            st.rerun()
    
    with tabs[1]:
        new_tag = st.text_input("Новый тег")
        if st.button("➕ Добавить"):
            if new_tag and new_tag not in st.session_state.tags:
                st.session_state.tags.append(new_tag)
                st.rerun()
        
        for tag in st.session_state.tags:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"`{tag}`")
            with col2:
                if st.button("🗑️", key=tag):
                    st.session_state.tags.remove(tag)
                    st.rerun()
