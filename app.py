import streamlit as st
import akshare as ak
import pandas as pd
import time

# 页面配置
st.set_page_config(page_title="A股全维度分析助手", layout="wide")

def get_stock_info(symbol):
    """获取股票基本信息和代码纠错"""
    try:
        df = ak.stock_zh_a_spot_em()
        # 尝试匹配代码或名称
        target = df[(df['代码'] == symbol) | (df['名称'] == symbol)]
        if target.empty:
            return None
        return target.iloc[0].to_dict()
    except:
        return None

st.title("🚀 A股全维度深度分析系统")
st.markdown("---")

# 输入区域
query = st.text_input("请输入股票代码或名称 (例如: 600519 或 贵州茅台)", value="600519").strip()

if st.button("开始全维度分析"):
    with st.status("正在调取实时金融数据...", expanded=True) as status:
        # 0. 基础信息校验
        st.write("🔍 正在检索股票信息...")
        info = get_stock_info(query)
        
        if not info:
            st.error(f"未找到股票 '{query}'，请检查输入是否正确。")
            status.update(label="分析终止", state="error")
        else:
            code = info['代码']
            name = info['名称']
            
            # 第一步：实时行情与价值因子
            st.write("📊 步骤1: 正在计算价值因子...")
            try:
                val_df = ak.stock_a_indicator_lg(symbol=code)
                latest_val = val_df.iloc[-1]
                pe = latest_val['pe']
                pb = latest_val['pb']
            except:
                pe, pb = "暂无数据", "暂无数据"

            # 第二步：财务分析 (摘要)
            st.write("🧾 步骤2: 正在解析最新财报...")
            try:
                # 获取主要财务指标
                finance_df = ak.stock_financial_analysis_indicator_em(symbol=code)
                latest_finance = finance_df.iloc[0] # 最近一期
                net_profit_growth = latest_finance['净利润同比增长率(%)']
                roe = latest_finance['净资产收益率(%)']
            except:
                net_profit_growth, roe = "数据获取失败", "数据获取失败"

            # 第三步：资金流向与交易指标
            st.write("💰 步骤3: 正在追踪主力资金及量比...")
            # 实时数据已在 info 中
            turnover = info['换手率']
            vol_ratio = info['量比']
            
            # 更新状态为完成
            status.update(label="数据获取成功，正在生成报告！", state="complete")

            # --- 渲染分析报告 ---
            st.header(f"【{name} | {code}】分析报告")
            
            # 布局排版
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("一、价值与质量因子 💎")
                st.write(f"**市盈率 (PE):** {pe}")
                st.write(f"**市净率 (PB):** {pb}")
                st.write(f"**净资产收益率 (ROE):** {roe}%")
                if isinstance(pe, (int, float)) and pe < 20:
                    st.success("研判：估值相对较低，具备防御属性。")
                else:
                    st.info("研判：估值处于行业平均或溢价水平。")

            with col2:
                st.subheader("二、财务健康度 📈")
                st.write(f"**净利润增长率:** {net_profit_growth}%")
                st.write(f"**当前股价:** {info['最新价']} 元")
                st.write(f"**今日涨跌幅:** {info['涨跌幅']}%")

            st.divider()

            col3, col4 = st.columns(2)
            
            with col3:
                st.subheader("三、资金与交易面 🌊")
                st.write(f"**换手率:** {turnover}%")
                st.write(f"**量比:** {vol_ratio}")
                if float(vol_ratio) > 1.5:
                    st.warning("提醒：量比显著放大，主力资金活跃或有突发变动。")
                
            with col4:
                st.subheader("四、成长空间与政策 🚀")
                st.info("该模块需结合行业深度报告。根据最新政策导向，建议关注所属板块是否涉及“新质生产力”或“大规模设备更新”等支持方向。")

            st.subheader("五、风险提示 ⚠️")
            st.error(f"""
            1. **波动风险：** 当前换手率为 {turnover}%，注意短期剧烈震荡。
            2. **财务风险：** 需进一步核实经营性现金流是否与净利润匹配。
            3. **宏观风险：** 注意市场系统性风险对个股的压制。
            """)

            st.caption(f"数据更新时间: {time.strftime('%Y-%m-%d %H:%M:%S')} | 数据源: AkShare")

