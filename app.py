import streamlit as st
import json
import os
from datetime import datetime, date, time
from streamlit_option_menu import option_menu
from streamlit_calendar import calendar

data_file = "courses.json"

# 將時間以 YYYY/MM/DD HH:MM 格式存取，並解析

def parse_time(dt: datetime) -> str:
    return dt.strftime("%Y/%m/%d %H:%M")


def str_to_datetime(s: str) -> datetime:
    # 支援多種格式解析（如 YYYY/MM/DD HH:MM 或 YYYY-MM-DD HH:MM）
    for fmt in ("%Y/%m/%d %H:%M", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"時間格式不正確: {s}")


def load_data() -> list:
    if not os.path.exists(data_file):
        return []
    with open(data_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(courses: list) -> None:
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(courses, f, ensure_ascii=False, indent=2)


def get_color(name: str) -> str:
    import hashlib
    h = hashlib.md5(name.encode()).hexdigest()
    # 取前6位 hex 作為顏色，配上透明度
    return f"#{h[:6]}55"


def main():
    st.set_page_config(page_title="課程管理系統", layout="wide")
    st.markdown("<h1 style='color:#3c3c3c;'>📘 課程管理系統</h1>", unsafe_allow_html=True)

    # 側邊選單：使用 option_menu
    with st.sidebar:
        action = option_menu(
            "📌 功能選單", 
            ["📥 新增課程", "📝 編輯課程", "🗑️ 刪除課程", "📋 所有課程", "⏱️ 時數統計", "📅 月曆視圖"],
            icons=["plus", "pencil", "trash", "list", "clock", "calendar"],
            menu_icon="cast", 
            default_index=0
        )

    courses = load_data()

    if action == "📥 新增課程":
        st.subheader("➕ 新增課程")
        course_names = sorted({c["course_name"] for c in courses})
        student_names = sorted({c["student_name"] for c in courses})
        teacher_names = sorted({c["teacher_name"] for c in courses})

        course_name = st.selectbox("課程名稱", [""] + course_names)
        student_name = st.selectbox("學生名稱", [""] + student_names)
        teacher_name = st.selectbox("老師名稱", [""] + teacher_names)
        d = st.date_input("日期")
        t1 = st.time_input("開始時間")
        t2 = st.time_input("結束時間")

        if st.button("新增課程"):
            st_dt = datetime.combine(d, t1)
            et_dt = datetime.combine(d, t2)
            if st_dt >= et_dt:
                st.error("❌ 結束時間必須晚於開始時間")
            else:
                new_id = max((c["id"] for c in courses), default=0) + 1
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
            opts = {f"{c['id']}: {c['course_name']}": c for c in courses}
            sel = st.selectbox("選擇課程", list(opts.keys()))
            course = opts[sel]
            course["course_name"] = st.text_input("課程名稱", course["course_name"])
            course["student_name"] = st.text_input("學生名稱", course["student_name"])
            course["teacher_name"] = st.text_input("老師名稱", course["teacher_name"])

            dt = str_to_datetime(course["start_time"])
            et = str_to_datetime(course["end_time"])
            d = st.date_input("日期", dt.date())
            t1 = st.time_input("開始時間", dt.time())
            t2 = st.time_input("結束時間", et.time())

            if st.button("儲存變更"):
                if t1 >= t2:
                    st.error("❌ 結束時間需晚於開始時間")
                else:
                    course["start_time"] = parse_time(datetime.combine(d, t1))
                    course["end_time"] = parse_time(datetime.combine(d, t2))
                    save_data(courses)
                    st.success("✅ 課程更新成功")

    elif action == "🗑️ 刪除課程":
        st.subheader("🗑️ 刪除課程")
        if not courses:
            st.info("目前沒有課程")
        else:
            opts = {f"{c['id']}: {c['course_name']}": c for c in courses}
            sel = st.selectbox("選擇要刪除的課程", list(opts.keys()))
            if st.button("刪除"):
                courses.remove(opts[sel])
                save_data(courses)
                st.success("✅ 課程已刪除")

    elif action == "📋 所有課程":
        st.subheader("📋 所有課程")
        if not courses:
            st.info("目前沒有課程")
        else:
            for c in courses:
                st.markdown(f"### {c['course_name']}\n" +
                            f"- 👤 學生：{c['student_name']} ／ 老師：{c['teacher_name']}\n" +
                            f"- 🕒 {c['start_time']} ~ {c['end_time']}")

    elif action == "⏱️ 時數統計":
        st.subheader("⏱️ 時數統計")
        sd = st.date_input("開始日期")
        ed = st.date_input("結束日期", min_value=sd)
        course_names = sorted({c['course_name'] for c in courses})
        sel_course = st.selectbox("選擇課程名稱", ["全部課程"] + course_names)

        total_h = 0.0
        filtered = []
        for c in courses:
            st_dt = str_to_datetime(c['start_time'])
            en_dt = str_to_datetime(c['end_time'])
            if sd <= st_dt.date() <= ed:
                if sel_course == "全部課程" or c['course_name'] == sel_course:
                    filtered.append(c)
                    total_h += (en_dt - st_dt).total_seconds() / 3600

        if filtered:
            for c in filtered:
                dur = (str_to_datetime(c['end_time']) - str_to_datetime(c['start_time'])).total_seconds() / 3600
                st.markdown(f"### {c['course_name']}\n" +
                            f"- 👤 學生：{c['student_name']} ／ 老師：{c['teacher_name']}\n" +
                            f"- 🕒 {c['start_time']} ~ {c['end_time']}\n" +
                            f"- ⏳ 時數：{dur:.2f} 小時")
            st.success(f"📚 選擇範圍內的總時數：{total_h:.2f} 小時")
        else:
            st.info("沒有符合條件的課程")

    elif action == "📅 月曆視圖":
        st.subheader("📅 月曆視圖")
        events = []
        for c in courses:
            try:
                events.append({
                    'title': f"{c['course_name']} ({c['student_name']})",
                    'start': str_to_datetime(c['start_time']).isoformat(),
                    'end': str_to_datetime(c['end_time']).isoformat(),
                    'backgroundColor': get_color(c['course_name']),
                    'borderColor': get_color(c['course_name']),
                    'textColor': '#000000'
                })
            except Exception:
                continue

        calendar_opts = {
            'initialView': 'dayGridMonth',
            'locale': 'zh-tw',
            'headerToolbar': {
                'start': 'prev,next today',
                'center': 'title',
                'end': 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            'height': 700,
            'eventDidMount': """
                function(info) {
                    info.el.style.whiteSpace = 'normal';
                    info.el.style.overflowWrap = 'break-word';
                    info.el.style.fontFamily = 'Verdana';
                    info.el.style.fontSize = '14pt';
                }
            """
        }
        calendar(events=events, options=calendar_opts)


if __name__ == '__main__':
    main()
