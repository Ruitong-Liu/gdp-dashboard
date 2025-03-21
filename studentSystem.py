import streamlit as st
import pandas as pd
import datetime
import os
from datetime import date

# 确保数据文件夹存在
if not os.path.exists('data'):
    os.makedirs('data')

# 初始化数据文件
def init_data():
    if not os.path.exists('data/students.csv'):
        pd.DataFrame(columns=['姓名']).to_csv('data/students.csv', index=False)
    if not os.path.exists('data/deductions.csv'):
        # 创建DataFrame时指定数据类型，确保备注列为字符串类型
        df = pd.DataFrame({
            '姓名': pd.Series(dtype='str'),
            '日期': pd.Series(dtype='str'),
            '迟到': pd.Series(dtype='int'),
            '打架': pd.Series(dtype='int'),
            '作业未完成': pd.Series(dtype='int'),
            '课堂违纪': pd.Series(dtype='int'),
            '其他': pd.Series(dtype='int'),
            '备注': pd.Series(dtype='str')
        })
        df.to_csv('data/deductions.csv', index=False)

# 获取学生列表
def get_students():
    try:
        df = pd.read_csv('data/students.csv')
        return df['姓名'].tolist()
    except:
        return []

# 添加新学生
def add_student(name):
    if not name:
        return False
    
    students = get_students()
    if name in students:
        return False
    
    df = pd.read_csv('data/students.csv')
    df = pd.concat([df, pd.DataFrame({'姓名': [name]})], ignore_index=True)
    df.to_csv('data/students.csv', index=False)
    return True

# 获取学生单日扣分记录
def get_student_daily_deduction(name, date):
    try:
        df = pd.read_csv('data/deductions.csv')
        record = df[(df['姓名'] == name) & (df['日期'] == date.strftime('%Y-%m-%d'))]
        if record.empty:
            return {'迟到': 0, '打架': 0, '作业未完成': 0, '课堂违纪': 0, '其他': 0, '备注': ''}
        return record.iloc[0].to_dict()
    except:
        return {'迟到': 0, '打架': 0, '作业未完成': 0, '课堂违纪': 0, '其他': 0, '备注': ''}

# 更新学生单日扣分记录
def update_student_daily_deduction(name, date, late, fight, homework, discipline, others, notes):
    df = pd.read_csv('data/deductions.csv')
    
    # 检查是否已存在该学生当天的记录
    mask = (df['姓名'] == name) & (df['日期'] == date.strftime('%Y-%m-%d'))
    
    if mask.any():
        # 更新现有记录，逐个更新以避免数据类型警告
        df.loc[mask, '迟到'] = late
        df.loc[mask, '打架'] = fight
        df.loc[mask, '作业未完成'] = homework
        df.loc[mask, '课堂违纪'] = discipline
        df.loc[mask, '其他'] = others
        df.loc[mask, '备注'] = notes
    else:
        # 添加新记录
        new_record = pd.DataFrame({
            '姓名': [name],
            '日期': [date.strftime('%Y-%m-%d')],
            '迟到': [late],
            '打架': [fight],
            '作业未完成': [homework],
            '课堂违纪': [discipline],
            '其他': [others],
            '备注': [notes]
        })
        df = pd.concat([df, new_record], ignore_index=True)
    
    df.to_csv('data/deductions.csv', index=False)

# 重置学生单日扣分记录
def reset_student_daily_deduction(name, date):
    df = pd.read_csv('data/deductions.csv')
    mask = (df['姓名'] == name) & (df['日期'] == date.strftime('%Y-%m-%d'))
    
    if mask.any():
        # 先显式转换数据类型，避免FutureWarning
        df.loc[mask, '迟到'] = 0
        df.loc[mask, '打架'] = 0
        df.loc[mask, '作业未完成'] = 0
        df.loc[mask, '课堂违纪'] = 0
        df.loc[mask, '其他'] = 0
        df.loc[mask, '备注'] = ''
        df.to_csv('data/deductions.csv', index=False)

# 获取学生总扣分情况
def get_student_total_deduction(name):
    try:
        df = pd.read_csv('data/deductions.csv')
        student_records = df[df['姓名'] == name]
        
        if student_records.empty:
            return 0
        
        total_deduction = (
            student_records['迟到'].sum() + 
            student_records['打架'].sum() + 
            student_records['作业未完成'].sum() + 
            student_records['课堂违纪'].sum() + 
            student_records['其他'].sum()
        )
        
        return total_deduction
    except:
        return 0

