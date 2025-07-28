# ⚠️ NOTE: THIS REPOSITORY INCLUDES MODEL FILES OVER 100MB, WHICH EXCEEDS GIT'S SIZE LIMITS AND MAY CAUSE CLONING ISSUES.  
TO CLONE SUCCESSFULLY, PLEASE ENSURE YOU HAVE GIT LFS INSTALLED AND INITIALIZED BEFORE CLONING.

#### To set up Git LFS, run the following commands before cloning:

```
# Install Git LFS (if not already installed)
# For example, on Ubuntu: sudo apt install git-lfs
# On Mac: brew install git-lfs

# Initialize Git LFS
git lfs install

# Now clone the repo as usual
git clone 
```

This ensures all large files are retrieved correctly and avoids issues with size limits.

---

# RocketWest Submission -- Adobe India Hackathon (Connecting the Dots)

## 📂 Repo Structure

This repo contains code and solution approaches for two major challenges:

| Directory         | Content Summary |
|-------------------|-----------------|
| `Challenge_1a/`   | Core PDF processing and structured data extraction. Dockerized pipeline for parsing and organizing PDF section hierarchy efficiently. See the folder for a detailed README with setup and usage instructions. |
| `Challenge_1b/`   | Advanced persona-based content analysis across multiple document collections—focused on cross-document intelligence, contextual linking, and multi-source insights. Check the folder for a detailed README covering the implementation and use cases. |

### Challenge 1a — Core PDF Processing

- Extracts outlines and structure from raw PDFs.
- Implements clean, modular pipeline for **fast parsing** and **section hierarchy identification**.
- Suitable for adapting into on-device intelligence modules or scalable backend processing.
- Includes Docker configuration for easy deployment.

*Go to `Challenge_1a/` to explore the code, detailed documentation, and deployment steps.*

### Challenge 1b — Multi-Collection Analysis

- Builds on 1a by analyzing multiple PDF collections.
- Showcases persona-based content recommendations (contextual insights tailored to user profile/intent).
- Demonstrates semantic linking across **multiple** documents, not just within a single PDF.
- Extendable for building recommendation engines or advanced digital library assistants.

*Navigate to `Challenge_1b/` for detailed explanations, walkthroughs, and demos.*

