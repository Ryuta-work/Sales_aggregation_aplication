import streamlit as st
import pandas as pd
import io

# ==============================================================================
# Streamlitアプリのタイトルと説明
# ==============================================================================
st.set_page_config(page_title="売上データ統合アプリ", layout="wide")
st.title("🛍️ 売上データ統合アプリ")
st.write("「店内売上」「自動販売機」「ふるさと納税」「ECサイト」の各データをアップロードして、売上を統合・集計します。")

# ==============================================================================
# 設定項目
# ==============================================================================

# --- ふるさと納税の集計パターン定義 ---
PATTERNS = [
    # （既存のふるさと納税の定義は省略せずそのまま残します）
    {
        'gift_name': 'ANFP002岐阜の味　田毎の味噌煮込みうどんセット 即席 カンタン 麺 岐阜市/ラボレムス　(8%)',
        'menus': [{'name': 'ｱﾙﾐ味噌(冷凍)', 'count': 3}]
    },
    {
        'gift_name': 'ANFP001岐阜の味　田毎のカレー煮込みうどんセット 即席 カンタン 麺 岐阜市/ラボレムス　(8%)',
        'menus': [{'name': 'ｱﾙﾐカレー(冷凍)', 'count': 3}]
    },
    {
        'gift_name': 'ANFP003岐阜の味　田毎の煮込みうどん定番セット 即席 カンタン 麺 岐阜市/ラボレムス　(8%)',
        'menus': [
            {'name': 'ｱﾙﾐ味噌(冷凍)', 'count': 1},
            {'name': 'ｱﾙﾐカレー(冷凍)', 'count': 1},
            {'name': 'ｱﾙﾐすまし(冷凍)', 'count': 1}
        ]
    },
    {
        'gift_name': 'ANFP004岐阜の味　田毎の煮込みうどん(辛辛麺)3食セット 即席 カンタン 麺 岐阜市/ラボレムス　(8%)',
        'menus': [
            {'name': 'ｱﾙﾐピリ辛(冷凍)', 'count': 1},
            {'name': 'ｱﾙﾐスタミナ(冷凍)', 'count': 1},
            {'name': 'ｱﾙﾐカレー(冷凍)', 'count': 1}
        ]
    },
    {
        'gift_name': 'ANFP005岐阜の味　田毎の煮込みうどん満喫セット 即席 カンタン 麺 岐阜市/ラボレムス　(8%)',
        'menus': [
            {'name': 'ｱﾙﾐ味噌(冷凍)', 'count': 1},
            {'name': 'ｱﾙﾐカレー(冷凍)', 'count': 1},
            {'name': 'ｱﾙﾐスタミナ(冷凍)', 'count': 1},
            {'name': 'ｱﾙﾐピリ辛(冷凍)', 'count': 1},
            {'name': 'ｱﾙﾐすまし(冷凍)', 'count': 1}
        ]
    }
]

# --- ふるさと納税のメニュー別単価定義 ---
MENU_PRICES = {
    'ｱﾙﾐ味噌(冷凍)': 540,
    'ｱﾙﾐカレー(冷凍)': 570,
    'ｱﾙﾐスタミナ(冷凍)': 900,
    'ｱﾙﾐピリ辛(冷凍)': 570,
    'ｱﾙﾐすまし(冷凍)': 540
}

