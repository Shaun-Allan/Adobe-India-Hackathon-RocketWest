import json
import os
import time
import warnings
from collections import defaultdict
from datetime import datetime
from statistics import mean

from tqdm import tqdm
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

from config import (
    EMBEDDING_PATH,
    JOB_PERFORMER_PATH,
    COSINE_THRESHOLD,
    DROP_RATIO,
    MAX_SECTIONS
)
from score import score_chunks  
from summary import extract_insights


# Suppress future warnings (like from PyTorch)
warnings.simplefilter(action='ignore', category=FutureWarning)


# --- CHUNKING UTIL ---
def split_into_chunks(text, max_tokens=500):
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_tokens):
        chunk = ' '.join(words[i:i + max_tokens])
        chunks.append(chunk)
    return chunks


# --- LOAD + CHUNK SECTIONS ---
def load_section_chunks(documents, outline_dir="outlines", max_tokens=500):
    chunk_list = []
    for doc in documents:
        filename = doc['filename']
        outline_path = os.path.join(outline_dir, filename.replace('.pdf', '.json'))

        if not os.path.exists(outline_path):
            print(f"⚠️ Warning: Outline not found for {filename}")
            continue

        with open(outline_path, 'r', encoding='utf-8') as f:
            doc_data = json.load(f)

        for section in doc_data.get("outline", []):
            section_text = section.get('text_content', "")
            if not section_text:
                continue  # Skip sections without text content

            chunk_texts = split_into_chunks(section_text, max_tokens=max_tokens)
            for idx, chunk_text in enumerate(chunk_texts):
                chunk_list.append({
                    'document': filename,
                    'section_title': section['text'],
                    'page_number': section.get('page', 1),
                    'chunk_text': chunk_text
                })

    return chunk_list


# --- Summarization Model Loading and Wrapper ---

def load_summarizer(local_path):
    tokenizer = AutoTokenizer.from_pretrained(local_path, local_files_only=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(local_path, local_files_only=True)
    summarizer_pipeline = pipeline("text2text-generation", model=model, tokenizer=tokenizer)
    return summarizer_pipeline



# --- MAIN PIPELINE ---
def main():
    # Step 1: Load input spec
    with open("/app/input/input.json", "r", encoding="utf-8") as f:
        input_data = json.load(f)

    documents = input_data["documents"]
    persona = input_data["persona"]["role"]
    task = input_data["job_to_be_done"]["task"]

    # Step 2: Chunk sections
    chunks = load_section_chunks(documents)
    if not chunks:
        print("❌ No chunks extracted. Exiting.")
        return

    print(f"✅ Loaded {len(chunks)} chunks across {len(documents)} documents.\n")

    # Step 3: Prepare input for scoring
    chunk_texts = [c["chunk_text"] for c in chunks]

    # Start timing for scoring/ranking
    start_rank_time = time.time()
    scored_output = score_chunks(query=task, chunks=chunk_texts, model_path=EMBEDDING_PATH, threshold=COSINE_THRESHOLD)
    end_rank_time = time.time()
    # print(f"⏱️ Ranking (embedding + scoring) completed in {end_rank_time - start_rank_time:.2f} seconds.\n")

    # Step 4: Map scores back to metadata
    scored_chunks = []
    scored_text_map = {score[0]: score for score in scored_output}

    for c in tqdm(chunks, desc="Mapping scores to chunks"):
        text = c["chunk_text"]
        if text in scored_text_map:
            score_data = scored_text_map[text]
            c.update({
                "score": score_data[1],  # final_score
                "cosine_similarity": score_data[2],
                "keyword_score": score_data[4]
            })
            scored_chunks.append(c)

    print(f"✅ Retained {len(scored_chunks)} scored chunks after filtering threshold.\n")

    # Step 5: Group by (document, section_title)
    sections = defaultdict(lambda: {
        'document': '',
        'section_title': '',
        'page_number': 0,
        'scores': [],
        'chunks': []
    })

    for c in tqdm(scored_chunks, desc="Grouping chunks into sections"):
        key = (c['document'], c['section_title'])
        s = sections[key]
        s['document'] = c['document']
        s['section_title'] = c['section_title']
        s['page_number'] = c['page_number']
        s['chunks'].append(c)
        s['scores'].append(c['score'])

    # Step 6: Average scores per section
    for s in sections.values():
        s["avg_score"] = mean(s["scores"]) if s["scores"] else 0.0

    # Step 7: Dynamic selection of top sections based on score gaps
    sorted_sections = sorted(sections.values(), key=lambda x: x["avg_score"], reverse=True)
    avg_scores = [s["avg_score"] for s in sorted_sections]

    if avg_scores:
        max_score = avg_scores[0]
        threshold = DROP_RATIO * max_score

        cutoff_idx = len(avg_scores)  # default to all if no big drop
        for i in range(len(avg_scores) - 1):
            diff = avg_scores[i] - avg_scores[i + 1]
            if diff > threshold:
                cutoff_idx = i + 1
                break

        cutoff_idx = min(cutoff_idx, MAX_SECTIONS)
        top_sections = sorted_sections[:cutoff_idx]
    else:
        top_sections = []

    # Assign importance rank
    for i, section in enumerate(top_sections, 1):
        section["importance_rank"] = i

    # Load summarizer model once
    summarizer = load_summarizer(JOB_PERFORMER_PATH)

    # Step 8: Extract insights from chunks of selected sections
    subsection_analysis = []

    # Start timing for insights extraction
    start_analysis_time = time.time()

    for section in tqdm(top_sections, desc="Extracting insights from top sections"):
        for chunk in section["chunks"]:
            refined = extract_insights(
                summarizer=summarizer,
                persona=persona,
                task=task,
                paragraph=chunk["chunk_text"]
            )
            subsection_analysis.append({
                "document": section["document"],
                "section_title": section["section_title"],
                "refined_text": refined.strip(),
                "page_number": section["page_number"]
            })

    end_analysis_time = time.time()
    

    # Step 9: Write output
    output = {
        "metadata": {
            "input_documents": [doc["filename"] for doc in documents],
            "persona": persona,
            "job_to_be_done": task,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": [
            {
                "document": section["document"],
                "section_title": section["section_title"],
                "importance_rank": section["importance_rank"],
                "page_number": section["page_number"]
            } for section in top_sections
        ],
        "subsection_analysis": subsection_analysis
    }

    os.makedirs("output", exist_ok=True)
    with open("output/output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("✅ Final output written to: output/output.json")


if __name__ == "__main__":
    main()