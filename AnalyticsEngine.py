import pandas as pd
import openai
import matplotlib.pyplot as plt
import seaborn as sns
from prophet import Prophet
from sqlalchemy import create_engine
import numpy as np
from scipy.stats import pearsonr

class AnalyticsEngine:
    def __init__(self, db_url, openai_api_key):
        self.engine = create_engine(db_url)
        openai.api_key = openai_api_key
    
    def query_to_sql(self, user_query):
        """Converts natural language query to SQL using GPT-3.5."""
        prompt = f"Convert this query into SQL for an AdventureWorks database: {user_query}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    
    def fetch_data(self, sql_query):
        """Executes SQL query and fetches data into a DataFrame."""
        return pd.read_sql(sql_query, self.engine)
    
    def analyze_trends(self, df, date_col, value_col):
        """Performs trend analysis and forecasting using Prophet."""
        df = df.rename(columns={date_col: "ds", value_col: "y"})
        model = Prophet()
        model.fit(df)
        future = model.make_future_dataframe(periods=12, freq="M")
        forecast = model.predict(future)
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    
    def detect_anomalies(self, df, value_col):
        """Finds anomalies based on statistical deviation."""
        threshold = df[value_col].mean() + 3 * df[value_col].std()
        anomalies = df[df[value_col] > threshold]
        return anomalies
    
    def correlation_analysis(self, df, col1, col2):
        """Performs correlation analysis between two variables."""
        correlation, _ = pearsonr(df[col1], df[col2])
        return f"Correlation coefficient between {col1} and {col2}: {correlation:.2f}"
    
    def moving_average(self, df, value_col, window=3):
        """Calculates moving average to smooth data trends."""
        df[f'{value_col}_moving_avg'] = df[value_col].rolling(window=window).mean()
        return df
    
    def generate_insights(self, user_query, df):
        """Generates humanized insights using GPT-3.5."""
        prompt = f"Analyze this data and answer: {user_query}. Data: {df.head(10).to_dict()}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    
    def process_query(self, user_query):
        """Full pipeline: Converts query -> Runs SQL -> Analyzes Data -> Returns Insights."""
        sql_query = self.query_to_sql(user_query)
        df = self.fetch_data(sql_query)
        if df.empty:
            return "No data found for your query."
        
        analysis_results = ""
        if "trend" in user_query.lower() or "forecast" in user_query.lower():
            analysis_results += "\nTrend Analysis:\n"
            trend_df = self.analyze_trends(df, date_col="date", value_col="value")
            analysis_results += trend_df.tail().to_string()
        
        if "anomaly" in user_query.lower() or "outlier" in user_query.lower():
            analysis_results += "\nAnomaly Detection:\n"
            anomalies = self.detect_anomalies(df, value_col="value")
            analysis_results += anomalies.to_string() if not anomalies.empty else "No anomalies detected."
        
        if "correlation" in user_query.lower():
            analysis_results += "\nCorrelation Analysis:\n"
            analysis_results += self.correlation_analysis(df, col1="col1", col2="col2")
        
        if "moving average" in user_query.lower():
            analysis_results += "\nMoving Average Analysis:\n"
            df = self.moving_average(df, value_col="value")
            analysis_results += df.tail().to_string()
        
        insights = self.generate_insights(user_query, df)
        return f"{analysis_results}\n\nGPT Insights:\n{insights}"

# Example usage
if __name__ == "__main__":
    DB_URL = "postgresql://user:password@localhost/adventureworks"
    OPENAI_API_KEY = "your-openai-api-key"
    
    engine = AnalyticsEngine(DB_URL, OPENAI_API_KEY)
    query = "What are the monthly sales trends and anomalies for the last 3 years?"
    response = engine.process_query(query)
    print(response)
