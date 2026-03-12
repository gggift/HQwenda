"""
Batch test runner for HQwenda Q&A system.
Usage: python run_test.py <round_dir> <start> <end>
"""
import json
import sys
import time
import urllib.request

API_URL = "http://8.147.71.40:8000/api/chat"
TIMEOUT = 180

QUESTIONS = [
    # 一、个股行情（1-15）
    "贵州茅台今天的收盘价是多少？",
    "宁德时代最近5个交易日的涨跌幅分别是多少？",
    "中国平安最近一个月的最高价和最低价？",
    "比亚迪的周K线数据（最近4周）？",
    "招商银行今天的成交额是多少亿？",
    "今天涨停的股票有多少只？跌停的有多少只？",
    "今天全市场上涨和下跌的股票各有多少只？",
    "隆基绿能最近20个交易日的日均成交额？",
    "中芯国际今天的开盘价、最高价、最低价、收盘价？",
    "全市场市值前十的股票是哪些？",
    "今天换手率最高的前10只股票？",
    "今天股息率最高的前10只股票？",
    "工商银行最近一个月的月K线数据？",
    "贵州茅台现在的实时行情？",
    "今天涨幅超过5%的股票有多少只？",
    # 二、指数行情（16-30）
    "上证指数今天收盘多少点？涨跌幅多少？",
    "深证成指最近10个交易日的走势？",
    "创业板指今天的成交额是多少？",
    "沪深300指数最近一周表现如何？",
    "上证50指数的成分股权重前10名？",
    "沪深300成分股中今天上涨和下跌的各有多少只？",
    "过去10年，上证指数收盘高于4000点的交易日有多少天？",
    "上证指数目前处于过去一年的历史分位数是多少？",
    "中证500指数今天的涨跌幅？",
    "中证1000指数最近20个交易日的走势？",
    "科创50指数今天的表现？",
    "沪深300今天涨跌幅贡献最大的前5只股票？",
    "上证指数过去一年的最高点和最低点分别是多少？",
    "上证指数成交额处于过去一年的历史分位数是多少？",
    "过去5年上证指数收盘低于3000点有多少天？",
    # 三、境外指数（31-35）
    "昨天美股三大指数的表现如何？",
    "恒生指数最近5个交易日的走势？",
    "日经225指数昨天收盘多少点？",
    "标普500最近一个月的涨跌幅？",
    "德国DAX指数最近10个交易日的走势？",
    # 四、申万行业（36-50）
    "今天申万一级行业涨幅排名？",
    "今天申万一级行业跌幅前5是哪些？",
    "煤炭行业指数最近一个月的走势？",
    "银行行业今天的PE和PB是多少？",
    "申万一级行业中PE最低的前5个行业？",
    "申万一级行业中PB最低的前5个行业？",
    "电子行业指数最近一周的涨跌幅？",
    "今天申万一级行业对上证指数的贡献点数排名？",
    "哪个一级行业今天对上证指数拖累最大？",
    "医药生物行业今天的成交额是多少？",
    "今天涨幅最大的申万二级行业是哪个？",
    "食品饮料行业最近20个交易日的走势？",
    "非银金融行业今天的涨跌幅？",
    "申万一级行业中今天成交额最大的前5个？",
    "汽车行业指数最近3个月的表现？",
    # 五、基本面与估值（51-62）
    "贵州茅台的市盈率(PE)和市净率(PB)是多少？",
    "宁德时代的总市值和流通市值？",
    "招商银行最近一期的ROE是多少？",
    "中国平安的每股收益(EPS)是多少？",
    "全市场PE最低的前10只股票？",
    "今天市净率低于1的股票有多少只？",
    "比亚迪的市值在全市场排名第几？",
    "贵州茅台的PE处于过去一年的历史分位数？",
    "宁德时代的PB处于过去一年的历史分位数？",
    "工商银行的股息率是多少？",
    "中国神华的毛利率和净利率？",
    "隆基绿能的PS(市销率)是多少？",
    # 六、技术分析（63-72）
    "上证指数的5日、10日、20日、60日均线分别是多少？",
    "贵州茅台当前是否出现均线金叉或死叉？",
    "沪深300指数当前收盘价偏离250日均线多少？",
    "创业板指的MA5和MA10的关系？是否金叉？",
    "宁德时代的20日均线和60日均线的乖离率？",
    "招商银行目前站上了哪些均线？",
    "比亚迪的120日均线是多少？当前价格在其上方还是下方？",
    "上证指数的250日均线（年线）是多少？",
    "中国平安最近有没有技术信号（金叉/死叉）？",
    "深证成指当前价格偏离60日均线多少百分比？",
    # 七、资金流向（73-80）
    "今天北向资金净流入还是净流出？金额多少？",
    "最近5个交易日北向资金的流入流出情况？",
    "沪股通和深股通今天分别净流入多少？",
    "贵州茅台今天的主力资金净流入还是净流出？",
    "宁德时代今天的超大单和大单买卖情况？",
    "最近一周北向资金累计净流入多少？",
    "招商银行今天的资金流向（大单/中单/小单）？",
    "南向资金今天的流入流出情况？",
    # 八、宏观与衍生品（81-90）
    "今天美元兑人民币汇率是多少？",
    "最近一周美元兑人民币汇率走势？",
    "今天SHIBOR隔夜利率是多少？",
    "中国10年期国债收益率是多少？",
    "美国10年期国债收益率是多少？",
    "中美10年期国债利差是多少？",
    "黄金期货今天的价格？",
    "原油期货最近5个交易日的走势？",
    "沪铜期货今天的收盘价？",
    "SHIBOR一周利率最近一个月的走势？",
    # 九、综合分析（91-100）
    "今天A股市场整体表现如何？请综合分析。",
    "从技术分析角度看当前上证指数处于什么位置？",
    "今天市场的量能结构如何？与昨天相比有何变化？",
    "今天领涨和领跌的行业分别是什么？原因可能是什么？",
    "当前A股市场估值处于历史什么水平？",
    "今天大盘股和小盘股的表现差异？",
    "上证指数和创业板指今天的走势分化情况？",
    "今天成交额最大的前5只个股是哪些？",
    "全市场今天平均涨跌幅是多少？",
    "今天的市场有哪些值得关注的异动？",
]


