import re
import time
import nltk
from langchain_huggingface import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag


###########################
# Ensure NLTK resources
###########################


def ensure_nltk_resources():
    resources = [
        ("tokenizers/punkt", "punkt"),
        ("corpora/stopwords", "stopwords"),
        ("taggers/averaged_perceptron_tagger", "averaged_perceptron_tagger"),
    ]
    for res_id, download_name in resources:
        try:
            nltk.data.find(res_id)
        except LookupError:
            print(f"Downloading missing NLTK resource: {download_name}")
            nltk.download(download_name)


ensure_nltk_resources()


###########################
# Functions
###########################


def extract_keywords_from_query(query):
    stop_words = set(stopwords.words("english"))
    try:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query is empty or not a string")

        # Try word_tokenize; fallback to simple split if punkt_tab is missing or LookupError occurs
        try:
            tokens = word_tokenize(query.lower())
        except LookupError as e:
            if "punkt_tab" in str(e):
                print("⚠️ punkt_tab tokenizer resource not found, falling back to whitespace split.")
                tokens = query.lower().split()
            else:
                raise

        if not tokens:
            raise ValueError("Tokenization resulted in empty list")

        tags = pos_tag(tokens)
        keywords = [
            word for word, tag in tags
            if tag.startswith(('NN', 'VB', 'JJ')) and word not in stop_words
        ]
        if keywords:
            return set(keywords)

        raise ValueError("No keywords extracted from POS tagging")

    except Exception as e:
        print(f"⚠️ Failed to extract keywords with POS tagging: {e}. Falling back to regex.")
        # Expanded common words: stopwords + typical question words + generic connectors
        common_words = {
            # Standard question words
            "what", "which", "when", "where", "who", "whose", "whom", "how", "why",
            # Modal/accompanying verbs and helpers
            "should", "would", "could", "might", "may", "will", "shall", "can", "must", "did",
            "does", "do", "is", "are", "was", "were", "be", "being", "been", "have", "has",
            "had", "having",
            # Pronouns
            "i", "me", "my", "mine", "we", "us", "our", "ours", "you", "your", "yours", "he",
            "him", "his", "she", "her", "hers", "it", "its", "they", "them", "their", "theirs",
            # Articles, prepositions, conjunctions, and common 'filler'
            "the", "a", "an", "and", "or", "if", "but", "because", "as", "while", "of", "to",
            "for", "about", "with", "on", "in", "out", "by", "at", "from", "up", "down", "off",
            "over", "under", "into", "above", "below", "through", "during", "before", "after",
            "between", "without", "within", "along", "across", "among", "against", "also",
            "however", "so", "just", "than", "then", "now", "there", "here", "thus", "yet",
            "still", "even", "very", "maybe", "perhaps",
            # Other possible fillers
            "need", "want", "let",
            # Generic context/meaningless words
            "query", "include", "including", "includes", "any", "every", "each", "all",
            "some", "other", "such"
        }
        # Use regex to extract words with length >= 4 to reduce noise
        raw_keywords = set(
            w for w in re.findall(r'\b[a-z]{4,}\b', query.lower())
            if w not in common_words
        )
        return raw_keywords


def soft_scale(score, low=0.50, high=0.75):
    # Scales score linearly between low and high to [0,1], clamps to [0,1]
    return max(0.0, min(1.0, (score - low) / (high - low)))


def keyword_score(text, dynamic_keywords):
    # Count how many keywords appear in text, normalized by keyword count
    text = text.lower()
    hits = sum(1 for kw in dynamic_keywords if re.search(rf"\b{re.escape(kw)}\b", text))
    return hits / max(len(dynamic_keywords), 1)


def score_chunks(query, chunks, model_path, threshold):
    embeddings = HuggingFaceEmbeddings(model_name=model_path)
    query_emb = embeddings.embed_query(query)
    chunk_embs = embeddings.embed_documents(chunks)
    cosine_scores = cosine_similarity([query_emb], chunk_embs)[0]

    dynamic_keywords = extract_keywords_from_query(query)
    print(f"\n🔍 Extracted Keywords: {sorted(dynamic_keywords)}\n")

    ranked_chunks = []

    for chunk, cosine in zip(chunks, cosine_scores):
        start_time = time.time()

        kw_score = keyword_score(chunk, dynamic_keywords)
        scaled_cosine = soft_scale(cosine)

        if cosine < threshold:
            continue

        final_score = 0.6 * scaled_cosine + 0.4 * kw_score
        elapsed_time = time.time() - start_time

        ranked_chunks.append((chunk, final_score, cosine, scaled_cosine, kw_score, elapsed_time))

    return sorted(ranked_chunks, key=lambda x: x[1], reverse=True)
