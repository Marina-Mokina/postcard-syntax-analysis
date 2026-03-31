import pandas as pd
from backend.src.postcard_syntax_analyzer.syntax_analyzer import TextSyntaxAnalyzer


def process_dataframe(df: pd.DataFrame, text_column: str, nlp) -> pd.DataFrame:
    """
    Apply TextSyntaxAnalyzer to each row of the dataframe.
    """
    total = len(df)
    stats_list = []

    for i, text in enumerate(df[text_column]):
        analyzer = TextSyntaxAnalyzer(text, nlp)
        stats_list.append(analyzer.get_all_stats())
        if (i + 1) % 1000 == 0:
            print(f"Processed {i + 1}/{total} texts")

    stats_df = pd.DataFrame(stats_list)
    return pd.concat([df.reset_index(drop=True), stats_df.reset_index(drop=True)], axis=1)
