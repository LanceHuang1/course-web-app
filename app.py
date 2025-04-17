import streamlit as st
import json
from datetime import datetime, timedelta
import os
from streamlit_calendar import calendar
from streamlit_option_menu import option_menu
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
    # 依課程名稱決定顏色 (淡色系)
    colors = [
        "#CFE2F3", "#D9EAD3", "#FFF2CC", "#FCE5CD", "#EAD1DC",
        "#D0E0E3", "#F4CCCC", "#F9CB9C", "#D9D2E9", "#C9DAF8"
    ]
    idx = int(hashlib.md5(course_name.encode()).hexdigest(), 16) % len(colors)
    return colors[idx]

def main():
    st.set_page_config(page_title="課程管理系統", layout="wide")
    st.markdown("<h1 style='color:#3c3c3c;'>📘 課程管理系統</h1>", unsafe_allow_html=True)
    # 功能選單（改為選單樣式）
    with st.sidebar:
        action = option_menu("功能選單", [
            "新增課程", "編輯課程", "刪除課程",
            "所有課程", "時數統計", "Calendar"
        ],
        icons=["plus", "pencil", "trash", "list", "clock", "calendar"],
        menu_icon="cast", default_index=0)

    courses = load_data()

    if action == "新增課程":
        st.subheader("➕ 新增課程")
        
        # 使用 selectbox 並結合輸入框來達到合併效果
        course_name = st.selectbox("課程名稱", [""] + course_names + ["新增課程"])
        if course_name == "新增課程":
            course_name = st.text_input("請輸入新的課程名稱")
        
        student_name = st.selectbox("學生名稱", [""] + student_names + ["新增學生"])
        if student_name == "新增學生":
            student_name = st.text_input("請輸入新的學生名稱")
        
        teacher_name = st.selectbox("老師名稱", [""] + teacher_names + ["新增老師"])
        if teacher_name == "新增老師":
            teacher_name = st.text_input("請輸入新的老師名稱")

        # 日期和時間
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
                new_course = {
                    "id": new_id,
                    "course_name": course_name,
                    "student_name": student_name,
                    "teacher_name": teacher_name,
                    "start_time": parse_time(st_dt),
                    "end_time": parse_time(et_dt)
                }
                courses.append(new_course)
                save_data(courses)
                st.success("✅ 課程新增成功")
                
                # 重置表單欄位
                st.session_state["course_name_input"] = ""
                st.session_state["student_name_input"] = ""
                st.session_state["teacher_name_input"] = ""
                st.session_state["course_date_input"] = datetime.now().date()
                st.session_state["start_time_input"] = datetime.now().time()
                st.session_state["end_time_input"] = (datetime.now() + timedelta(hours=1)).time()

    elif action == "編輯課程":
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

    elif action == "刪除課程":
        st.subheader("刪除課程")
        if not courses:
            st.info("目前沒有課程")
        else:
            course_dict = {f'{c["id"]}: {c["course_name"]}': c for c in courses}
            selected = st.selectbox("選擇要刪除的課程", list(course_dict.keys()))
            if st.button("刪除"):
                courses.remove(course_dict[selected])
                save_data(courses)
                st.success("✅ 課程已刪除")

    elif action == "所有課程":
        st.subheader("所有課程")
        if not courses:
            st.info("目前沒有課程")
        else:
            for c in courses:
                st.markdown(f"""
                ### {c['course_name']}
                - 👤 學生：{c['student_name']} ／ 老師：{c['teacher_name']}
                - 🕒 {c['start_time']} ~ {c['end_time']}
                """)

    elif action == "時數統計":
        st.subheader("時數統計")
        # 時間範圍選擇
        start_date = st.date_input("開始日期")
        end_date = st.date_input("結束日期", min_value=start_date)

        # 課程名稱篩選
        course_names = sorted(set(c["course_name"] for c in courses))  # 所有課程名稱
        selected_course = st.selectbox("選擇課程名稱", ["全部課程"] + course_names)

        total_hours = 0
        filtered_courses = []
        
        # 根據選擇的時間範圍和課程名稱進行過濾
        for c in courses:
            course_start_time = str_to_datetime(c["start_time"])
            course_end_time = str_to_datetime(c["end_time"])

            # 過濾時間範圍
            if start_date <= course_start_time.date() <= end_date:
                # 過濾課程名稱
                if selected_course == "全部課程" or c["course_name"] == selected_course:
                    filtered_courses.append(c)
                    total_hours += (course_end_time - course_start_time).total_seconds() / 3600

        # 顯示過濾後的課程
        if filtered_courses:
            for c in filtered_courses:
                st.markdown(f"""
                ### {c['course_name']}
                - 👤 學生：{c['student_name']} ／ 老師：{c['teacher_name']}
                - 🕒 {c['start_time']} ~ {c['end_time']}
                - ⏳ 時數：{(str_to_datetime(c['end_time']) - str_to_datetime(c['start_time'])).total_seconds() / 3600:.2f} 小時
                """)
            
            st.success(f"📚 選擇範圍內的總時數：{total_hours:.2f} 小時")
        else:
            st.info("沒有符合條件的課程")

    elif action == "Calendar":
        st.subheader("Calendar")
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
            "editable": True,
            "eventDurationEditable": True,
            "eventStartEditable": True,
            "height": 700,
        }
        
        updated_event = calendar(
            events=events,
            options=calendar_options,
            key="course_calendar"
        )

        # 顯示 updated_event 的內容來檢查它的結構
        st.write("DEBUG updated_event:", updated_event)
        
        # 點擊事件：顯示詳細資料
        if updated_event and "event" in updated_event:
            e = updated_event["event"]
            event_id = e["id"]
            target_course = next((c for c in courses if str(c["id"]) == event_id), None)
        
            if updated_event["trigger"] == "eventClick" and target_course:
                with st.expander(f"✏️ 編輯課程：{target_course['course_name']} ({target_course['student_name']})", expanded=True):
                    course_name = st.text_input("課程名稱", target_course["course_name"], key="edit_course_name")
                    student_name = st.text_input("學生名稱", target_course["student_name"], key="edit_student_name")
                    teacher_name = st.text_input("老師名稱", target_course["teacher_name"], key="edit_teacher_name")
        
                    start_dt = str_to_datetime(target_course["start_time"])
                    end_dt = str_to_datetime(target_course["end_time"])
                    date = st.date_input("日期", start_dt.date(), key="edit_date")
                    start_time = st.time_input("開始時間", start_dt.time(), key="edit_start")
                    end_time = st.time_input("結束時間", end_dt.time(), key="edit_end")
        
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 儲存修改", key="save_edit"):
                            target_course["course_name"] = course_name
                            target_course["student_name"] = student_name
                            target_course["teacher_name"] = teacher_name
                            target_course["start_time"] = parse_time(datetime.combine(date, start_time))
                            target_course["end_time"] = parse_time(datetime.combine(date, end_time))
                            save_data(courses)
                            st.success("✅ 課程已更新")
                
                    with col2:
                        if st.button("📄 複製課程", key="copy_course_trigger"):
                            st.session_state["copy_mode"] = target_course

        # 顯示複製課程用的表單（如果使用者剛按下「複製課程」）
        if "copy_mode" in st.session_state and st.session_state["copy_mode"]:
            copy_target = st.session_state["copy_mode"]
            st.markdown("## 🧬 複製課程")
            copy_date = st.date_input("新日期", datetime.now().date(), key="copy_date")
            copy_start = st.time_input("新開始時間", datetime.now().time(), key="copy_start")
            copy_end = st.time_input("新結束時間", (datetime.now() + timedelta(hours=1)).time(), key="copy_end")
        
            if st.button("✅ 建立複製課程", key="confirm_copy"):
                new_id = max([c["id"] for c in courses], default=0) + 1
                new_course = {
                    "id": new_id,
                    "course_name": copy_target["course_name"],
                    "student_name": copy_target["student_name"],
                    "teacher_name": copy_target["teacher_name"],
                    "start_time": parse_time(datetime.combine(copy_date, copy_start)),
                    "end_time": parse_time(datetime.combine(copy_date, copy_end)),
                }
                courses.append(new_course)
                save_data(courses)
                st.success("🎉 已成功複製課程")
                st.session_state["copy_mode"] = None  # 重置狀態
        
        elif updated_event["trigger"] in ["eventDrop", "eventResize"] and target_course:
            try:
                target_course["start_time"] = parse_time(datetime.fromisoformat(e["start"]))
                target_course["end_time"] = parse_time(datetime.fromisoformat(e["end"]))
                save_data(courses)
                st.success("✅ 課程時間已更新")
            except Exception as ex:
                st.error(f"❌ 無法更新時間：{ex}")

        # 拖曳或縮放事件：更新資料
        if updated_event and "event" in updated_event and updated_event["trigger"] in ["eventDrop", "eventResize"]:
            e = updated_event["event"]
            for c in courses:
                if str(c["id"]) == e["id"]:
                    c["start_time"] = parse_time(datetime.fromisoformat(e["start"]))
                    c["end_time"] = parse_time(datetime.fromisoformat(e["end"]))
                    break
            save_data(courses)
            st.success("✅ 課程時間已更新")

if __name__ == "__main__":
    main()
