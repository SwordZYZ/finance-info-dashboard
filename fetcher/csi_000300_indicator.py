import os
import datetime
import pandas as pd
import akshare as ak

def calculate_percentile(current_val: float, history_series: pd.Series) -> float:
    """
    数学核心：计算当前值在历史序列中的百分位
    """
    if history_series.empty:
        return 0.0
    less_than_count = (history_series < current_val).sum()
    percentile = (less_than_count / len(history_series)) * 100
    return round(percentile, 2)

def fetch_csi_000300_valuation(years_back: int = 10) -> dict:
    """
    【自愈重构版】
    1. df_hist 拥有完整的 10 年滚动市盈率 (PE TTM)。
    2. df_value 通常仅提供最近 1-2 年的市盈率2/股息率2。
    3. 核心计算直接基于 10 年原始主表，防止由于内连接(Inner Join)导致历史缩水。
    """
    print(f"🚀 [任务: 沪深300] 正在通过 AkShare 调取中证官网 {years_back} 年历史数据...")
    
    today = datetime.date.today()
    start_date_str = (today - datetime.timedelta(days=years_back * 365)).strftime("%Y%m%d")
    end_date_str = today.strftime("%Y%m%d")
    
    try:
        # 📢 维度一：拉取大盘经典行情接口（天然自带 10 年全量 PE TTM，极其稳定）
        df_hist = ak.stock_zh_index_hist_csindex(
            symbol="000300", start_date=start_date_str, end_date=end_date_str
        )
        
        # 📢 维度二：拉取估值指标接口（中证网关限制，通常只下发最近 1-2 年数据）
        df_value_raw = ak.stock_zh_index_value_csindex(symbol="000300")
        
        if df_hist.empty:
            print("❌ 错误：中证官网 K 线历史接口返回空数据，无法计算百分位。")
            return {}

        # 数据清洗，格式化对齐时间戳
        df_hist['date_clean'] = pd.to_datetime(df_hist['日期']).dt.strftime('%Y%m%d')
        df_hist = df_hist.sort_values(by='date_clean').reset_index(drop=True)
        
        if not df_value_raw.empty:
            df_value_raw['date_clean'] = pd.to_datetime(df_value_raw['日期']).dt.strftime('%Y%m%d')
            df_value = df_value_raw[(df_value_raw['date_clean'] >= start_date_str) & 
                                    (df_value_raw['date_clean'] <= end_date_str)].copy()
        else:
            df_value = pd.DataFrame(columns=['date_clean', '市盈率2', '股息率2'])

        # 🎯 【核心改动 1】直接在拥有完整 10 年厚度的 df_hist 上进行多周期百分位切片计算
        # 完美避开合并造成的脱水瓶颈
        pe_ttm_series = df_hist['滚动市盈率'].astype(float)
        current_pe_ttm = float(pe_ttm_series.iloc[-1])
        
        # A 股一年约 242 个交易日
        window_sizes = {
            "1年分位_1y": 1 * 242,
            "3年分位_3y": 3 * 242,
            "5年分位_5y": 5 * 242,
            "10年分位_10y": 10 * 242
        }
        
        percentiles = {}
        for label, size in window_sizes.items():
            # 使用 tail(size) 截取各自真实的周期窗口数据
            history_window = pe_ttm_series.tail(size)
            percentiles[label] = calculate_percentile(current_pe_ttm, history_window)
            # 调试日志：确认每个窗口切出的真实天数
            # print(f"DEBUG: 窗口 {label} 参与计算的实际历史天数: {len(history_window)}")

        # 🎯 【核心改动 2】改用 Left Join (左连接)，以 10 年行情为主表，无损保留长线数据
        df_merged = pd.merge(df_hist, df_value, on='date_clean', how='left', suffixes=('_hist', '_val'))
        df_merged = df_merged.sort_values(by='date_clean').reset_index(drop=True)

        # 提取最新单日截面快照
        latest_row = df_merged.iloc[-1]
        latest_date = int(latest_row['date_clean'])
        current_close = float(latest_row['收盘'])
        
        # 兼容处理历史过旧时可能为 NaN 的扩展估值指标
        current_pe_lyr2 = float(latest_row['市盈率2']) if pd.notna(latest_row['市盈率2']) else None
        current_dp2 = float(latest_row['股息率2']) if pd.notna(latest_row['股息率2']) else None

        # 汇编全量历史列表
        history_list = []
        for _, row in df_merged.iterrows():
            history_list.append({
                "date": int(row['date_clean']),
                "close": float(row['收盘']),
                "pe_ttm": float(row['滚动市盈率']),
                "pe_lyr2": float(row['市盈率2']) if pd.notna(row['市盈率2']) else None,
                "dp2": float(row['股息率2']) if pd.notna(row['股息率2']) else None
            })

        print(f"=====================================")
        print(f"📊 资产名称: {latest_row['指数中文简称'] if '指数中文简称' in latest_row else '沪深300'} (000300)")
        print(f"📅 最新日期: {latest_date} | 收盘点位: {current_close}")
        print(f"🔥 当前滚动市盈率 (PE TTM): {current_pe_ttm}")
        print(f"📈 动态估值百分位矩阵 (✅ 10年跨度修正成功):")
        print(f"   ├─ 近 1 年分位: {percentiles['1年分位_1y']}%")
        print(f"   ├─ 近 3 年分位: {percentiles['3年分位_3y']}%")
        print(f"   ├─ 近 5 年分位: {percentiles['5年分位_5y']}%")
        print(f"   └─ 近 10年分位: {percentiles['10年分位_10y']}%")
        print(f"💎 计算股本市盈率2: {current_pe_lyr2} | 股息率2: {current_dp2}%")
        print(f"=====================================")

        return {
            "summary": {
                "update_date": latest_date,
                "close": current_close,
                "current_pe_ttm": current_pe_ttm,
                "current_pe_lyr2": current_pe_lyr2,
                "current_dp2": current_dp2,
                "percentile_1y": percentiles['1年分位_1y'],
                "percentile_3y": percentiles['3年分位_3y'],
                "percentile_5y": percentiles['5年分位_5y'],
                "percentile_10y": percentiles['10年分位_10y']
            },
            "history": history_list
        }
        
    except Exception as e:
        print(f"❌ 抓取或解析沪深300长线指标发生致命错误: {e}")
        return {}

if __name__ == "__main__":
    fetch_csi_000300_valuation(years_back=10)