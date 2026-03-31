import pandas as pd
import spacy
from backend.src.postcard_syntax_analyzer.dataframe_processor import process_dataframe


def main():
    """
    Load the dataset, process texts, and save the resulting syntax features.
    """
    nlp = spacy.load("ru_core_news_lg")
    df = pd.read_csv("../data/postcard_filtred.csv")
    df_result = process_dataframe(df, 'Текст открытки', nlp)
    df_result.to_csv("data/syntax_features.csv", index=False, encoding='utf-8')


if __name__ == "__main__":
    main()
