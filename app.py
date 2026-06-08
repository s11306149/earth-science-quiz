import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="高中地科學科能力競賽 複習站", layout="centered")
st.title("🌋 高中地科學科能力競賽 複習站")

# 讀取 CSV 題庫
@st.cache_data
def load_data():
    try:
        return pd.read_csv("questions.csv")
    except Exception as e:
        st.error("讀取題庫檔案失敗，請檢查 questions.csv 格式是否正確。")
        return None

df = load_data()

if df is not None:
    # 側邊欄分類篩選
    categories = ["全部領域"] + list(df["分類"].dropna().unique())
    selected_cat = st.sidebar.selectbox("選擇學科領域", categories)

    if selected_cat != "全部領域":
        filtered_df = df[df["分類"] == selected_cat].reset_index(drop=True)
    else:
        filtered_df = df.reset_index(drop=True)

    st.sidebar.write(f"當前領域題數：{len(filtered_df)} 題")

    # 初始化 session state
    if "current_idx" not in st.session_state:
        st.session_state.current_idx = random.randint(0, len(filtered_df) - 1) if len(filtered_df) > 0 else -1
        st.session_state.submitted = False
        st.session_state.user_ans = None

    # 左側邊欄的強制換題按鈕
    if st.sidebar.button("🎲 隨機換一題"):
        if len(filtered_df) > 0:
            st.session_state.current_idx = random.randint(0, len(filtered_df) - 1)
            st.session_state.submitted = False
            st.session_state.user_ans = None
            st.rerun()

    if st.session_state.current_idx != -1 and len(filtered_df) > 0:
        # 防呆機制：避免切換分類時 index 超出範圍
        if st.session_state.current_idx >= len(filtered_df):
            st.session_state.current_idx = 0
             
        row = filtered_df.iloc[st.session_state.current_idx]
        
        st.subheader(f"題目：{row['題目']}")
        
        options = [
            f"(A) {row['選項A']}",
            f"(B) {row['選項B']}",
            f"(C) {row['選項C']}",
            f"(D) {row['選項D']}"
        ]
        
        # 讓使用者選擇答案
        user_choice = st.radio("請選擇你的答案：", options, index=None if not st.session_state.submitted else ["A","B","C","D"].index(st.session_state.user_ans))

        if not st.session_state.submitted:
            if st.button("⚡ 確認提交"):
                if user_choice:
                    st.session_state.user_ans = user_choice[1]
                    st.session_state.submitted = True
                    st.rerun()
                else:
                    st.warning("請先選擇一個答案！")
        else:
            correct_ans = str(row['正確答案']).strip().upper()
            if st.session_state.user_ans == correct_ans:
                st.success("🎉 回答正確！")
            else:
                st.error(f"❌ 答錯了！正確答案是：({correct_ans})")
            
            st.info(f"💡 **核心解析：**\n{row['詳解']}")
            
            # 【新增】答題完畢後，直接在下方顯示「下一題」按鈕
            if st.button("➡️ 下一題"):
                st.session_state.current_idx = random.randint(0, len(filtered_df) - 1)
                st.session_state.submitted = False
                st.session_state.user_ans = None
                st.rerun()
    else:
        st.info("該分類下目前沒有題目，請打開 Google 試算表補充！")
