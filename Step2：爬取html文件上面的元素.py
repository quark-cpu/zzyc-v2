'''
使用方法
1、修改路径，运行五次文档，导入考试宝。
2、导出excel文件，导入包
3、一些想说的话:为什么不把第一步和第二部放在一起自动化写呢？因为通过两次退出快速提交问卷和保存问卷的过程不能自动化。
'''
from bs4 import BeautifulSoup
import re

file_route = r'C:\Users\Lenovo\Desktop\党建知识竞赛'  # 修改到你的路径，不需要后缀名
def process_html_to_final(file1=file_route):
    """直接处理HTML到最终结果，不生成中间文件"""
    try:
        # 1. 读取并解析HTML
        with open(file1 + '.html', 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        all_elements = soup.find_all(True)
        
        # 提取所有文本内容
        extracted_text = ""
        for element in all_elements:
            tag_name = element.name
            text = element.get_text()
            extracted_text += f"标签名: {tag_name}\n文本内容: {text}\n\n"
        
        # 2. 提取有用部分（从"*1"到"保存报告 收起答题解析"）
        start_idx = extracted_text.find("*1")
        end_idx = extracted_text.find("保存报告 收起答题解析", start_idx)
        
        if start_idx == -1 or end_idx == -1:
            print("未找到所需的标记")
            return False
        
        content = extracted_text[start_idx:end_idx + len("保存报告 收起答题解析")]

        # 3.处理选项
        def process_ABC(content):
            content = re.sub('对', 'A、对\n', content)
            content = re.sub('错', 'B、错', content)
            content = re.sub('A', 'A', content)
            content = re.sub('B', '\nB', content)
            content = re.sub('C', '\nC', content)
            content = re.sub('D', '\nD', content)
            return content
        def process_multiple_choice_ABC(content):
            content = re.sub('A、', 'A、', content)        #print('A'=='A')#呵呵，这是个什么东西,居然返回false，看来是多选题前面的符号不太一样
            content = re.sub('B、', '\nB、', content)
            content = re.sub('C、', '\nC、', content)
            content = re.sub('D、', '\nD、', content)
            content = re.sub('E、', '\nE、', content)
            content = re.sub('F、', '\nF、', content)
            content = re.sub('G、', '\nG、', content)
            content = re.sub('H、', '\nH、', content)
            content = re.sub('I、', '\nI、', content)
            return content

        # 4. 处理答案
        def process_all_answers(text):
            lines = text.split('\n')
            processed_lines = []
            
            for line in lines:
                # 处理答案行
                if line.strip().startswith('答案:') or line.strip().startswith('答案：'):
                    answer_part = line.replace('答案:', '').replace('答案：', '').strip()
                    
                    # 处理判断题
                    if '对' in answer_part:
                        processed_line = "答案: A"
                    elif '错' in answer_part:
                        processed_line = "答案: B"
                    # 处理多选题（包含┋分隔符的）
                    elif '┋' in answer_part:
                        # 提取所有字母并排序
                        matches = re.findall(r'[A-Z]', answer_part)
                        if matches:
                            unique_letters = sorted(set(matches))
                            option_letters = ''.join(unique_letters)
                            processed_line = f"答案: {option_letters}"
                        else:
                            processed_line = line
                    # 处理单选题（直接提取第一个字母）
                    else:
                        match = re.search(r'[A-D]', answer_part)
                        if match:
                            processed_line = f"答案: {match.group()}"
                        else:
                            processed_line = line
                else:
                    processed_line = line
                
                processed_lines.append(processed_line)
            
            return '\n'.join(processed_lines)
        def process_multiple_choice_answers(text):
            lines = text.split('\n')
            processed_lines = []
            
            for line in lines:
                if line.strip().startswith('答案：'):
                    answer_part = line.replace('答案：', '').strip()
                    matches = re.findall(r'[A-Z]', answer_part)
                    if matches:
                        unique_letters = sorted(set(matches))
                        option_letters = ''.join(unique_letters)
                        processed_line = f"答案：{option_letters}"
                        processed_lines.append(processed_line)
                    else:
                        processed_lines.append(line)
                else:
                    processed_lines.append(line)
            
            return '\n'.join(processed_lines)
        
        content = re.sub(r'分值[1-9]分|回答错误\+0分', '\n', content)
        content=  re.sub(r'[、\.]', '、', content)
        content=  re.sub(r'：', ':', content)
        content=  re.sub(r'\*(\d+)、', r'\n\1、', content)
        content= process_ABC(content)
        content= process_multiple_choice_ABC(content)
        content = re.sub('正确答案:', '答案:', content)
        content = re.sub('答案:对', '答案:A', content)
        content = re.sub('答案:错', '答案:B', content)
        content= process_multiple_choice_answers(content)
        content = process_all_answers(content)  # 统一处理所有答案格式
        # 5. 直接保存到最终文件
        with open(file1 + '.txt', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"处理完成！直接保存到: {file1}.txt")
        return True
        
    except Exception as e:
        print(f"错误: {e}")
        return False
    
def auto_run(route,times=5):
    for i in range(times):
        new_route=route+str(i)
        process_html_to_final(new_route)


# 直接运行处理函数
#process_html_to_final()
#auto_run(file_route,times=2)
