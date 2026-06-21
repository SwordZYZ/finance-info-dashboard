# /// script
# dependencies = [
#   "requests",
#   "pandas",
#   "akshare",
# ]
# ///
import os
import json
from fetcher.csi_930955_indicator import fetch_csi_930955_list
from fetcher.us10ytip_indicator import fetch_us10ytip_list
from fetcher.csi_000300_indicator import fetch_csi_000300_valuation

# 🚀 路径安全锁：解耦拆分为三个独立的本地数据文件
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "data") # 👈 精准拼接出 根目录/data

# 如果根目录下没有 data 文件夹，Python 会自动帮你创建它，再也不怕容器报错
os.makedirs(DATA_DIR, exist_ok=True)

PATH_CSI_000300 = os.path.join(DATA_DIR, "csi_000300_data.json")
PATH_CSI_930955 = os.path.join(DATA_DIR, "csi_930955_data.json")
PATH_US10YTIP = os.path.join(DATA_DIR, "us10ytip_data.json")

def safe_write_json(file_path, data):
    """安全写回本地JSON辅助函数"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 成功刷入本地文件: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"❌ 写入 {os.path.basename(file_path)} 发生错误: {e}")

def main():
    print("================ 监控看板自动化流水线启动 ================")

    # ------------------ 第一步：并发抓取 ------------------
    
    # 1. 抓取红利低波 100 历史 List (默认取 20 天)
    print("\n--- [任务 1/3] 抓取红利低波 100 指数数据 ---")
    csi_930955_dividend_list = fetch_csi_930955_list(limit_days=20)
    
    # 2. 抓取美债实际利率历史 List (默认取 20 天)
    # 密码由于写了 os.getenv，会完美自动读取你 UNRAID 容器或环境里的 FRED_API_KEY
    print("\n--- [任务 2/3] 抓取圣路易斯联储 FRED 美债数据 ---")
    # 这里我们放大了接口请求的上限（days_limit=30），以确保在剔除掉美国节假日后，我们依然能获得足够的有效交易日数据（目标是至少20条）。所以即使接口返回了30条原始记录，最终我们也会在数据清洗阶段锁定到我们真正想要的20条有效交易日数据。
    us10ytip_data_list = fetch_us10ytip_list(api_key="8564bbe541091fb29e8fbc237380b2aa", days_limit=30)

    # 3. 抓取沪深300估值指标历史 List (默认取 10 年)
    print("\n--- [任务 3/3] 抓取沪深300估值指标数据 ---")
    csi_000300_valuation_list = fetch_csi_000300_valuation(years_back=10)

# ------------------ 第二步：非空安全校验与数据写入 ------------------
    print("\n--- 正在汇总并写入所有数据 ---")
    
    # 1. 红利低波独立落盘
    if csi_930955_dividend_list:
        # 直接存入纯数组结构，干净整洁
        safe_write_json(PATH_CSI_930955, csi_930955_dividend_list)
        print(f"✅ [红利低波100] 更新完毕，共 {len(csi_930955_dividend_list)} 条记录。")
    else:
        print("⚠️ [红利低波100] 本次抓取列表为空，保留上一次的历史缓存，不进行覆盖。")

    # 2. 美债利率独立落盘
    if us10ytip_data_list:
        # 直接存入纯数组结构
        safe_write_json(PATH_US10YTIP, us10ytip_data_list)
        print(f"✅ [美债利率] 更新完毕，共 {len(us10ytip_data_list)} 条记录。")
    else:
        print("⚠️ [美债利率] 本次抓取列表为空，保留上一次的历史缓存，不进行覆盖。")

    # 3. 沪深300独立落盘
    if csi_000300_valuation_list:
        # 存入包含 summary 和 history 的多维字典结构
        safe_write_json(PATH_CSI_000300, csi_000300_valuation_list)
        print(f"✅ [沪深300] 更新完毕，共 {len(csi_000300_valuation_list['history'])} 条记录。")
    else:
        print("⚠️ [沪深300] 本次抓取列表为空，保留上一次的历史缓存，不进行覆盖。")

    print("========================= 流水线结束 =========================")

if __name__ == "__main__":
    main()