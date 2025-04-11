import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from newsapi import NewsApiClient
import pandas_ta as ta

from services import mt5_service
from config import NEWS_API_KEY, TIMEFRAME

# Inicializa APIs externas
newsapi = NewsApiClient(api_key=NEWS_API_KEY)
sentiment_analyzer = SentimentIntensityAnalyzer()


def analyze_chart(symbol, bars=500):
    rates = mt5_service.copy_rates(symbol, TIMEFRAME, bars)
    if rates is None or len(rates) < 50:
        return "Erro - Dados insuficientes"

    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df['MA5'] = df['close'].rolling(5).mean()
    df['MA20'] = df['close'].rolling(20).mean()
    df['RSI'] = ta.rsi(df['close'], length=14)

    bb = ta.bbands(df['close'], length=20)
    df = pd.concat([df, bb], axis=1)

    df['Target'] = (df['close'].shift(-1) > df['close']).astype(int)
    df.dropna(inplace=True)

    X = df[['MA5', 'MA20', 'RSI', 'BBU_20_2.0', 'BBM_20_2.0', 'BBL_20_2.0']]
    y = df['Target']

    if X.empty or len(X) < 2:
        return "Erro - Dados insuficientes"

    try:
        last_row = X.iloc[-1].dropna()
        if last_row.shape[0] != X.shape[1]:
            return "Erro - Última linha incompleta"

        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X[:-1], y[:-1])
        signal = model.predict([last_row])[0]
        signal_text = "Buy" if signal == 1 else "Sell"
    except Exception as e:
        print(f"[IA] Erro ao prever sinal com modelo técnico: {e}")
        return "Erro - Modelo técnico"

    # Justificativa da previsão técnica
    try:
        if df['MA5'].iloc[-1] > df['MA20'].iloc[-1] and signal == 1:
            justification = "MA5 crossed above MA20"
        elif df['MA5'].iloc[-1] < df['MA20'].iloc[-1] and signal == 0:
            justification = "MA5 crossed below MA20"
        elif df['RSI'].iloc[-1] > 70 and signal == 0:
            justification = "RSI overbought (>70)"
        elif df['RSI'].iloc[-1] < 30 and signal == 1:
            justification = "RSI oversold (<30)"
        else:
            justification = "Pattern detected by model"
    except Exception:
        justification = "Justification error"

    return f"{signal_text} - {justification}"


def analyze_news(symbol):
    try:
        articles = newsapi.get_everything(
            q=symbol,
            language='en',
            sort_by='publishedAt',
            page_size=5
        )

        if not articles['articles']:
            return "Erro - Nenhuma notícia recente"

        sentiments = []
        for article in articles['articles']:
            text = f"{article['title']} {article.get('description', '')}"
            score = sentiment_analyzer.polarity_scores(text)['compound']
            sentiments.append(score)

        avg_sentiment = np.mean(sentiments)
        if avg_sentiment > 0.05:
            return "Positive - Optimistic news"
        elif avg_sentiment < -0.05:
            return "Negative - Pessimistic news"
        else:
            return "Neutral - No clear impact"

    except Exception as e:
        print(f"[NEWS] Erro ao buscar notícias: {e}")
        return "Erro - News API"


def safe_split(signal_str):
    if not isinstance(signal_str, str):
        return "Indefinido"
    parts = signal_str.split(" - ")
    return parts[0] if parts else "Indefinido"


def combine_signals(chart_signal, news_signal):
    chart_action = safe_split(chart_signal)
    news_sentiment = safe_split(news_signal)

    if "Erro" in chart_action or "Erro" in news_sentiment:
        return "Neutral - Sem dados confiáveis"

    confidence = 50

    if chart_action == "Buy":
        confidence += 15
    elif chart_action == "Sell":
        confidence += 15

    if news_sentiment == "Positive":
        confidence += 20 if chart_action == "Buy" else -10
    elif news_sentiment == "Negative":
        confidence += 20 if chart_action == "Sell" else -10

    confidence = max(0, min(100, confidence))
    signal = chart_action if abs(confidence - 50) >= 10 else "Neutral"

    return f"{signal} - {confidence:.0f}% confidence"
