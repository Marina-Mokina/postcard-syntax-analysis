import numpy as np
from typing import List, Dict
from backend.src.postcard_syntax_analyzer.syntax_constants import INFINITIVE_AUXILIARIES


class TextParser:
    """
    Responsible for parsing the text and providing raw syntactic features.
    """

    def __init__(self, text: str, nlp):
        self.text = text
        self.nlp = nlp
        self._sentences = []
        self._parsed = False

    def _parse(self):
        """Parse the text if not already done."""
        if self._parsed:
            return
        if not isinstance(self.text, str) or self.text.strip() == "":
            self._sentences = []
        else:
            doc = self.nlp(self.text)
            self._sentences = list(doc.sents) if doc.sents else [doc]
        self._parsed = True

    def _get_tree_depth(self, token, depth=0) -> int:
        """Compute the depth of the subtree rooted at token."""
        children = list(token.children)
        if not children:
            return depth + 1
        return 1 + max(self._get_tree_depth(child, depth) for child in children)

    def _get_amod_chain(self, token):
        """Count adjectives depending on the same parent."""
        parent = token.head
        chain = sum(1 for child in parent.children if child.dep_.lower() == 'amod')
        return max(1, chain)

    def get_tree_depth_raw(self) -> List[int]:
        """Depth of the syntactic tree for each sentence."""
        self._parse()
        if not self._sentences:
            return [1]
        res = []
        for sent in self._sentences:
            roots = [t for t in sent if t.head == t]
            if roots:
                res.append(self._get_tree_depth(roots[0]))
            else:
                res.append(1)
        return res

    def get_dep_distance_raw(self) -> List[int]:
        """Distance between token and its head for all tokens."""
        self._parse()
        if not self._sentences:
            return [0]
        res = []
        for sent in self._sentences:
            for token in sent:
                res.append(abs(token.i - token.head.i))
        return res

    def get_clauses_raw(self) -> List[int]:
        """
        Number of clauses per sentence.
        """
        self._parse()
        if not self._sentences:
            return [1]

        res = []
        for sent in self._sentences:
            clauses = 0
            for token in sent:
                if 'Inf' in token.morph.get('VerbForm', []):
                    continue

                dep = token.dep_.lower()
                if dep == 'advcl':
                    if 'Conv' in token.morph.get('VerbForm', []):
                        continue
                    else:
                        clauses += 1
                    continue

                if dep in {'root', 'ccomp', 'csubj', 'xcomp', 'acl:relcl'}:
                    clauses += 1
                    continue

                if dep == 'conj':
                    if token.pos_ in {'VERB', 'AUX'}:
                        has_subj = any(
                            child.dep_ in {'nsubj', 'nsubj:pass', 'csubj'} for child in token.children
                        )
                        if has_subj:
                            clauses += 1
                    elif token.pos_ in {'ADJ', 'ADV', 'NOUN'}:
                        clauses += 1
                    continue

            if clauses == 0 and len(sent) > 0:
                clauses = 1
            res.append(clauses)
        return res

    def get_amod_chain_raw(self) -> List[int]:
        """Length of adjective chains (one per amod token)."""
        self._parse()
        if not self._sentences:
            return [1]
        res = []
        for sent in self._sentences:
            for token in sent:
                if token.dep_.lower() == 'amod':
                    res.append(self._get_amod_chain(token))
        return res if res else [1]

    def get_advcl_count_per_sentence(self) -> List[int]:
        """Number of adverbial clauses (advcl) in each sentence."""
        self._parse()
        if not self._sentences:
            return [0]
        res = []
        for sent in self._sentences:
            cnt = sum(1 for token in sent if token.dep_.lower() == 'advcl')
            res.append(cnt)
        return res

    def get_participles_per_sentence(self) -> List[int]:
        """Number of participles (acl) in each sentence."""
        self._parse()
        if not self._sentences:
            return [0]
        res = []
        for sent in self._sentences:
            cnt = sum(1 for token in sent if token.dep_.lower() == 'acl')
            res.append(cnt)
        return res

    def get_relcl_per_sentence(self) -> List[int]:
        """Number of relative clauses (acl:relcl) in each sentence."""
        self._parse()
        if not self._sentences:
            return [0]
        res = []
        for sent in self._sentences:
            cnt = sum(1 for token in sent if token.dep_.lower() == 'acl:relcl')
            res.append(cnt)
        return res

    def get_verbal_adverbs_per_sentence(self) -> List[int]:
        """Number of verbal adverbs (gerunds, advcl + Conv) in each sentence."""
        self._parse()
        if not self._sentences:
            return [0]
        res = []
        for sent in self._sentences:
            cnt = sum(1 for token in sent
                      if token.dep_.lower() == 'advcl' and 'Conv' in token.morph.get('VerbForm', []))
            res.append(cnt)
        return res

    def get_ccomp_count_per_sentence(self) -> List[int]:
        """Number of clausal complements (ccomp) in each sentence."""
        self._parse()
        if not self._sentences:
            return [0]
        res = []
        for sent in self._sentences:
            cnt = sum(1 for token in sent if token.dep_.lower() == 'ccomp')
            res.append(cnt)
        return res

    def get_infinitive_phrases_per_sentence(self) -> List[int]:
        """
        Number of infinitive phrases per sentence.
        """
        self._parse()
        if not self._sentences:
            return [0]

        def has_chtoby_child(t):
            return any(child.dep_ == 'mark' and child.lemma_ == 'чтобы' for child in t.children)

        res = []
        for sent in self._sentences:
            infinitive_tokens = [
                token for token in sent
                if token.pos_ == 'VERB' and 'Inf' in token.morph.get('VerbForm', [])
            ]
            cnt = 0
            for token in infinitive_tokens:
                if token.dep_.lower() in ('csubj', 'nsubj'):
                    continue
                if token.head.lemma_ in INFINITIVE_AUXILIARIES:
                    continue
                if has_chtoby_child(token):
                    continue
                if token.dep_ == 'conj' and token.head in infinitive_tokens and has_chtoby_child(token.head):
                    continue
                cnt += 1
            res.append(cnt)
        return res

    def get_nmod_count_per_sentence(self) -> List[int]:
        """Number of nominal modifiers (nmod, nmod:poss) in each sentence."""
        self._parse()
        if not self._sentences:
            return [0]
        res = []
        for sent in self._sentences:
            cnt = sum(1 for token in sent if token.dep_.lower() in ('nmod', 'nmod:poss'))
            res.append(cnt)
        return res

    def get_predicate_units_per_sentence(self) -> List[int]:
        """The number of predicative units in each sentence according to Zolotova."""
        self._parse()
        if not self._sentences:
            return [0]
        clauses = self.get_clauses_raw()
        participles = self.get_participles_per_sentence()
        verbal_adverbs = self.get_verbal_adverbs_per_sentence()
        infinitive_phrases = self.get_infinitive_phrases_per_sentence()

        pu = []
        for i in range(len(self._sentences)):
            total = (clauses[i] + participles[i] + verbal_adverbs[i] + infinitive_phrases[i])
            pu.append(total)
        return pu


