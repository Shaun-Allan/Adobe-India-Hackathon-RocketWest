def extract_insights(summarizer, persona, task, paragraph, max_tokens=512):
    prompt = (
        f"Role: {persona}\n"
        f"Objective: {task}\n\n"
        "Use the following passage as background context. Generate a concise summary (max 100 words) "
        "in your own words. If the passage is repetitive or sparse, produce a brief summary capturing the key idea without inventing details. "
        "Avoid repetition and copying text verbatim.\n\n"
        f"Given Context Passage:\n{paragraph}\n\n"
        "Summary:"
    )
    result = summarizer(
        prompt,
        max_new_tokens=max_tokens,
        no_repeat_ngram_size=2,
        num_beams=4,
        do_sample=True,            # enable sampling so temperature matters
        temperature=0.7,
        early_stopping=True
    )[0]["generated_text"]



    return result