# ★★★ ECサイトの集計ルール定義 ★★★
EC_RULES = {
    '味噌煮込み（3食入り）': [
        {'name': 'ｱﾙﾐ味噌(冷凍)', 'count': 3, 'price': 900}
    ],
    'すまし煮込み（3食入り）': [
        {'name': 'ｱﾙﾐすまし(冷凍)', 'count': 3, 'price': 900}
    ],
    'カレー煮込み（3食入り）': [
        {'name': 'ｱﾙﾐカレー(冷凍)', 'count': 3, 'price': 950}
    ],
    'ピリ辛味噌煮込み（3食入り）': [
        {'name': 'ｱﾙﾐピリ辛(冷凍)', 'count': 3, 'price': 950}
    ],
    'ピリ辛スタミナ牛もつ煮込み（3食入り）': [
        {'name': 'ｱﾙﾐスタミナ(冷凍)', 'count': 3, 'price': 1500}
    ],
    '定番セット（3食入り）': [
        {'name': 'ｱﾙﾐ味噌(冷凍)',   'count': 1, 'price': 900},
        {'name': 'ｱﾙﾐカレー(冷凍)', 'count': 1, 'price': 950},
        {'name': 'ｱﾙﾐすまし(冷凍)', 'count': 1, 'price': 900}
    ],
    '満喫セット（5食入り）': [
        {'name': 'ｱﾙﾐ味噌(冷凍)',   'count': 1, 'price': 900},
        {'name': 'ｱﾙﾐカレー(冷凍)', 'count': 1, 'price': 950},
        {'name': 'ｱﾙﾐスタミナ(冷凍)', 'count': 1, 'price': 1500},
        {'name': 'ｱﾙﾐピリ辛(冷凍)',   'count': 1, 'price': 950},
        {'name': 'ｱﾙﾐすまし(冷凍)', 'count': 1, 'price': 900}
    ],
    '辛辛麺セット（3食入り）': [
        {'name': 'ｱﾙﾐピリ辛(冷凍)', 'count': 1, 'price': 950},
        {'name': 'ｱﾙﾐスタミナ(冷凍)', 'count': 1, 'price': 1500},
        {'name': 'ｱﾙﾐカレー(冷凍)', 'count': 1, 'price': 950}
    ],
    '辛辛麺セット（5食入り）': [
        {'name': 'ｱﾙﾐピリ辛(冷凍)',   'count': 1, 'price': 950},
        {'name': 'ｱﾙﾐスタミナ(冷凍)', 'count': 2, 'price': 1500},
        {'name': 'ｱﾙﾐカレー(冷凍)', 'count': 2, 'price': 950}
    ],
}


# ==============================================================================
# データ処理関数
# ==============================================================================

def convert_excel_to_dataframes(uploaded_file):
    try:
        excel_book = pd.read_excel(uploaded_file, sheet_name=None)
        st.success(f"✅ Excelファイル（{len(excel_book)}シート）を読み込みました。")
        return excel_book
    except Exception as e:
        st.error(f"エラー: Excelファイルの処理中に問題が発生しました: {e}")
        return None

def summarize_store_sales(excel_sheets_dict):
    TARGET_CATEGORY = "冷凍持帰り"
    all_sales_data = []
    for sheet_name, df_sheet in excel_sheets_dict.items():
        try:
            df = df_sheet.iloc[:, [1, 2, 35, 38]]
            df.columns = ['カテゴリ', 'メニュー名', '売上数', '売上額']
            df['カテゴリ'] = df['カテゴリ'].ffill()
            target_df = df[df['カテゴリ'].str.contains(TARGET_CATEGORY, na=False)].copy()
            all_sales_data.append(target_df[['メニュー名', '売上数', '売上額']])
        except Exception:
            continue
    if not all_sales_data:
        st.warning("Excelファイル内に「冷凍持帰り」カテゴリのデータが見つかりませんでした。")
        return pd.DataFrame(columns=['メニュー名', '売上数', '売上額'])
    combined_df = pd.concat(all_sales_data, ignore_index=True)
    for col in ['売上数', '売上額']:
        combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')
    combined_df.dropna(subset=['メニュー名', '売上数', '売上額'], inplace=True)
    for col in ['売上数', '売上額']:
        combined_df[col] = combined_df[col].astype(int)
    total_sales = combined_df.groupby('メニュー名').agg(売上数=('売上数', 'sum'),売上額=('売上額', 'sum')).reset_index()
    st.success("✅ 店舗データ（冷凍持帰り）の集計が完了しました。")
    return total_sales

def summarize_vending_machine(vending_df):
    name_mapping = {'味噌煮込み': 'ｱﾙﾐ味噌(冷凍)','カレー煮込み': 'ｱﾙﾐカレー(冷凍)','ピリ辛味噌煮込み': 'ｱﾙﾐピリ辛(冷凍)','鍋焼き': 'ｱﾙﾐ鍋焼き(冷凍)'}
    try:
        df = vending_df[['商品名', '価額']].copy()
        df['商品名'] = df['商品名'].replace(name_mapping)
        sales_summary = df.groupby('商品名').agg(売上数=('商品名', 'count'),売上額=('価額', 'sum')).reset_index()
        sales_summary.rename(columns={'商品名': 'メニュー名'}, inplace=True)
        st.success("✅ 自動販売機データの集計が完了しました。")
        return sales_summary
    except Exception as e:
        st.error(f"エラー: 自動販売機データの処理中に問題が発生しました: {e}")
        return pd.DataFrame(columns=['メニュー名', '売上数', '売上額'])