class SyntaxStats:
    """
    Computes statistics from raw features obtained from TextParser.
    """

    def __init__(self, parser: TextParser):
        self.parser = parser

    @staticmethod
    def _stats(values: List[float], label: str) -> Dict[str, float]:
        """Compute mean, median, max, std for a list of numbers."""
        if not values:
            return {f'{label}_mean': 0.0, f'{label}_median': 0.0, f'{label}_max': 0.0, f'{label}_std': 0.0}
        arr = np.array(values)
        return {
            f'{label}_mean': float(np.mean(arr)),
            f'{label}_median': float(np.median(arr)),
            f'{label}_max': float(np.max(arr)),
            f'{label}_std': float(np.std(arr, ddof=1) if len(arr) > 1 else 0.0)
        }

    def tree_depth_stats(self) -> Dict[str, float]:
        return self._stats(self.parser.get_tree_depth_raw(), 'tree_depth')

    def dep_distance_stats(self) -> Dict[str, float]:
        return self._stats(self.parser.get_dep_distance_raw(), 'dep_distance')

    def clauses_stats(self) -> Dict[str, float]:
        return self._stats(self.parser.get_clauses_raw(), 'clauses')

    def amod_chain_stats(self) -> Dict[str, float]:
        return self._stats(self.parser.get_amod_chain_raw(), 'amod_chain')

    def advcl_stats(self) -> Dict[str, float]:
        return self._stats(self.parser.get_advcl_count_per_sentence(), 'advcl')

    def participles_stats(self) -> Dict[str, float]:
        return self._stats(self.parser.get_participles_per_sentence(), 'participles')

    def relcl_stats(self) -> Dict[str, float]:
        return self._stats(self.parser.get_relcl_per_sentence(), 'relcl')

    def verbal_adverbs_stats(self) -> Dict[str, float]:
        return self._stats(self.parser.get_verbal_adverbs_per_sentence(), 'verbal_adverbs')

    def ccomp_stats(self) -> Dict[str, float]:
        return self._stats(self.parser.get_ccomp_count_per_sentence(), 'ccomp')

    def infinitive_phrases_stats(self) -> Dict[str, float]:
        return self._stats(self.parser.get_infinitive_phrases_per_sentence(), 'infinitive_phrases')

    def nmod_stats(self) -> Dict[str, float]:
        return self._stats(self.parser.get_nmod_count_per_sentence(), 'nmod')

    def info_density_stats(self) -> Dict[str, float]:
        """Information density statistics."""
        values = self.parser.get_predicate_units_per_sentence()
        return self._stats(values, 'info_density')

    def all_stats(self) -> Dict[str, float]:
        """Collect statistics for all features into one dictionary."""
        stats = {}
        stats.update(self.tree_depth_stats())
        stats.update(self.dep_distance_stats())
        stats.update(self.clauses_stats())
        stats.update(self.amod_chain_stats())
        stats.update(self.advcl_stats())
        stats.update(self.participles_stats())
        stats.update(self.relcl_stats())
        stats.update(self.verbal_adverbs_stats())
        stats.update(self.ccomp_stats())
        stats.update(self.infinitive_phrases_stats())
        stats.update(self.nmod_stats())
        stats.update(self.info_density_stats())
        return stats


