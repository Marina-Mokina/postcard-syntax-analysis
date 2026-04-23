import pandas as pd
import spacy
from pathlib import Path
from backend.src.postcard_syntax_analyzer.dataframe_processor import process_dataframe


def main():
    """
    Load the dataset, process texts, and save the resulting syntax features.
    """
    nlp = spacy.load("ru_core_news_lg")
    project_root = Path(__file__).parent.parent
    data_path = project_root / 'data' / 'postcard_filtered.csv'
    df = pd.read_csv(data_path)
    df_result = process_dataframe(df, 'Текст открытки', nlp)
    df_result.to_csv(project_root / 'data' / 'syntax_features.csv', index=False, encoding='utf-8')


if __name__ == "__main__":
    main()