def summarize_furusato_sales(furusato_df):
    all_summary_data = []
    try:
        df = furusato_df[['返礼品', '提供価格']].copy()
        for pattern in PATTERNS:
            target_gift = pattern['gift_name']
            menus = pattern['menus']
            target_df = df[df['返礼品'] == target_gift].copy()
            if not target_df.empty:
                num_gifts = len(target_df)
                for menu in menus:
                    menu_name, count_per_gift = menu['name'], menu['count']
                    sales_count = num_gifts * count_per_gift
                    unit_price = MENU_PRICES.get(menu_name, 0)
                    total_revenue = sales_count * unit_price
                    all_summary_data.append({'メニュー名': menu_name, '売上数': sales_count, '売上額': total_revenue})
        if not all_summary_data:
            st.warning("ふるさと納税ファイル内に、集計対象の返礼品が見つかりませんでした。")
            return pd.DataFrame(columns=['メニュー名', '売上数', '売上額'])
        summary_df = pd.DataFrame(all_summary_data)
        final_summary = summary_df.groupby('メニュー名').agg({'売上数': 'sum', '売上額': 'sum'}).reset_index()
        st.success("✅ ふるさと納税データの集計が完了しました。")
        return final_summary
    except Exception as e:
        st.error(f"エラー: ふるさと納税データの処理中に問題が発生しました: {e}")
        return pd.DataFrame(columns=['メニュー名', '売上数', '売上額'])

# ★★★ 新しく追加したECサイト集計用の関数 ★★★
def summarize_ec_sales(ec_df):
    """ECサイトの売上DataFrameを読み込み、定義済みルールに基づいてセット商品を分解・集計する。"""
    try:
        df = ec_df[['商品名', '販売個数', '小計']].copy()
        rule_product_names = EC_RULES.keys()
        
        rules_df = df[df['商品名'].isin(rule_product_names)].copy()
        standard_df = df[~df['商品名'].isin(rule_product_names)].copy()
        
        processed_dfs = []

        if not rules_df.empty:
            decomposed_rows = []
            for _, row in rules_df.iterrows():
                product_name, num_sets_sold = row['商品名'], row['販売個数']
                breakdown_rules = EC_RULES[product_name]
                for item_rule in breakdown_rules:
                    sales_count = num_sets_sold * item_rule['count']
                    sales_amount = sales_count * item_rule['price']
                    decomposed_rows.append({'メニュー名': item_rule['name'], '売上数': sales_count, '売上額': sales_amount})
            processed_dfs.append(pd.DataFrame(decomposed_rows))

        if not standard_df.empty:
            standard_df.rename(columns={'商品名': 'メニュー名', '販売個数': '売上数', '小計': '売上額'}, inplace=True)
            processed_dfs.append(standard_df[['メニュー名', '売上数', '売上額']])

        if not processed_dfs:
            st.warning("ECサイトファイル内に、集計対象の商品が見つかりませんでした。")
            return pd.DataFrame(columns=['メニュー名', '売上数', '売上額'])
        
        combined_df = pd.concat(processed_dfs, ignore_index=True)
        summary_df = combined_df.groupby('メニュー名').agg({'売上数': 'sum', '売上額': 'sum'}).reset_index()
        st.success("✅ ECサイトデータの集計が完了しました。")
        return summary_df

    except Exception as e:
        st.error(f"エラー: ECサイトデータの処理中に問題が発生しました: {e}")
        return pd.DataFrame(columns=['メニュー名', '売上数', '売上額'])

# ★★★ 修正した最終レポート関数 ★★★
def create_final_report(store_df, vending_df, furusato_df, ec_df):
    """4つの集計済みDataFrameを統合し、最終的な統合レポートを作成する。"""
    all_dfs = [df for df in [store_df, vending_df, furusato_df, ec_df] if not df.empty]
    if not all_dfs:
        st.error("統合対象のデータがありません。")
        return pd.DataFrame()
    combined_df = pd.concat(all_dfs, ignore_index=True)
    for col in ['売上数', '売上額']:
        combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce').fillna(0)
        combined_df[col] = combined_df[col].astype(int)
    final_summary = combined_df.groupby('メニュー名').agg(売上数=('売上数', 'sum'), 売上額=('売上額', 'sum')).reset_index()
    final_summary_sorted = final_summary.sort_values(by='売上額', ascending=False)
    total_count = final_summary_sorted['売上数'].sum()
    total_revenue = final_summary_sorted['売上額'].sum()
    total_row = pd.DataFrame([{'メニュー名': '合計', '売上数': total_count, '売上額': total_revenue}])
    report_with_total = pd.concat([final_summary_sorted, total_row], ignore_index=True)
    st.success("✅ 最終レポートの作成が完了しました。")
    return report_with_total

