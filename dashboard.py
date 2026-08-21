import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.utils.quant import get_quant_metrics

# --- Page Setup ---
st.set_page_config(
    page_title="AuraQuant Terminal", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- Institutional UI & Custom CSS Tooltips ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;700&display=swap');

    .stApp { background-color: #0B0E11; color: #EAECEF; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; letter-spacing: -0.5px; font-weight: 700; }
    
    /* Metric Cards */
    .metric-card {
        background-color: #181A20; border: 1px solid #2B313A; border-radius: 4px; 
        padding: 16px 20px; margin-bottom: 12px; transition: border-color 0.2s ease-in-out;
    }
    .metric-card:hover { border-color: #F0B90B; }
    .metric-title { font-size: 13px; color: #848E9C; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; }
    .metric-value-green { font-size: 26px; color: #0ECB81; font-weight: 700; font-family: 'JetBrains Mono', monospace; margin: 6px 0; }
    .metric-value-red { font-size: 26px; color: #F6465D; font-weight: 700; font-family: 'JetBrains Mono', monospace; margin: 6px 0; }
    .metric-sub { font-size: 13px; color: #848E9C; font-family: 'JetBrains Mono', monospace; }
    
    /* Custom CSS Tooltip Engine */
    .tooltip { position: relative; display: inline-flex; align-items: center; cursor: help; }
    .tooltip-icon { 
        font-size: 10px; margin-left: 6px; color: #848E9C; font-weight: bold; 
        background: #2B313A; padding: 2px 6px; border-radius: 12px; font-family: 'Inter', sans-serif;
    }
    .tooltip .tooltiptext {
        visibility: hidden; width: 240px; background-color: #2B313A; color: #EAECEF;
        text-align: left; border-radius: 4px; padding: 12px; position: absolute;
        z-index: 999; bottom: 130%; left: 50%; transform: translateX(-50%);
        opacity: 0; transition: opacity 0.2s; font-size: 12px; font-weight: 400;
        text-transform: none; font-family: 'Inter', sans-serif; line-height: 1.5;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5); border: 1px solid #474D57;
    }
    .tooltip .tooltiptext::after {
        content: ""; position: absolute; top: 100%; left: 50%; margin-left: -5px;
        border-width: 5px; border-style: solid; border-color: #2B313A transparent transparent transparent;
    }
    .tooltip:hover .tooltiptext { visibility: visible; opacity: 1; }
    
    /* Alerts & Tabs */
    .anomaly-alert { 
        background-color: rgba(246, 70, 93, 0.08); border-left: 4px solid #F6465D; 
        padding: 12px 16px; margin-bottom: 16px; color: #F6465D; font-weight: 600; font-size: 14px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 16px; border-bottom: 1px solid #2B313A; }
    .stTabs [data-baseweb="tab"] { color: #848E9C; font-size: 14px; font-weight: 600; padding-bottom: 10px; }
    .stTabs [aria-selected="true"] { color: #F0B90B !important; border-bottom: 2px solid #F0B90B !important; }
    </style>
""", unsafe_allow_html=True)

st.title("AuraQuant Terminal | Real-Time Telemetry")

selected_asset = st.selectbox(
    "Select Asset to Monitor", 
    ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
    index=0,
    help="Select the cryptocurrency pair to query from the local time-series database. The ingestion engine processes all three simultaneously."
)

tab_live, tab_anomalies, tab_arch, tab_quant = st.tabs([
    "Live Terminal", 
    "Anomaly Engine", 
    "Pipeline Architecture", 
    "Quantitative Methods"
])

def create_metric_card(title, value, sub, color_class, tooltip):
    return f"""
        <div class="metric-card">
            <div class="metric-title tooltip">{title} <span class="tooltip-icon">i</span>
                <span class="tooltiptext">{tooltip}</span>
            </div>
            <div class="{color_class}">{value}</div>
            <div class="metric-sub">{sub}</div>
        </div>
    """

with tab_live:
    @st.fragment(run_every="1s")
    def render_live_dashboard():
        ohlcv, raw_ticks, anomalies, stats = get_quant_metrics(symbol=selected_asset, timeframe="1min")
        
        if ohlcv.empty or not stats:
            st.info(f"Waiting for live {selected_asset} ticker stream... Run `python -m src.ingestion.ticker` in Terminal 1.")
            return

        if stats['anomaly_count'] > 0:
            st.markdown(f"""
                <div class="anomaly-alert">
                    ML RISK ALERT: {stats['anomaly_count']} structural market anomaly event(s) isolated by Isolation Forest model. Check Anomaly Engine tab.
                </div>
            """, unsafe_allow_html=True)

        price_color_class = "metric-value-green" if stats['price_change'] >= 0 else "metric-value-red"
        price_sign = "+" if stats['price_change'] >= 0 else ""
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        col1.markdown(create_metric_card(
            f"{selected_asset} Spot", 
            f"${stats['latest_price']:,.2f}", 
            f"{price_sign}${stats['price_change']:,.2f} ({price_sign}{stats['pct_change']:.2f}%)", 
            price_color_class,
            "The most recent spot price received from the exchange via the low-latency WebSocket connection."
        ), unsafe_allow_html=True)
        
        col2.markdown(create_metric_card(
            "Session High", 
            f"${stats['high']:,.2f}", 
            "Peak Price", 
            "metric-value-green",
            "The absolute highest execution price recorded in the database during the currently active tracking session."
        ), unsafe_allow_html=True)

        col3.markdown(create_metric_card(
            "Session Low", 
            f"${stats['low']:,.2f}", 
            "Trough Price", 
            "metric-value-red",
            "The absolute lowest execution price recorded in the database during the currently active tracking session."
        ), unsafe_allow_html=True)

        col4.markdown(create_metric_card(
            "Ingested Volume", 
            f"{stats['total_volume']:,.2f}", 
            "Total Base Asset", 
            "metric-value-green",
            "Cumulative trading volume (in the base asset) aggregated from all raw micro-ticks stored in the relational database."
        ), unsafe_allow_html=True)

        col5.markdown(create_metric_card(
            "ML Anomalies", 
            f"{stats['anomaly_count']} Flagged", 
            f"Ticks Analyzed: {stats['tick_count']:,}", 
            "metric-value-red" if stats['anomaly_count'] > 0 else "metric-value-green",
            "Count of structural outliers identified dynamically using an unsupervised scikit-learn Isolation Forest model."
        ), unsafe_allow_html=True)

        chart_col, feed_col = st.columns([3.5, 1])
        
        with chart_col:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])
            fig.add_trace(go.Candlestick(x=ohlcv['timestamp'], open=ohlcv['open'], high=ohlcv['high'], low=ohlcv['low'], close=ohlcv['close'], name="OHLCV", increasing_line_color='#0ECB81', decreasing_line_color='#F6465D'), row=1, col=1)
            fig.add_trace(go.Scatter(x=ohlcv['timestamp'], y=ohlcv['upper_band'], line=dict(color='#848E9C', width=1, dash='dash'), name="Upper Band (2σ)"), row=1, col=1)
            fig.add_trace(go.Scatter(x=ohlcv['timestamp'], y=ohlcv['lower_band'], line=dict(color='#848E9C', width=1, dash='dash'), fill='tonexty', fillcolor='rgba(132, 142, 156, 0.05)', name="Lower Band (2σ)"), row=1, col=1)
            fig.add_trace(go.Scatter(x=ohlcv['timestamp'], y=ohlcv['vwap'], line=dict(color='#F0B90B', width=1.5), name="VWAP"), row=1, col=1)
            
            colors = ['#0ECB81' if c >= o else '#F6465D' for c, o in zip(ohlcv['close'], ohlcv['open'])]
            fig.add_trace(go.Bar(x=ohlcv['timestamp'], y=ohlcv['volume'], marker_color=colors, name="Volume"), row=2, col=1)

            fig.update_layout(
                template="plotly_dark", paper_bgcolor="#0B0E11", plot_bgcolor="#0B0E11", height=540, margin=dict(l=10, r=10, t=10, b=10),
                showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="Inter", size=12)),
                xaxis_rangeslider_visible=False, xaxis=dict(showgrid=True, gridcolor='#1E2329'), yaxis=dict(showgrid=True, gridcolor='#1E2329'),
                xaxis2=dict(showgrid=True, gridcolor='#1E2329'), yaxis2=dict(showgrid=True, gridcolor='#1E2329')
            )
            st.plotly_chart(fig, use_container_width=True)

        with feed_col:
            st.subheader(f"Live Trade Stream", help="Displays the 15 most recent raw WebSocket ticks processed by the ingestion engine.")
            if not raw_ticks.empty:
                raw_ticks['price_fmt'] = raw_ticks['price'].apply(lambda x: f"${x:,.2f}")
                raw_ticks['vol_fmt'] = raw_ticks['volume'].apply(lambda x: f"{x:,.4f}")
                st.dataframe(
                    raw_ticks[['timestamp', 'price_fmt', 'vol_fmt']],
                    column_config={"timestamp": "Time (UTC)", "price_fmt": "Price", "vol_fmt": "Size"},
                    hide_index=True, use_container_width=True, height=500
                )

    render_live_dashboard()

with tab_anomalies:
    st.subheader(f"Machine Learning Risk Telemetry for {selected_asset}", help="Anomalies flagged via scikit-learn Isolation Forest unsupervised outlier detection.")
    _, _, anomalies, _ = get_quant_metrics(symbol=selected_asset, timeframe="1min")
    
    if anomalies.empty:
        st.success(f"Market conditions stable. Zero structural anomalies detected for {selected_asset} in current session buffer.")
    else:
        st.dataframe(
            anomalies[['timestamp', 'close', 'returns', 'volatility', 'volume']],
            column_config={
                "timestamp": "Time (UTC)", 
                "close": "Close Price", 
                "returns": "Period Return", 
                "volatility": "Rolling Volatility", 
                "volume": "Candle Volume"
            },
            hide_index=True, use_container_width=True
        )

with tab_arch:
    st.subheader("System Architecture & Telemetry Flow")
    st.markdown("""
    * **Async Event Engine:** Non-blocking `asyncio` loop parsing Binance ticker frames (Multi-stream: BTC, ETH, SOL).
    * **Relational Storage:** SQLAlchemy ORM committing normalized ticks to SQLite.
    * **Machine Learning Outlier Engine:** Unsupervised Isolation Forest model processing rolling returns and volatility.
    """)

with tab_quant:
    st.subheader("Machine Learning Anomaly Detection Architecture")
    st.markdown("""
    #### Unsupervised Outlier Detection (Isolation Forest)
    Instead of relying on rigid static thresholds, **AuraQuant** deploys an **Isolation Forest** ensemble model to identify abnormal market behavior in real-time high-frequency tick streams.

    * **Feature Matrix:** Built dynamically from rolling returns, realized volatility, and aggregate volume.
    * **Algorithm Mechanics:** The model recursively partitions feature space. Because market anomalies (flash crashes, liquidity vacuums, or institutional block dumps) are rare and distinct, they isolate much faster than normal market micro-structure.
    """)