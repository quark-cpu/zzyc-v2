#一个简单的问题:一个m道题的题库,每次出100题,求爬虫几次之后大概能算全部爬取完，alpha=0.001即99.9%的概率能全部爬取完
#deepseek一下
import math

def calculate_crawl_sessions(m, alpha=0.001):
    """
    计算需要多少次爬取才能以概率(1-alpha)覆盖全部题库
    
    参数:
    m: 题库总题数
    alpha: 显著性水平，默认0.001
    
    返回:
    sessions: 需要的爬取次数
    """
    # 每次抽取100题，单次抽取中某道题被抽中的概率
    p_single_selection = 100 / m
    
    # 单次抽取中某道题未被抽中的概率
    p_not_selected = 1 - p_single_selection
    
    # 计算需要多少次抽取才能使得至少有一道题从未被抽中的概率小于alpha
    # P(至少有一题从未被抽中) <= alpha
    # 使用Union Bound: P(至少有一题从未被抽中) <= m * (p_not_selected)^k
    
    # 解不等式: m * (p_not_selected)^k <= alpha
    # (p_not_selected)^k <= alpha/m
    # k * log(p_not_selected) <= log(alpha/m)
    # k >= log(alpha/m) / log(p_not_selected)
    
    if p_not_selected <= 0:
        return 1  # 如果每次都能覆盖全部题目
    
    sessions = math.log(alpha / m) / math.log(p_not_selected)
    return math.ceil(sessions)

def main():
    # 测试不同规模的题库 - 修改为指定的值
    test_cases = [100, 150, 200, 220, 250, 275, 300, 350, 400]
    alpha = 0.001
    
    print("题库规模与所需爬取次数分析 (alpha=0.001)")
    print("=" * 60)
    print(f"{'题库大小(m)':<12} {'每次抽题数':<12} {'所需次数':<12} {'备注':<20}")
    print("-" * 60)
    
    results = []
    for m in test_cases:
        sessions = calculate_crawl_sessions(m, alpha)
        
        if m <= 100:
            remark = "一次即可全覆盖"
        elif sessions > 10000:
            remark = "需要极多次"
        else:
            remark = f"约需{sessions}次"
        
        results.append((m, sessions))
        print(f"{m:<12} {100:<12} {sessions:<12} {remark:<20}")
    
    # 显示关键数据点
    print("\n" + "=" * 60)
    print("分析结果汇总")
    print("=" * 60)
    
    info_text = f"分析结果汇总 (α={alpha}):\n\n"
    for m, sessions in results:
        info_text += f"题库大小: {m}\n"
        info_text += f"所需次数: {sessions}\n"
        info_text += f"覆盖率: ≥{1-alpha:.3f}\n\n"
    
    print(info_text)
    
    # 交互式查询
    print("\n" + "=" * 60)
    print("交互式查询 (alpha=0.001)")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\n请输入题库大小m (输入q退出): ")
            if user_input.lower() == 'q':
                break
            
            m = int(user_input)
            if m < 100:
                print("题库大小至少为100（因为每次抽100题）")
                continue
                
            sessions = calculate_crawl_sessions(m, alpha)
            print(f"题库大小: {m}")
            print(f"每次抽题: 100")
            print(f"达到全覆盖概率 ≥ {1-alpha:.3f} 所需次数: {sessions}")
            
            # 额外信息
            if sessions == 1:
                print("说明: 一次抽取即可基本覆盖全部题目")
            elif sessions > 10000:
                print("说明: 需要极多次抽取，考虑优化策略")
            else:
                # 计算实际概率
                p_not_selected = 1 - 100/m
                expected_missing = m * (p_not_selected ** sessions)
                actual_prob = 1 - math.exp(-expected_missing)
                print(f"实际全覆盖概率估计: {actual_prob:.6f}")
                
                # 显示达到目标概率的详细过程
                print("\n达到目标概率的过程:")
                check_points = [max(1, sessions//4), max(1, sessions//2), max(1, sessions*3//4), sessions]
                for k in check_points:
                    p_missing = (1 - 100/m) ** k
                    expected_missing = m * p_missing
                    coverage_prob = 1 - math.exp(-expected_missing)
                    print(f"  爬取 {k} 次后，全覆盖概率约为: {coverage_prob:.4f}")
                
        except ValueError:
            print("请输入有效的数字！")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()