# --- ヘルパー関数 ---
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

# ==============================================================================
# Streamlit UI部分
# ==============================================================================

st.header("1. ファイルのアップロード")
# ★★★ ファイルアップローダーを4つに修正 ★★★
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

with row1_col1:
    uploaded_store_file = st.file_uploader("**① 店内売上データ (.xlsx)**", type=['xlsx'])
with row1_col2:
    uploaded_vending_file = st.file_uploader("**② 自動販売機売上データ (.csv)**", type=['csv'])
with row2_col1:
    uploaded_furusato_file = st.file_uploader("**③ ふるさと納税売上データ (.csv)**", type=['csv'])
with row2_col2:
    uploaded_ec_file = st.file_uploader("**④ ECサイト売上データ (.csv)**", type=['csv'])


st.header("2. データ処理の実行")
# ★★★ ボタンの有効化条件を4ファイルに変更 ★★★
if uploaded_store_file and uploaded_vending_file and uploaded_furusato_file and uploaded_ec_file:
    if st.button("📈 すべてのデータを集計する", type="primary"):
        with st.spinner("データを処理中です..."):
            # 各データソースの処理
            store_sheets = convert_excel_to_dataframes(uploaded_store_file)
            st.session_state['store_summary'] = summarize_store_sales(store_sheets) if store_sheets else pd.DataFrame()
            
            st.session_state['vending_summary'] = summarize_vending_machine(pd.read_csv(uploaded_vending_file))
            
            st.session_state['furusato_summary'] = summarize_furusato_sales(pd.read_csv(uploaded_furusato_file, encoding='cp932'))
            
            # ★★★ ECサイトの処理を追加 ★★★
            st.session_state['ec_summary'] = summarize_ec_sales(pd.read_csv(uploaded_ec_file, encoding='cp932'))

            # 最終レポートの作成
            st.session_state['final_report'] = create_final_report(
                st.session_state['store_summary'],
                st.session_state['vending_summary'],
                st.session_state['furusato_summary'],
                st.session_state['ec_summary']
            )
        st.balloons()
else:
    st.info("4つすべてのファイルをアップロードすると、処理を開始できます。")

# --- 結果の表示とダウンロード ---
if 'final_report' in st.session_state:
    st.header("3. 集計結果の確認とダウンロード")
    
    # ★★★ タブを5つに修正 ★★★
    tabs = st.tabs(["📊 最終統合レポート", "🏪 店舗売上", "🤖 自動販売機", "🎁 ふるさと納税", "💻 ECサイト"])

    with tabs[0]:
        st.subheader("最終統合レポート")
        final_df = st.session_state['final_report']
        st.dataframe(final_df.style.format({'売上数': '{:,}', '売上額': '{:,}円'}))
        st.download_button("📥 CSVをダウンロード", convert_df_to_csv(final_df), "最終統合レポート.csv", "text/csv")

    with tabs[1]:
        st.subheader("店舗売上レポート (冷凍持帰り)")
        df = st.session_state['store_summary']
        st.dataframe(df.style.format({'売上数': '{:,}', '売上額': '{:,}円'}))
        st.download_button("📥 CSVをダウンロード", convert_df_to_csv(df), "店舗売上レポート.csv", "text/csv")

    with tabs[2]:
        st.subheader("自動販売機レポート")
        df = st.session_state['vending_summary']
        st.dataframe(df.style.format({'売上数': '{:,}', '売上額': '{:,}円'}))
        st.download_button("📥 CSVをダウンロード", convert_df_to_csv(df), "自動販売機レポート.csv", "text/csv")

    with tabs[3]:
        st.subheader("ふるさと納税レポート")
        df = st.session_state['furusato_summary']
        st.dataframe(df.style.format({'売上数': '{:,}', '売上額': '{:,}円'}))
        st.download_button("📥 CSVをダウンロード", convert_df_to_csv(df), "ふるさと納税レポート.csv", "text/csv")
        
    # ★★★ ECサイト用のタブを追加 ★★★
    with tabs[4]:
        st.subheader("ECサイトレポート")
        df = st.session_state['ec_summary']
        st.dataframe(df.style.format({'売上数': '{:,}', '売上額': '{:,}円'}))
        st.download_button("📥 CSVをダウンロード", convert_df_to_csv(df), "ECサイトレポート.csv", "text/csv")