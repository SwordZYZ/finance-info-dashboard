import os
import requests

def fetch_us10ytip_list(api_key: str = None, days_limit: int = 30) -> list:
    """
    全量抓取美债实际利率历史列表 (US10YTIP)
    返回符合前端直接替换的 list 格式，且按日期升序(旧->新)排列
    """
    final_api_key = api_key or os.getenv("FRED_API_KEY")
    if not final_api_key:
        print("❌ 错误: 未检测到 FRED_API_KEY")
        return []

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": "DFII10",
        "api_key": final_api_key,
        "file_type": "json",
        "sort_order": "desc",       # 🎯 关键修改：升序排列，让最新的数据落在数组最后，契合 ECharts
        "limit": days_limit        # 🎯 放大 limit，一口气拉下最近 30 条原始记录
    }

    proxies = {
        "http": os.getenv("HTTP_PROXY") or os.getenv("http_proxy"),
        "https": os.getenv("HTTPS_PROXY") or os.getenv("https_proxy"),
    }
    proxies = {k: v for k, v in proxies.items() if v}

    try:
        print(f"🚀 正在获取最近 {days_limit} 条美债实际利率数据...")
        response = requests.get(url, params=params, proxies=proxies, timeout=15)
        response.raise_for_status()
        
        observations = response.json().get("observations", [])
        
        # 🎯 核心重隔：将所有有效的数据清洗后装进列表
        cleaned_list = []
        for node in observations:
            raw_date = node["date"]
            raw_value = node["value"]
            
            # 1. 自动过滤掉美国节假日的无效占位符（此时由于放宽了上限，扔掉后依然管够）
            if raw_value == ".":
                continue
                
            cleaned_list.append({
                "日期Date": int(raw_date.replace("-", "")), # 对齐键名规范
                "美债利率Rate": float(raw_value)
            })
            
            # 2. 🎯 绝妙截断锁：一旦我们在循环中收集满了我们真正想要的有效交易日数（如20天），就立刻收工
            if len(cleaned_list) >= 20:  # 🎯 这里的20是我们想要的最终有效交易日数量，不是接口请求的原始记录数量
                break
            
        cleaned_list.reverse() # 🎯 反转列表，让日期从旧到新排列，契合 ECharts

        print(f"✅ 抓取成功，排除节假日后，共获得 {len(cleaned_list)} 个足额有效交易日数据。")
        return cleaned_list

    except Exception as e:
        print(f"❌ 抓取 FRED 历史数据失败: {e}")
        return []

# 💡 留下一段单兵训练（Mock）接口：
# 以后你调试这个脚本，不需要运行整个项目，直接在命令行敲：uv run fetcher/us10ytip_indicator.py
if __name__ == "__main__":
    res = fetch_us10ytip_list(api_key="8564bbe541091fb29e8fbc237380b2aa", days_limit=30) # 测试抓取最近 20 天
    print("本地调试输出 List 示例（前两项）:", res[:2] if res else "无数据")