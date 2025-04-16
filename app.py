import streamlit as st
import json
from datetime import datetime, timedelta
import os
from streamlit_calendar import calendar
import pytz
import hashlib

DATA_FILE = "courses.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(courses):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(courses, f, ensure_ascii=False, indent=2)

def parse_time(dt_obj):
    return dt_obj.strftime("%Y/%m/%d %H:%M")

def str_to_datetime(s):
    return datetime.strptime(s, "%Y/%m/%d %H:%M")

def get_color(course_name):
    colors = [
        "#CFE2F3", "#D9EAD3", "#FFF2CC", "#FCE5CD", "#EAD1DC",
        "#D0E0E3", "#F4CCCC", "#F9CB9C", "#D9D2E9", "#C9DAF8"
    ]
    idx = int(hashlib.md5(course_name.encode()).hexdigest(), 16) % len(colors)
    return colors[idx]

def main():
    st.set_page_config(page_title="課程管理系統", layout="wide", page_icon="📘")
    st.markdown("<style>body {background-color: white;}</style>", unsafe_allow_html=True)  # Set background to white
    st.markdown("<h1 style='color:#3c3c3c;'>📘 課程管理系統</h1>", unsafe_allow_html=True)
    
    # Remove dots from sidebar menu
    st.sidebar.markdown("<style> .css-ffhzg2 { list-style-type: none; } </style>", unsafe_allow_html=True)
    st.sidebar.title("📌 功能選單")
    action = st.sidebar.radio("", [
        "📥 新增課程", "📝 編輯課程", "🗑️ 刪除課程",
        "📋 所有課程", "⏱️ 總時數", "📅 月曆視圖"
    ])

    courses = load_data()

    if action == "📥 新增課程":
        st.subheader("➕ 新增課程")
        course_name = st.text_input("課程名稱")
        student_name = st.text_input("學生名稱")
        teacher_name = st.text_input("老師名稱")
        date = st.date_input("日期")
        start_time = st.time_input("開始時間")
        end_time = st.time_input("結束時間")

        if st.button("新增課程"):
            st_dt = datetime.combine(date, start_time)
            et_dt = datetime.combine(date, end_time)
            if st_dt >= et_dt:
                st.error("❌ 結束時間必須晚於開始時間")
            else:
                new_id = max([c["id"] for c in courses], default=0) + 1
                courses.append({
                    "id": new_id,
                    "course_name": course_name,
                    "student_name": student_name,
                    "teacher_name": teacher_name,
                    "start_time": parse_time(st_dt),
                    "end_time": parse_time(et_dt)
                })
                save_data(courses)
                st.success("✅ 課程新增成功")

    elif action == "📝 編輯課程":
        st.subheader("🛠️ 編輯課程")
        if not courses:
            st.info("目前沒有課程")
        else:
            course_dict = {f'{c["id"]}: {c["course_name"]}': c for c in courses}
            selected = st.selectbox("選擇課程", list(course_dict.keys()))
            course = course_dict[selected]
            course["course_name"] = st.text_input("課程名稱", course["course_name"])
            course["student_name"] = st.text_input("學生名稱", course["student_name"])
            course["teacher_name"] = st.text_input("老師名稱", course["teacher_name"])

            dt = str_to_datetime(course["start_time"])
            et = str_to_datetime(course["end_time"])
            date = st.date_input("日期", dt.date())
            start_time = st.time_input("開始時間", dt.time())
            end_time = st.time_input("結束時間", et.time())

            if st.button("儲存變更"):
                if start_time >= end_time:
                    st.error("❌ 結束時間需晚於開始")
                else:
                    course["start_time"] = parse_time(datetime.combine(date, start_time))
                    course["end_time"] = parse_time(datetime.combine(date, end_time))
                    save_data(courses)
                    st.success("✅ 課程更新成功")

    elif action == "🗑️ 刪除課程":
        st.subheader("🗑️ 刪除課程")
        if not courses:
            st.info("目前沒有課程")
        else:
            course_dict = {f'{c["id"]}: {c["course_name"]}': c for c in courses}
            selected = st.selectbox("選擇要刪除的課程", list(course_dict.keys()))
            if st.button("刪除"):
                courses.remove(course_dict[selected])
                save_data(courses)
                st.success("✅ 課程已刪除")

    elif action == "📋 所有課程":
        st.subheader("📋 所有課程")
        if not courses:
            st.info("目前沒有課程")
        else:
            for c in courses:
                st.markdown(f"""
                ### {c['course_name']}
                - 👤 學生：{c['student_name']} ／ 老師：{c['teacher_name']}
                - 🕒 {c['start_time']} ~ {c['end_time']}
                """)

    elif action == "⏱️ 總時數":
        st.subheader("⏱️ 總時數")
        total = 0
        for c in courses:
            try:
                start = str_to_datetime(c["start_time"])
                end = str_to_datetime(c["end_time"])
                total += (end - start).total_seconds() / 3600
            except:
                pass
        st.success(f"📚 所有課程總時數：{total:.2f} 小時")

    elif action == "📅 月曆視圖":
        st.subheader("📅 月曆視圖")
        events = []
        for c in courses:
            try:
                events.append({
                    "title": f"{c['course_name']} ({c['student_name']})",
                    "start": str_to_datetime(c["start_time"]).isoformat(),
                    "end": str_to_datetime(c["end_time"]).isoformat(),
                    "backgroundColor": get_color(c["course_name"]),
                    "borderColor": get_color(c["course_name"]),
                    "textColor": "#000000"
                })
            except:
                pass

        calendar_options = {
            "initialView": "dayGridMonth",
            "locale": "zh-tw",
            "headerToolbar": {
                "start": "prev,next today",
                "center": "title",
                "end": "dayGridMonth,timeGridWeek,timeGridDay"
            },
            "height": 700,
            "eventContent": {"borderRadius": "8px", "padding": "4px", "overflow": "hidden"},  # Add bottom color for events
            "scrolling": True  # Enable scrolling for long events
        }
        calendar(events=events, options=calendar_options)

if __name__ == "__main__":
    main()
