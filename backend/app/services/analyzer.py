import re
import spacy
from dataclasses import dataclass, field


@dataclass
class AnalysisResult:
    is_question: bool = False
    keywords: list = field(default_factory=list)
    action_items: list = field(default_factory=list)


QUESTION_STARTERS = re.compile(
    r"^(who|what|when|where|why|how|which|whose|whom"
    r"|is|are|was|were|do|does|did|have|has|had"
    r"|can|could|will|would|should|shall|may|might"
    r"|aren't|isn't|wasn't|weren't|don't|doesn't|didn't)\b",
    re.IGNORECASE
)

ACTION_PATTERNS = [
    re.compile(r"\b(will|going to|needs? to|should|must|have to|has to)\s+\w+", re.IGNORECASE),
    re.compile(r"\b(action item|todo|follow[- ]up|next step)[s]?\b", re.IGNORECASE),
    re.compile(r"\b(let['s]*|please)\s+\w+", re.IGNORECASE),
    re.compile(r"\bremind\b.{0,40}", re.IGNORECASE),
]

STOPWORDS = {
    "i", "me", "my", "we", "our", "you", "your", "he", "she", "they",
    "it", "its", "the", "a", "an", "and", "or", "but", "in", "on",
    "at", "to", "for", "of", "with", "that", "this", "is", "are",
    "was", "were", "be", "been", "have", "has", "had", "do", "does",
    "did", "will", "would", "could", "should", "may", "might", "just",
    "like", "know", "think", "so", "okay", "yeah", "um", "uh",
}


class TextAnalyzer:

    def __init__(self):
        self.nlp = None
        self.is_ready = False

    def load(self):
        print("⏳ Loading spacy NLP model...")
        self.nlp = spacy.load("en_core_web_sm")
        self.is_ready = True
        print("✅ NLP model ready.")

    def analyze(self, text: str) -> AnalysisResult:
        if not text or not text.strip():
            return AnalysisResult()
        text = text.strip()
        return AnalysisResult(
            is_question=self.detect_question(text),
            keywords=self.extract_keywords(text),
            action_items=self.detect_action_items(text),
        )

    def detect_question(self, text: str) -> bool:
        if text.endswith("?"):
            return True
        if QUESTION_STARTERS.match(text):
            return True
        if self.is_ready:
            doc = self.nlp(text[:100])
            for token in doc[:5]:
                if token.tag_ in ("WDT", "WP", "WP$", "WRB"):
                    return True
        return False

    def extract_keywords(self, text: str) -> list:
        if not self.is_ready:
            words = re.findall(r'\b[a-zA-Z]{4,}\b', text)
            return [w for w in words if w.lower() not in STOPWORDS][:5]

        doc = self.nlp(text)
        keywords = set()

        for ent in doc.ents:
            kw = ent.text.strip().lower()
            if len(kw) > 2 and kw not in STOPWORDS:
                keywords.add(ent.text.strip())

        for chunk in doc.noun_chunks:
            root = chunk.root.text.strip().lower()
            if len(root) > 3 and root not in STOPWORDS:
                keywords.add(chunk.root.text.strip())

        return list(keywords)[:5]

    def detect_action_items(self, text: str) -> list:
        for pattern in ACTION_PATTERNS:
            if pattern.search(text):
                return [text.strip()]
        return []


text_analyzer = TextAnalyzer()