import os
import pandas as pd
import akshare as ak

def fetch_csi_930955_list(limit_days: int = 20) -> list:
    """
    全量/近端抓取中证红利低波 100 指数历史列表 (930955)
    直接调用 AkShare 官方中证指数接口，完全摒弃本地 Excel 依赖。
    返回符合前端直接替换的 list 格式，且按日期升序(旧->新)排列。
    """
    try:
        print("🚀 开始通过 AkShare 接口抓取中证红利低波 100 估值指标...")
        
        # 🎯 核心：直接调用中证指数历史指标接口
        df_index = ak.stock_zh_index_value_csindex(symbol="930955")
        
        if df_index.empty:
            print("⚠️ 接口返回的红利低波指数数据为空！")
            return []

        # 🔄 清洗与规范化处理
        # 1. 确保日期列为字符串或 datetime，方便统一格式化
        df_index["日期"] = pd.to_datetime(df_index["日期"])
        
        # 2. 按日期降序排列（最新在前），以便精准截取最近的 N 天数据
        df_index = df_index.sort_values(by="日期", ascending=False)
        
        # 3. 截取最近的指定天数
        df_recent = df_index.head(limit_days)

        cleaned_list = []
        for _, row in df_recent.iterrows():
            # 将日期转换为整型数字，例如 2026-06-20 -> 20260620
            date_int = int(row["日期"].strftime("%Y%m%d"))
            
            # 兼容性处理：提取股息率1和股息率2，并转化为标准 float
            dp1 = float(row.get("股息率1", 0.0))
            dp2 = float(row.get("股息率2", 0.0))

            cleaned_list.append({
                "日期Date": date_int,
                "股息率1（总股本）D/P1": dp1,
                "股息率2（计算用股本）D/P2": dp2
            })

        # 🎯 灵魂反转：截取出来是最新的在前，反转后变成“由旧到新”升序排列，完美贴合 ECharts
        cleaned_list.reverse()
        
        print(f"✅ 红利低波 100 (去Excel化) 抓取成功，共汇编 {len(cleaned_list)} 个最新历史交易日 List。")
        return cleaned_list

    except Exception as e:
        print(f"❌ 抓取中证红利低波 100 指数历史数据失败: {e}")
        return []

# 💡 留给你的“单兵训练”调试接口
# 无论你在根目录下敲 `uv run fetcher/csi_930955_indicator.py` 
# 还是 cd 到 fetchers 目录敲 `uv run csi_930955_indicator.py`，因为有了上面的路径锁，都能完美独立运行调试！
if __name__ == "__main__":
    res = fetch_csi_930955_list(limit_days=20) # 测试抓取最近 20 天
    print("\n[本地调试输出样例（前两项）]:")
    import json
    print(json.dumps(res[:2], ensure_ascii=False, indent=2))