class TextSyntaxAnalyzer:
    """
    Facade that combines the parser and statistics for easy use.
    """

    def __init__(self, text: str, nlp):
        self.parser = TextParser(text, nlp)
        self.stats = SyntaxStats(self.parser)

    def get_tree_depth_raw(self) -> List[int]:
        return self.parser.get_tree_depth_raw()

    def get_dep_distance_raw(self) -> List[int]:
        return self.parser.get_dep_distance_raw()

    def get_clauses_raw(self) -> List[int]:
        return self.parser.get_clauses_raw()

    def get_amod_chain_raw(self) -> List[int]:
        return self.parser.get_amod_chain_raw()

    def get_advcl_count_raw(self) -> int:
        """Return total number of advcl (legacy, but kept)."""
        return sum(self.parser.get_advcl_count_per_sentence())

    def get_participles_raw(self) -> int:
        return sum(self.parser.get_participles_per_sentence())

    def get_relcl_raw(self) -> int:
        return sum(self.parser.get_relcl_per_sentence())

    def get_verbal_adverbs_raw(self) -> int:
        return sum(self.parser.get_verbal_adverbs_per_sentence())

    def get_ccomp_count_raw(self) -> int:
        return sum(self.parser.get_ccomp_count_per_sentence())

    def get_infinitive_phrases_raw(self) -> int:
        return sum(self.parser.get_infinitive_phrases_per_sentence())

    def get_nmod_count_raw(self) -> int:
        return sum(self.parser.get_nmod_count_per_sentence())

    def get_all_stats(self) -> Dict[str, float]:
        return self.stats.all_stats()
