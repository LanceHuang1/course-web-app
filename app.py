import streamlit as st
import json
from datetime import datetime
import os
from streamlit_calendar import calendar
import pytz

DATA_FILE = "courses.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(courses):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(courses, f, ensure_ascii=False, indent=2)

def parse_time(t):
    return datetime.strptime(t, "%Y/%m/%d %H:%M")

def main():
    st.set_page_config(page_title="課程管理系統", layout="wide")
    st.title("📘 課程管理系統")

    courses = load_data()

    st.sidebar.title("功能選單")
    action = st.sidebar.selectbox("請選擇操作", [
        "📥 新增課程", "📝 編輯課程", "🗑️ 刪除課程",
        "📋 所有課程", "⏱️ 總時數", "📅 月曆視圖"
    ])

    if action == "📥 新增課程":
        st.subheader("新增課程")
        course_name = st.text_input("課程名稱")
        student_name = st.text_input("學生名稱")
        teacher_name = st.text_input("老師名稱")
        start_time = st.text_input("開始時間（YYYY/MM/DD HH:MM）")
        end_time = st.text_input("結束時間（YYYY/MM/DD HH:MM）")

        if st.button("新增"):
            try:
                st_time = parse_time(start_time)
                et_time = parse_time(end_time)
                if st_time >= et_time:
                    st.error("結束時間必須晚於開始時間")
                else:
                    new_id = max([c["id"] for c in courses], default=0) + 1
                    courses.append({
                        "id": new_id,
                        "course_name": course_name,
                        "student_name": student_name,
                        "teacher_name": teacher_name,
                        "start_time": start_time,
                        "end_time": end_time
                    })
                    save_data(courses)
                    st.success("課程新增成功！")
            except:
                st.error("時間格式錯誤！")

    elif action == "📝 編輯課程":
        st.subheader("編輯課程")
        if not courses:
            st.info("目前沒有課程")
        else:
            options = {f"{c['id']}: {c['course_name']}": c for c in courses}
            selected = st.selectbox("選擇課程", list(options.keys()))
            course = options[selected]

            course["course_name"] = st.text_input("課程名稱", course["course_name"])
            course["student_name"] = st.text_input("學生名稱", course["student_name"])
            course["teacher_name"] = st.text_input("老師名稱", course["teacher_name"])
            course["start_time"] = st.text_input("開始時間", course["start_time"])
            course["end_time"] = st.text_input("結束時間", course["end_time"])

            if st.button("儲存變更"):
                try:
                    stime = parse_time(course["start_time"])
                    etime = parse_time(course["end_time"])
                    if stime >= etime:
                        st.error("結束時間需晚於開始")
                    else:
                        save_data(courses)
                        st.success("課程更新成功！")
                except:
                    st.error("時間格式錯誤！")

    elif action == "🗑️ 刪除課程":
        st.subheader("刪除課程")
        if not courses:
            st.info("目前沒有課程")
        else:
            options = {f"{c['id']}: {c['course_name']}": c for c in courses}
            selected = st.selectbox("選擇課程刪除", list(options.keys()))
            if st.button("刪除"):
                courses.remove(options[selected])
                save_data(courses)
                st.success("課程已刪除")

    elif action == "📋 所有課程":
        st.subheader("所有課程")
        if courses:
            for c in courses:
                st.markdown(f"""
                ### {c['course_name']}
                - 👤 學生：{c['student_name']} / 老師：{c['teacher_name']}
                - 🕒 {c['start_time']} 到 {c['end_time']}
                """)
        else:
            st.info("目前沒有任何課程。")

    elif action == "⏱️ 總時數":
        st.subheader("加總所有課程時數")
        total = 0
        for c in courses:
            try:
                stime = parse_time(c["start_time"])
                etime = parse_time(c["end_time"])
                total += (etime - stime).total_seconds() / 3600
            except:
                pass
        st.success(f"總時數為 {total:.2f} 小時")

    elif action == "📅 月曆視圖":
        st.subheader("📅 課程月曆")
        events = []
        for c in courses:
            try:
                events.append({
                    "title": f"{c['course_name']} ({c['student_name']})",
                    "start": parse_time(c["start_time"]).isoformat(),
                    "end": parse_time(c["end_time"]).isoformat(),
                    "extendedProps": {
                        "老師": c["teacher_name"],
                        "學生": c["student_name"]
                    }
                })
            except Exception as e:
                print("解析時間錯誤：", e)

        calendar_options = {
            "initialView": "dayGridMonth",
            "locale": "zh-tw",
            "headerToolbar": {
                "start": "prev,next today",
                "center": "title",
                "end": "dayGridMonth,timeGridWeek,timeGridDay"
            }
        }

        calendar(events=events, options=calendar_options)

if __name__ == "__main__":
    main()