# 获取所有学生扣分情况汇总
def get_all_students_deductions():
    try:
        students = get_students()
        deductions_df = pd.read_csv('data/deductions.csv')
        
        result = []
        for student in students:
            student_records = deductions_df[deductions_df['姓名'] == student]
            
            total_late = student_records['迟到'].sum()
            total_fight = student_records['打架'].sum()
            total_homework = student_records['作业未完成'].sum()
            total_discipline = student_records['课堂违纪'].sum()
            total_others = student_records['其他'].sum()
            total_deduction = total_late + total_fight + total_homework + total_discipline + total_others
            moral_score = 100 - total_deduction
            
            result.append({
                '姓名': student,
                '迟到': total_late,
                '打架': total_fight,
                '作业未完成': total_homework,
                '课堂违纪': total_discipline,
                '其他扣分': total_others,
                '总扣分': total_deduction,
                '德育分': max(0, moral_score)
            })
        
        return pd.DataFrame(result)
    except Exception as e:
        st.error(f"获取数据时发生错误: {e}")
        return pd.DataFrame()

# 导出所有学生扣分情况到Excel
def export_to_excel():
    summary_df = get_all_students_deductions()
    detailed_df = pd.read_csv('data/deductions.csv')
    
    # 创建Excel写入器
    with pd.ExcelWriter('德育评分系统记录.xlsx') as writer:
        summary_df.to_excel(writer, sheet_name='学生德育分汇总', index=False)
        detailed_df.to_excel(writer, sheet_name='详细扣分记录', index=False)
    
    return '德育评分系统记录.xlsx'

# 从Excel或CSV文件导入学生名单
def import_students_from_file(uploaded_file):
    try:
        # 根据文件类型选择读取方法
        if uploaded_file.name.endswith('.csv'):
            new_students_df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            new_students_df = pd.read_excel(uploaded_file)
        else:
            return False, "不支持的文件格式，请上传CSV或Excel文件"
        
        # 检查是否包含必要的列
        if '姓名' not in new_students_df.columns:
            return False, "文件中缺少'姓名'列"
        
        # 读取现有学生名单
        if os.path.exists('data/students.csv'):
            existing_students_df = pd.read_csv('data/students.csv')
        else:
            existing_students_df = pd.DataFrame(columns=['姓名'])
        
        # 获取新学生列表，排除已存在的学生
        existing_names = set(existing_students_df['姓名'].tolist())
        new_students = []
        duplicates = []
        
        for name in new_students_df['姓名']:
            if pd.notna(name) and name.strip() != '':
                if name in existing_names:
                    duplicates.append(name)
                else:
                    new_students.append(name)
                    existing_names.add(name)
        
        # 添加新学生到数据框
        if new_students:
            new_df = pd.DataFrame({'姓名': new_students})
            updated_df = pd.concat([existing_students_df, new_df], ignore_index=True)
            updated_df.to_csv('data/students.csv', index=False)
        
        return True, f"成功导入{len(new_students)}名学生" + (f"，{len(duplicates)}名学生已存在" if duplicates else "")
    
    except Exception as e:
        return False, f"导入失败: {str(e)}"

# 删除学生
def delete_student(name):
    if not name:
        return False
    
    # 删除学生记录
    try:
        # 从学生列表中删除
        students_df = pd.read_csv('data/students.csv')
        students_df = students_df[students_df['姓名'] != name]
        students_df.to_csv('data/students.csv', index=False)
        
        # 从扣分记录中删除
        deductions_df = pd.read_csv('data/deductions.csv')
        deductions_df = deductions_df[deductions_df['姓名'] != name]
        deductions_df.to_csv('data/deductions.csv', index=False)
        
        return True
    except Exception as e:
        print(f"删除学生时出错: {e}")
        return False

