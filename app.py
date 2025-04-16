import streamlit as st
import json
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar
import os

# ---------- 初始設定 ----------
st.set_page_config(layout="wide")
THEME = st.sidebar.selectbox("主題模式", ["白天模式", "黑夜模式"])
if THEME == "白天模式":
    st.markdown("<style>body { background-color: white; color: black; }</style>", unsafe_allow_html=True)
else:
    st.markdown("<style>body { background-color: #1e1e1e; color: white; }</style>", unsafe_allow_html=True)

# ---------- 功能選單 ----------
def custom_sidebar():
    st.sidebar.markdown("### 功能選單")
    pages = {
        "📌 新增課程": "add",
        "📅 月曆視圖": "calendar",
        "⏱️ 總時數統計": "summary",
    }
    selected = st.sidebar.radio(
        label="功能選單",
        options=list(pages.keys()),
        label_visibility="collapsed",
        index=0,
    )
    return pages[selected]

menu = custom_sidebar()

# ---------- 資料處理 ----------
DB_FILE = "courses.json"

def load_courses():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_courses(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def calc_duration(start, end):
    fmt = "%Y/%m/%d %H:%M"
    return round((datetime.strptime(end, fmt) - datetime.strptime(start, fmt)).total_seconds() / 3600, 2)

# ---------- 新增課程 ----------
if menu == "add":
    st.header("📌 新增課程")
    with st.form("course_form"):
        course = st.text_input("課程名稱")
        student = st.text_input("學生名稱")
        teacher = st.text_input("老師名稱")
        start_time = st.datetime_input("課程開始時間")
        end_time = st.datetime_input("課程結束時間")
        submitted = st.form_submit_button("新增課程")

        if submitted:
            start_str = start_time.strftime("%Y/%m/%d %H:%M")
            end_str = end_time.strftime("%Y/%m/%d %H:%M")
            duration = calc_duration(start_str, end_str)

            new_course = {
                "課程名稱": course,
                "學生名稱": student,
                "老師名稱": teacher,
                "開始時間": start_str,
                "結束時間": end_str,
                "時數": duration
            }

            data = load_courses()
            data.append(new_course)
            save_courses(data)
            st.success("課程已新增！")

# ---------- 月曆視圖 ----------
elif menu == "calendar":
    st.header("📅 月曆視圖")
    raw_data = load_courses()
    events = []
    color_map = {}
    pastel_colors = ["#A0C4FF", "#BDB2FF", "#FFD6A5", "#FDFFB6", "#CAFFBF", "#9BF6FF", "#FFC6FF"]

    for i, course in enumerate(raw_data):
        cname = course["課程名稱"]
        if cname not in color_map:
            color_map[cname] = pastel_colors[len(color_map) % len(pastel_colors)]

        events.append({
            "title": f"{cname}({course['學生名稱']}): {course['老師名稱']}",
            "start": course["開始時間"].replace("/", "-") + ":00",
            "end": course["結束時間"].replace("/", "-") + ":00",
            "color": color_map[cname]
        })

    calendar_options = {
        "initialView": "timeGridWeek",
        "slotMinTime": "07:00:00",
        "slotMaxTime": "22:00:00",
        "allDaySlot": False,
        "locale": "zh-tw",
        "slotLabelFormat": {"hour": '2-digit', "minute": '2-digit', "hour12": False},
        "eventTimeFormat": {"hour": '2-digit', "minute": '2-digit', "hour12": False},
    }

    st.markdown("""
    <style>
    .fc-event-title, .fc-event-time {
        white-space: normal !important;
    }
    </style>
    """, unsafe_allow_html=True)

    calendar(events=events, options=calendar_options)

# ---------- 總時數 ----------
elif menu == "summary":
    st.header("⏱️ 課程總時數統計")
    data = load_courses()
    if not data:
        st.info("目前尚無課程資料。")
    else:
        df = pd.DataFrame(data)
        total_by_teacher = df.groupby("老師名稱")["時數"].sum().reset_index()
        total_by_course = df.groupby("課程名稱")["時數"].sum().reset_index()

        st.subheader("依老師統計")
        st.dataframe(total_by_teacher)

        st.subheader("依課程統計")
        st.dataframe(total_by_course)
