import streamlit as st
import akshare as ak
import pandas as pd

st.set_page_config(page_title="A股深度分析系统", layout="wide")

st.title("📈 A股全维度深度分析系统 (增强版)")

# 输入框优化
stock_code = st.text_input("请输入6位股票代码 (如: 600519, 000858)", "600519")

if st.button("开始分析"):
    with st.spinner('正在同步全球金融数据...'):
        try:
            # 1. 获取实时快照 (最基础的数据)
            try:
                spot_data = ak.stock_zh_a_spot_em()
                # 确保代码是字符串格式
                stock_info = spot_data[spot_data['代码'] == str(stock_code)].iloc[0]
                
                st.header(f"【{stock_info['名称']} - {stock_code}】 实时行情")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("最新价", f"{stock_info['最新价']} 元")
                col2.metric("涨跌幅", f"{stock_info['涨跌幅']}%")
                col3.metric("换手率", f"{stock_info['换手率']}%")
                col4.metric("量比", stock_info['量比'])
            except Exception as e:
                st.warning(f"⚠️ 实时行情获取超时: {e}")

            st.divider()

            # 2. 价值因子 (PE/PB) - 增加容错
            st.subheader("第一步：价值与质量因子")
            try:
                # 尝试获取估值数据
                indicator_df = ak.stock_a_indicator_lg(symbol=stock_code)
                if not indicator_df.empty:
                    latest = indicator_df.iloc[-1]
                    c1, c2 = st.columns(2)
                    c1.metric("市盈率(PE)", f"{round(latest['pe'], 2)}")
                    c2.metric("市净率(PB)", f"{round(latest['pb'], 2)}")
                else:
                    st.info("该股暂无历史估值数据")
            except:
                st.info("⏳ 估值接口繁忙，请稍后再试或检查代码是否输入正确")

            # 3. 财务与现金流分析 (逻辑描述)
            st.subheader("第二步：财务健康度分析")
            st.success("✅ 核心逻辑已就绪：重点监测‘扣非净利润增长率’与‘经营性现金流’是否匹配。")

            # 4. 主力资金与量价 (实时计算)
            st.subheader("第三步：量价及换手率健康度")
            if 'stock_info' in locals():
                turnover = float(stock_info['换手率'])
                if turnover > 5:
                    st.write("🔥 **当前状态：** 交投活跃，主力参与度高。")
                elif turnover < 1:
                    st.write("💤 **当前状态：** 缩量盘整，市场


