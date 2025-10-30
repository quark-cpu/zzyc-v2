import re
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
import time
import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog
from selenium.webdriver.edge.service import Service
def extract_questions_from_web(url):
    custom_user_agent = "Mozilla/5.0 (Linux; Android 10; CDY-AN90 Build/HUAWEICDY-AN90; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.62 XWEB/2691 MMWEBSDK/200801 Mobile Safari/537.36 MMWEBID/4006 MicroMessenger/7.0.18.1740(0x2700123B) Process/toolsmp WeChat/arm64 NetType/4G Language/zh_CN ABI/arm64"

    options = webdriver.EdgeOptions()
    options.add_argument(f'--user-agent={custom_user_agent}')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("detach", True)

    # 新增：选择driver路径
    driver_path = filedialog.askopenfilename(title="选择driver路径", filetypes=[("Driver Files", "*.exe;*.msi")])
    if not driver_path:
        print("未选择driver路径，程序将退出。")
        return
    # 使用Service类来指定driver的路径
    service = Service(executable_path=driver_path)
    driver = webdriver.Edge(service=service, options=options)  # 创建浏览器实例
    driver.get(url)
    time.sleep(5)  # 等待网页加载完成

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    divs = soup.find_all('div', class_='topichtml')
    for div in divs:
        for element in div.find_all('span', class_='qtypetip'):
            element.decompose()

    questions = [div.get_text(strip=True) for div in divs]

    # 排除特定的文本
    exclude_texts = ["教学层次：", "您的年级：", "您的专业：", "您的区队：", "您的姓名：", "您的学号："]
    filtered_questions = [q for q in questions if all(text not in q for text in exclude_texts)]

    return filtered_questions

def remove_parentheses_content(text):
    # 去除英文括号
    text = re.sub(r'\(.*?\)', '', text)
    # 去除中文括号
    text = re.sub(r'（.*?）', '', text)
    return text.strip()

def clean_text(text):
    # 去除标点符号
    text = re.sub(r'[^\w\s]', '', text)
    # 去除空格
    text = re.sub(r'\s+', '', text)
    # 去除换行符
    text = text.replace('\n', '')
    return text



def load_questions_and_answers_from_excel(excel_file):
    df = pd.read_excel(excel_file)
    if '题干（必填）' in df.columns and '正确答案（必填）' in df.columns:
        qa_dict = dict(zip(df['题干（必填）'], df['正确答案（必填）']))
        return qa_dict
    else:
        print("Excel文件中未找到 '题干（必填）' 或 '正确答案（必填）' 列。")
        return {}

def match_questions(web_questions, qa_dict):
    results = []
    cleaned_qa_dict = {clean_text(remove_parentheses_content(question)): answer for question, answer in qa_dict.items()}

    for question in web_questions:
        cleaned_question = clean_text(remove_parentheses_content(question))
        if cleaned_question in cleaned_qa_dict:
            row_number = list(cleaned_qa_dict.keys()).index(cleaned_question) + 1
            correct_answer = cleaned_qa_dict[cleaned_question]
            results.append(f"网页题目: {question} - 对应行数: {row_number} - 正确答案: {correct_answer}")
        else:
            results.append(f"网页题目: {question} - 未找到对应行数和答案")

    return results

def display_results(results):
    window = tk.Tk()
    window.title("问卷结果输出")

    text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=100, height=40)
    text_area.pack(padx=10, pady=10)

    # 设置标签以改变字体颜色
    text_area.tag_configure("red", foreground="red", font=("Arial", 12, "bold"))
    text_area.tag_configure("green", foreground="green", font=("Arial", 12, "bold"))
    text_area.tag_configure("blue", foreground="blue", font=("Arial", 12, "bold"))

    # 插入结果
    not_found_count = 0
    for idx, result in enumerate(results):
        if idx > 0 and idx % 5 == 0:  # 每五道题插入一条横线
            text_area.insert(tk.END, "------------------------------------------------\n")

        if "网页题目: " in result and "未找到对应行数和答案" in result:
            text_area.insert(tk.END, result + "\n", "blue")  # 未找到为蓝色
            not_found_count += 1
        else:
            question_part, answer_part = result.split(" - 正确答案: ")
            text_area.insert(tk.END, question_part + " - 正确答案: \n", "green")  # 题目为绿色
            text_area.insert(tk.END, answer_part + "\n", "red")  # 答案为红色

    text_area.config(state=tk.DISABLED)

    # 在窗口底部显示未找到题目的个数
    not_found_label = tk.Label(window, text=f"未找到题目的个数: {not_found_count}", font=("Arial", 12, "bold"))
    not_found_label.pack(pady=10)

    window.mainloop()

def select_excel_file():
    # 弹出文件选择对话框
    excel_file_path = filedialog.askopenfilename(title="选择Excel文件", filetypes=[("Excel Files", "*.xlsx;*.xls")])
    return excel_file_path

def get_url_and_process():
    url = url_entry.get()
    if not url:
        print("未输入问卷网址，程序将退出。")
        return

    excel_file = select_excel_file()
    if not excel_file:
        print("未选择Excel文件，程序将退出。")
        return

    web_questions = extract_questions_from_web(url)
    qa_dict = load_questions_and_answers_from_excel(excel_file)
    results = match_questions(web_questions, qa_dict)
    display_results(results)

if __name__ == "__main__":
    window = tk.Tk()
    window.title("问卷星题目和答案提取器")

    tk.Label(window, text="请输入问卷网址:").pack(padx=10, pady=5)
    url_entry = tk.Entry(window, width=50)
    url_entry.pack(padx=10, pady=5)

    start_button = tk.Button(window, text="开始提取", command=get_url_and_process)
    start_button.pack(padx=10, pady=10)

    window.mainloop()
