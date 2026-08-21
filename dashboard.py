import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from src.utils.quant import get_quant_metrics

# --- Page Setup ---
st.set_page_config(
    page_title="AuraQuant Terminal", 
    page_icon="⚡", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- Binance Dark Theme CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0B0E11; color: #EAECEF; font-family: 'Inter', sans-serif; }
    .metric-card {
        background-color: #181A20; border: 1px solid #2B313A; border-radius: 6px; 
        padding: 12px 16px; margin-bottom: 10px; cursor: help; transition: border-color 0.2s;
    }
    .metric-card:hover { border-color: #F0B90B; }
    .metric-title { font-size: 11px; color: #848E9C; text-transform: uppercase; font-weight: 600; }
    .metric-value-green { font-size: 20px; color: #0ECB81; font-weight: bold; }
    .metric-value-red { font-size: 20px; color: #F6465D; font-weight: bold; }
    .metric-sub { font-size: 12px; color: #848E9C; }
    .anomaly-alert { 
        background-color: rgba(246, 70, 93, 0.15); border: 1px solid #F6465D; 
        border-radius: 6px; padding: 10px 16px; margin-bottom: 15px; 
        color: #F6465D; font-weight: 600; display: flex; align-items: center; gap: 10px; 
    }
    .stTabs [data-baseweb="tab-list"] { gap: 12px; border-bottom: 1px solid #2B313A; }
    .stTabs [data-baseweb="tab"] { color: #848E9C; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #F0B90B !important; border-bottom: 2px solid #F0B90B !important; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ AuraQuant Terminal | Real-Time Telemetry")

selected_asset = st.selectbox(
    "Select Asset to Monitor", 
    ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
    index=0,
    help="Select the cryptocurrency pair to query from the local time-series database. The ingestion engine processes all three simultaneously."
)

tab_live, tab_anomalies, tab_arch, tab_quant = st.tabs([
    "📈 Live Terminal", 
    "🚨 Anomaly Engine", 
    "⚙️ Pipeline Architecture", 
    "🧮 Quantitative Methods"
])

# --- LIVE TERMINAL TAB ---
with tab_live:
    @st.fragment(run_every="1s")
    def render_live_dashboard():
        ohlcv, raw_ticks, anomalies, stats = get_quant_metrics(symbol=selected_asset, timeframe="1min")
        
        if ohlcv.empty or not stats:
            st.info(f"🔄 Waiting for live {selected_asset} ticker stream... Run `python -m src.ingestion.ticker` in Terminal 1.")
            return

        if stats['anomaly_count'] > 0:
            st.markdown(f"""
                <div class="anomaly-alert" title="Review the Anomaly Engine tab for timestamps and details regarding these statistical breaches.">
                    ⚠️ <b>VOLATILITY ALERT:</b> {stats['anomaly_count']} statistical anomaly event(s) detected ($2\sigma$ Price Breach or $3\\times$ Volume Spike) for {selected_asset}. Check Anomaly Engine tab for details.
                </div>
            """, unsafe_allow_html=True)

        price_color_class = "metric-value-green" if stats['price_change'] >= 0 else "metric-value-red"
        price_sign = "+" if stats['price_change'] >= 0 else ""
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        col1.markdown(f"""
            <div class="metric-card" title="The most recent spot price received from the exchange via WebSocket.">
                <div class="metric-title">{selected_asset} Spot ℹ️</div>
                <div class="{price_color_class}">${stats['latest_price']:,.2f}</div>
                <div class="metric-sub">{price_sign}${stats['price_change']:,.2f} ({price_sign}{stats['pct_change']:.2f}%)</div>
            </div>
        """, unsafe_allow_html=True)
        
        col2.markdown(f"""
            <div class="metric-card" title="The absolute highest price recorded during the currently active tracking session.">
                <div class="metric-title">Session High ℹ️</div>
                <div style="font-size:20px; font-weight:bold; color:#EAECEF">${stats['high']:,.2f}</div>
                <div class="metric-sub">Peak Price</div>
            </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
            <div class="metric-card" title="The absolute lowest price recorded during the currently active tracking session.">
                <div class="metric-title">Session Low ℹ️</div>
                <div style="font-size:20px; font-weight:bold; color:#EAECEF">${stats['low']:,.2f}</div>
                <div class="metric-sub">Trough Price</div>
            </div>
        """, unsafe_allow_html=True)

        col4.markdown(f"""
            <div class="metric-card" title="Cumulative volume (in base asset) aggregated from all raw ticks in the database.">
                <div class="metric-title">Ingested Volume ℹ️</div>
                <div style="font-size:20px; font-weight:bold; color:#EAECEF">{stats['total_volume']:,.2f}</div>
                <div class="metric-sub">Total Handled</div>
            </div>
        """, unsafe_allow_html=True)

        col5.markdown(f"""
            <div class="metric-card" title="Count of times the asset price breached the 2-Sigma Bollinger Band or volume spiked above the moving average.">
                <div class="metric-title">Anomaly Events ℹ️</div>
                <div style="font-size:20px; font-weight:bold; color:{'#F6465D' if stats['anomaly_count'] > 0 else '#0ECB81'}">{stats['anomaly_count']} Flagged</div>
                <div class="metric-sub">Ticks: {stats['tick_count']:,}</div>
            </div>
        """, unsafe_allow_html=True)

        chart_col, feed_col = st.columns([3.5, 1])
        
        with chart_col:
            fig = make_subplots(
                rows=2, cols=1, 
                shared_xaxes=True, 
                vertical_spacing=0.03, 
                row_heights=[0.75, 0.25]
            )

            # Candlestick
            fig.add_trace(go.Candlestick(
                x=ohlcv['timestamp'],
                open=ohlcv['open'], high=ohlcv['high'],
                low=ohlcv['low'], close=ohlcv['close'],
                name="OHLCV",
                increasing_line_color='#0ECB81',
                decreasing_line_color='#F6465D'
            ), row=1, col=1)

            # Bollinger Bands ($2\sigma$)
            fig.add_trace(go.Scatter(
                x=ohlcv['timestamp'], y=ohlcv['upper_band'],
                line=dict(color='#848E9C', width=1, dash='dash'),
                name="Upper Band ($2\sigma$)"
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=ohlcv['timestamp'], y=ohlcv['lower_band'],
                line=dict(color='#848E9C', width=1, dash='dash'),
                fill='tonexty', fillcolor='rgba(132, 142, 156, 0.05)',
                name="Lower Band ($2\sigma$)"
            ), row=1, col=1)

            # VWAP
            fig.add_trace(go.Scatter(
                x=ohlcv['timestamp'], y=ohlcv['vwap'],
                line=dict(color='#F0B90B', width=1.5),
                name="VWAP"
            ), row=1, col=1)

            # Volume Bars
            colors = ['#0ECB81' if c >= o else '#F6465D' for c, o in zip(ohlcv['close'], ohlcv['open'])]
            fig.add_trace(go.Bar(
                x=ohlcv['timestamp'], y=ohlcv['volume'],
                marker_color=colors,
                name="Volume"
            ), row=2, col=1)

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0B0E11",
                plot_bgcolor="#0B0E11",
                height=520,
                margin=dict(l=10, r=10, t=10, b=10),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis_rangeslider_visible=False,
                xaxis=dict(showgrid=True, gridcolor='#1E2329'),
                yaxis=dict(showgrid=True, gridcolor='#1E2329'),
                xaxis2=dict(showgrid=True, gridcolor='#1E2329'),
                yaxis2=dict(showgrid=True, gridcolor='#1E2329')
            )
            st.plotly_chart(fig, use_container_width=True)

        with feed_col:
            st.subheader(f"⚡ {selected_asset} Live Feed", help="Displays the 15 most recent raw WebSocket ticks processed by the ingestion engine.")
            if not raw_ticks.empty:
                raw_ticks['price_fmt'] = raw_ticks['price'].apply(lambda x: f"${x:,.2f}")
                raw_ticks['vol_fmt'] = raw_ticks['volume'].apply(lambda x: f"{x:,.4f}")
                
                st.dataframe(
                    raw_ticks[['timestamp', 'price_fmt', 'vol_fmt']],
                    column_config={
                        "timestamp": "Time (UTC)",
                        "price_fmt": "Price",
                        "vol_fmt": "Size"
                    },
                    hide_index=True,
                    use_container_width=True,
                    height=480
                )

    render_live_dashboard()

# --- ANOMALY TAB ---
with tab_anomalies:
    st.subheader(f"🚨 Detected Events for {selected_asset}", help="A log of all ticks that breached the 2-Sigma volatility bands or exceeded the 3x volume average.")
    _, _, anomalies, _ = get_quant_metrics(symbol=selected_asset, timeframe="1min")
    
    if anomalies.empty:
        st.success(f"✅ No volatility breaches or volume spikes detected for {selected_asset} in current session buffer.")
    else:
        st.dataframe(
            anomalies[['timestamp', 'close', 'upper_band', 'lower_band', 'volume', 'price_anomaly', 'volume_anomaly']],
            column_config={
                "timestamp": "Time (UTC)",
                "close": "Close Price",
                "upper_band": "Upper $2\sigma$ Band",
                "lower_band": "Lower $2\sigma$ Band",
                "volume": "Candle Vol",
                "price_anomaly": "Price Breach ($2\sigma$)",
                "volume_anomaly": "Volume Spike ($3\\times$)"
            },
            hide_index=True,
            use_container_width=True
        )

# --- ARCHITECTURE TAB ---
with tab_arch:
    st.subheader("⚙️ System Architecture & Telemetry Flow")
    st.markdown("""
    * **Async Event Engine:** Non-blocking `asyncio` loop parsing Binance ticker frames (Multi-stream: BTC, ETH, SOL).
    * **Relational Storage:** SQLAlchemy ORM committing normalized ticks to SQLite.
    * **Quantitative Anomaly Engine:** Real-time Bollinger Band ($2\sigma$) and Volume ($3\\times$ MA) detection.
    """)

# --- QUANTITATIVE TAB ---
with tab_quant:
    st.subheader("🧮 Statistical Anomaly Math")
    st.markdown("""
    #### 1. Bollinger Band ($2\sigma$) Volatility Breach
    $$\text{Upper Band} = \mu_{20} + 2\sigma_{20}, \quad \text{Lower Band} = \mu_{20} - 2\sigma_{20}$$
    An anomaly is triggered whenever:
    $$\text{Price} > \text{Upper Band} \quad \text{or} \quad \text{Price} < \text{Lower Band}$$

    #### 2. Volume Spike Anomaly
    $$\text{Volume Anomaly} = \text{Volume}_{t} > 3 \\times \text{SMA}_{10}(\text{Volume})$$
    """)