# 清除所有学生名单
def clear_all_students():
    try:
        # 首先检查并创建数据目录
        if not os.path.exists('data'):
            os.makedirs('data')
        
        # 直接用空DataFrame覆盖原文件
        empty_df = pd.DataFrame(columns=['姓名'])
        empty_df.to_csv('data/students.csv', index=False)
        
        # 同时清除扣分记录
        df = pd.DataFrame({
            '姓名': pd.Series(dtype='str'),
            '日期': pd.Series(dtype='str'),
            '迟到': pd.Series(dtype='int'),
            '打架': pd.Series(dtype='int'),
            '作业未完成': pd.Series(dtype='int'),
            '课堂违纪': pd.Series(dtype='int'),
            '其他': pd.Series(dtype='int'),
            '备注': pd.Series(dtype='str')
        })
        df.to_csv('data/deductions.csv', index=False)
        
        return True
    except Exception as e:
        print(f"清除学生名单时出错: {e}")
        return False

# 清除所有德育分记录
def clear_all_deductions():
    try:
        # 仅重新创建空的扣分记录文件
        df = pd.DataFrame({
            '姓名': pd.Series(dtype='str'),
            '日期': pd.Series(dtype='str'),
            '迟到': pd.Series(dtype='int'),
            '打架': pd.Series(dtype='int'),
            '作业未完成': pd.Series(dtype='int'),
            '课堂违纪': pd.Series(dtype='int'),
            '其他': pd.Series(dtype='int'),
            '备注': pd.Series(dtype='str')
        })
        df.to_csv('data/deductions.csv', index=False)
        
        return True
    except Exception as e:
        print(f"清除德育分记录时出错: {e}")
        return False


# 应用主函数
def main():
    st.set_page_config(page_title="学校德育评分系统", layout="wide")
    
    # 初始化数据
    init_data()
    
    st.title("学校德育评分系统")
    
    # 侧边栏 - 系统导航
    st.sidebar.title("系统导航")
    
    # 从session_state获取当前页面，如果没有则默认为"首页"
    if 'page' not in st.session_state:
        st.session_state.page = "首页"
    
    # 使用侧边栏切换页面
    page = st.sidebar.radio("请选择功能", ["首页", "学生德育评分", "学生德育分查询"], index=["首页", "学生德育评分", "学生德育分查询"].index(st.session_state.page))
    
    # 更新session_state中的页面
    st.session_state.page = page
    
    if page == "首页":
        show_home_page()
    elif page == "学生德育评分":
        show_deduction_page()
    elif page == "学生德育分查询":
        show_query_page()

# 首页
def show_home_page():
    st.header("欢迎使用学校德育评分系统")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("学生德育评分")
        st.write("在此功能中，您可以记录学生的德育表现，包括迟到、打架等情况。")
        if st.button("前往学生德育评分", key="goto_deduction"):
            st.session_state.page = "学生德育评分"
            st.rerun()
    
    with col2:
        st.subheader("学生德育分查询")
        st.write("在此功能中，您可以查看所有学生的德育分情况，并导出Excel表格。")
        if st.button("前往学生德育分查询", key="goto_query"):
            st.session_state.page = "学生德育分查询"
            st.rerun()
    
    st.markdown("---")
    
    # 分成两列：左侧添加单个学生，右侧批量导入学生
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("添加新学生")
        new_student = st.text_input("请输入新学生姓名")
        if st.button("添加"):
            if add_student(new_student):
                st.success(f"已成功添加学生：{new_student}")
            else:
                st.warning("学生姓名不能为空或该学生已存在")
    
    with col2:
        st.subheader("批量导入学生名单")
        st.write("上传包含学生名单的Excel或CSV文件，文件中必须包含'姓名'列")
        
        uploaded_file = st.file_uploader("选择文件", type=["csv", "xlsx", "xls"])
        
        if uploaded_file is not None:
            if st.button("导入学生名单"):
                success, message = import_students_from_file(uploaded_file)
                if success:
                    st.success(message)
                else:
                    st.error(message)
    
    # 显示现有学生列表
    st.markdown("---")
    st.subheader("现有学生列表")
    
    students = get_students()
    if students:
        # 显示学生列表和删除按钮
        for i in range(0, len(students), 4):  # 每行显示4个学生
            cols = st.columns(4)
            for j in range(4):
                if i+j < len(students):
                    with cols[j]:
                        student_name = students[i+j]
                        col1, col2 = st.columns([3, 1])
                        col1.write(f"{i+j+1}. {student_name}")
                        if col2.button("删除", key=f"del_{student_name}"):
                            if delete_student(student_name):
                                st.success(f"已删除学生：{student_name}")
                                st.rerun()
                            else:
                                st.error(f"删除学生失败：{student_name}")
    else:
        st.info("暂无学生信息，请先添加学生")
    
    # 添加一键清除所有数据功能
    st.markdown("---")
    st.subheader("系统管理")
    
    with st.expander("数据管理区域"):
        st.warning("以下操作将永久删除数据，请谨慎操作！")
        
        # 清除学生名单 - 简化流程，直接一键清除
        st.markdown("### 清除学生名单")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("清除所有学生信息（同时会清除所有德育分记录）")
        
        # 直接一键清除，无需确认
        if col2.button("一键清除所有学生", type="primary", help="此操作不可恢复", key="clear_students"):
            if clear_all_students():
                st.success("已成功清除所有学生名单和相关记录！")
                st.rerun()
            else:
                st.error("清除学生名单失败！")
        
        # 清除德育分记录
        st.markdown("---")
        st.markdown("### 清除德育分记录")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("仅清除所有学生的德育分记录，保留学生名单")
        
        # 直接一键清除，无需确认
        if col2.button("一键清除德育分记录", type="primary", help="此操作不可恢复", key="clear_deductions"):
            if clear_all_deductions():
                st.success("已成功清除所有德育分记录！")
                st.rerun()
            else:
                st.error("清除德育分记录失败！")
        


