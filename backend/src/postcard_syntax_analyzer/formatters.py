from backend.src.postcard_syntax_analyzer.syntax_analyzer import TextSyntaxAnalyzer


def simplify_stats(analyzer: TextSyntaxAnalyzer) -> dict:
    """
    Return a simplified dictionary of key syntax metrics.
    """
    stats = analyzer.get_all_stats()
    return {
        "Средняя глубина предложений": round(stats.get("tree_depth_mean", 0), 2),
        "Среднее расстояние зависимостей": round(stats.get("dep_distance_mean", 0), 2),
        "Среднее количество клауз": round(stats.get("clauses_mean", 0), 2),
        "Максимальная длина цепочки прилагательных": int(stats.get("amod_chain_max", 0)),
        "Количество обстоятельственных придаточных": analyzer.get_advcl_count_raw(),
        "Количество определительных придаточных": analyzer.get_relcl_raw(),
        "Количество изъяснительных придаточных": analyzer.get_ccomp_count_raw(),
        "Количество причастий": analyzer.get_participles_raw(),
        "Количество деепричастий": analyzer.get_verbal_adverbs_raw(),
        "Количество инфинитивных оборотов": analyzer.get_infinitive_phrases_raw(),
        "Количество предложных определений": analyzer.get_nmod_count_raw(),
    }