def test_question(idx, question):
    """Send one question, return (idx, question, reply, elapsed)."""
    session_id = f"qa-test-{idx}"
    payload = json.dumps({"session_id": session_id, "message": question}).encode()
    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read().decode())
            reply = data.get("reply", "(empty)")
    except Exception as e:
        reply = f"[ERROR] {e}"
    elapsed = round(time.time() - t0, 1)
    return idx, question, reply, elapsed


def main():
    if len(sys.argv) < 4:
        print("Usage: python run_test.py <round_dir> <start> <end>")
        print("  e.g.: python run_test.py round1 1 15")
        sys.exit(1)

    round_dir = sys.argv[1]
    start = int(sys.argv[2])
    end = int(sys.argv[3])

    results = []
    for i in range(start - 1, min(end, len(QUESTIONS))):
        q = QUESTIONS[i]
        num = i + 1
        print(f"[{num}/{end}] {q[:40]}...", flush=True)
        idx, question, reply, elapsed = test_question(num, q)
        results.append((idx, question, reply, elapsed))
        print(f"  -> {elapsed}s, {len(reply)} chars", flush=True)

    # Write markdown report
    fname = f"{round_dir}/Q{start:03d}-Q{end:03d}.md"
    with open(fname, "w") as f:
        f.write(f"# 行情问答测试 Q{start}-Q{end}\n\n")
        f.write(f"测试时间：{time.strftime('%Y-%m-%d %H:%M')}\n\n")
        for idx, question, reply, elapsed in results:
            f.write(f"---\n\n## Q{idx}. {question}\n\n")
            f.write(f"**耗时**：{elapsed}s\n\n")
            f.write(f"**回答**：\n\n{reply}\n\n")
    print(f"\nSaved to {fname}")


if __name__ == "__main__":
    main()