# 学生德育评分页面
def show_deduction_page():
    st.header("学生德育评分")
    
    students = get_students()
    
    if not students:
        st.warning("暂无学生信息，请先在首页添加学生")
        return
    
    selected_student = st.selectbox("请选择学生", students)
    selected_date = st.date_input("请选择日期", date.today())
    
    # 获取当前学生的当日扣分记录
    record = get_student_daily_deduction(selected_student, selected_date)
    
    with st.form("deduction_form"):
        st.subheader(f"{selected_student} 在 {selected_date} 的德育表现")
        
        late = st.number_input("迟到次数", min_value=0, value=int(record['迟到']), step=1)
        fight = st.number_input("打架次数", min_value=0, value=int(record['打架']), step=1)
        homework = st.number_input("作业未完成次数", min_value=0, value=int(record['作业未完成']), step=1)
        discipline = st.number_input("课堂违纪次数", min_value=0, value=int(record['课堂违纪']), step=1)
        others = st.number_input("其他扣分", min_value=0, value=int(record['其他']), step=1)
        notes = st.text_area("备注", value=record['备注'])
        
        col1, col2, col3 = st.columns(3)
        
        submit = col1.form_submit_button("保存")
        reset = col2.form_submit_button("重置为零")
        
    if submit:
        update_student_daily_deduction(selected_student, selected_date, late, fight, homework, discipline, others, notes)
        st.success("保存成功！")
    
    if reset:
        reset_student_daily_deduction(selected_student, selected_date)
        st.success("已重置当天扣分记录！")
        st.rerun()
    
    # 显示当前学生的德育总分
    total_deduction = get_student_total_deduction(selected_student)
    moral_score = 100 - total_deduction
    
    st.markdown("---")
    st.subheader("德育总分统计")
    
    col1, col2 = st.columns(2)
    col1.metric("总扣分", f"{total_deduction}分")
    col2.metric("德育总分", f"{max(0, moral_score)}分 (满分100分)")
    
    if moral_score < 60:
        st.warning("德育总分低于60分，请加强教育引导")
    elif moral_score < 80:
        st.info("德育总分一般，仍有提升空间")
    else:
        st.success("德育表现良好，请继续保持")

# 学生德育分查询页面
def show_query_page():
    st.header("学生德育分查询")
    
    # 获取所有学生德育分汇总
    summary_df = get_all_students_deductions()
    
    if summary_df.empty:
        st.warning("暂无学生德育分记录")
    else:
        st.dataframe(summary_df, use_container_width=True)
        
        # 导出到Excel
        if st.button("导出到Excel"):
            excel_file = export_to_excel()
            
            with open(excel_file, "rb") as file:
                st.download_button(
                    label="下载Excel文件",
                    data=file,
                    file_name=excel_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            st.success(f"已成功导出数据到 {excel_file}")

if __name__ == "__main__":
    main()
