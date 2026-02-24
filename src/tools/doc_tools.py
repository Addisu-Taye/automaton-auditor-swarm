"""
src/tools/doc_tools.py

Document Analysis Tools for PDF Ingestion and Cross-Reference
Production Module - Automaton Auditor Swarm v3.0.0

Capabilities:
- PDF ingestion with page-level text extraction
- Chunked querying for large documents (RAG-lite approach)
- Theoretical depth analysis (keyword search with context)
- File path extraction for cross-reference verification
- Hallucination detection (claimed paths vs. actual repo structure)

Compliance:
- Protocol A.2: Theoretical Depth verification
- Protocol A.2: Report Accuracy (Cross-Reference)
- Protocol B: Fact Supremacy rule enforcement
"""

import os
import re
from typing import List, Dict, Any, Optional
from pypdf import PdfReader


# =============================================================================
# PDF INGESTION TOOLS
# =============================================================================

def ingest_pdf(path: str) -> Dict[str, Any]:
    """
    Security Protocol: Parse PDF and extract text with metadata.
    
    Rationale:
    - RAG-lite approach: Don't dump entire document into context
    - Chunk by page for targeted querying
    - Extract metadata for forensic analysis
    
    Args:
        path: Absolute or relative path to PDF file
        
    Returns:
        Dictionary containing parsed document structure
        
    Compliance:
    - Protocol A.2: Theoretical Depth evidence collection
    - Protocol A.2: Host Analysis Accuracy verification
    """
    if not os.path.exists(path):
        return {
            "success": False,
            "error": "PDF_NOT_FOUND",
            "path": path,
            "message": f"Document not found at specified path: {path}"
        }
    
    try:
        reader = PdfReader(path)
        pages = []
        total_chars = 0
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                char_count = len(text)
                total_chars += char_count
                pages.append({
                    "page_number": i + 1,
                    "content": text,
                    "char_count": char_count,
                    "word_count": len(text.split())
                })
        
        return {
            "success": True,
            "path": path,
            "filename": os.path.basename(path),
            "total_pages": len(pages),
            "total_chars": total_chars,
            "total_words": sum(p["word_count"] for p in pages),
            "pages": pages,
            "metadata": {
                "num_pages": len(reader.pages),
                "is_encrypted": reader.is_encrypted
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": "PDF_PARSE_ERROR",
            "path": path,
            "message": str(e)
        }


def chunk_document(doc: Dict[str, Any], chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
    """
    Chunk document for RAG-lite querying.
    
    Rationale:
    - Large PDFs exceed LLM context windows
    - Chunking enables targeted evidence retrieval
    - Overlap preserves context across chunk boundaries
    
    Args:
        doc: Parsed document from ingest_pdf()
        chunk_size: Target characters per chunk
        overlap: Character overlap between chunks
        
    Returns:
        List of chunk dictionaries with metadata
    """
    if not doc.get("success"):
        return []
    
    chunks = []
    full_text = "\n\n".join([p["content"] for p in doc.get("pages", [])])
    
    if len(full_text) <= chunk_size:
        return [{
            "chunk_id": 0,
            "content": full_text,
            "char_count": len(full_text),
            "start_char": 0,
            "end_char": len(full_text),
            "source_pages": [p["page_number"] for p in doc.get("pages", [])]
        }]
    
    start = 0
    chunk_id = 0
    
    while start < len(full_text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(full_text):
            last_period = full_text.rfind(".", start, end)
            last_newline = full_text.rfind("\n", start, end)
            break_point = max(last_period, last_newline)
            if break_point > start + (chunk_size // 2):
                end = break_point + 1
        
        chunk_content = full_text[start:end]
        
        # Determine which pages this chunk spans
        char_count = 0
        source_pages = []
        for page in doc.get("pages", []):
            page_start = char_count
            page_end = char_count + page["char_count"]
            if start < page_end and end > page_start:
                source_pages.append(page["page_number"])
            char_count = page_end
        
        chunks.append({
            "chunk_id": chunk_id,
            "content": chunk_content,
            "char_count": len(chunk_content),
            "start_char": start,
            "end_char": end,
            "source_pages": source_pages
        })
        
        start = end - overlap
        chunk_id += 1
    
    return chunks


# =============================================================================
# THEORETICAL DEPTH ANALYSIS
# =============================================================================

def search_document_terms(doc: Dict[str, Any], keywords: List[str]) -> Dict[str, Any]:
    """
    Forensic Protocol: Search for theoretical concepts in document.
    
    Evidence Class: Theoretical Depth (Protocol A.2)
    Success Pattern: Terms appear in substantive architectural explanations
    Failure Pattern: Terms appear only in executive summary (keyword dropping)
    
    Args:
        doc: Parsed document from ingest_pdf()
        keywords: List of terms to search for
        
    Returns:
        Dictionary containing search results with context
    """
    if not doc.get("success"):
        return {
            "success": False,
            "error": doc.get("error", "UNKNOWN_ERROR"),
            "findings": {}
        }
    
    findings = {}
    
    for keyword in keywords:
        matches = []
        
        for page in doc.get("pages", []):
            content = page["content"]
            # Case-insensitive search
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            
            for match in pattern.finditer(content):
                # Extract context (150 chars before and after)
                start = max(0, match.start() - 150)
                end = min(len(content), match.end() + 150)
                context = content[start:end]
                
                matches.append({
                    "page": page["page_number"],
                    "position": match.start(),
                    "context": f"...{context}...",
                    "surrounding_words": context.split()[:20]  # First 20 words for quick scan
                })
        
        findings[keyword] = {
            "found": len(matches) > 0,
            "count": len(matches),
            "matches": matches,
            "depth_score": _calculate_depth_score(matches)
        }
    
    return {
        "success": True,
        "keywords_searched": keywords,
        "findings": findings,
        "overall_depth_score": sum(f["depth_score"] for f in findings.values()) / len(findings) if findings else 0
    }


def _calculate_depth_score(matches: List[Dict[str, Any]]) -> int:
    """
    Calculate theoretical depth score based on match quality.
    
    Scoring:
    - 0: Not found
    - 1: Found but only in summary/intro (keyword dropping)
    - 2: Found in architectural explanation with implementation details
    - 3: Found with code references and cross-references
    
    Args:
        matches: List of match dictionaries from search_document_terms()
        
    Returns:
        Depth score (0-3)
    """
    if not matches:
        return 0
    
    score = 1  # Base score for finding the term
    
    for match in matches:
        context = match["context"].lower()
        
        # Check for implementation details
        implementation_indicators = [
            "implement", "architecture", "design", "pattern",
            "src/", ".py", "code", "function", "class",
            "graph", "node", "edge", "state", "reducer"
        ]
        
        for indicator in implementation_indicators:
            if indicator in context:
                score = max(score, 2)
                break
        
        # Check for code references
        code_patterns = [
            r"src/[a-zA-Z0-9_/\.]+",
            r"\.py",
            r"def\s+\w+",
            r"class\s+\w+",
            r"operator\.(add|ior)"
        ]
        
        for pattern in code_patterns:
            if re.search(pattern, context):
                score = max(score, 3)
                break
    
    return score


# =============================================================================
# CROSS-REFERENCE VERIFICATION
# =============================================================================

def extract_file_paths(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Forensic Protocol: Extract file paths mentioned in document.
    
    Evidence Class: Report Accuracy (Protocol A.2)
    Used for cross-reference verification with RepoInvestigator.
    
    Args:
        doc: Parsed document from ingest_pdf()
        
    Returns:
        Dictionary containing extracted paths with locations
    """
    if not doc.get("success"):
        return {
            "success": False,
            "error": doc.get("error", "UNKNOWN_ERROR"),
            "paths": []
        }
    
    # Pattern matches: src/nodes/judges.py, src/tools/repo_tools.py, etc.
    path_pattern = r'src/[a-zA-Z0-9_/\.]+'
    
    extracted_paths = []
    
    for page in doc.get("pages", []):
        content = page["content"]
        matches = re.findall(path_pattern, content)
        
        for match in matches:
            # Normalize path (remove trailing punctuation)
            normalized = match.rstrip('.,;:)]}')
            if normalized not in [p["path"] for p in extracted_paths]:
                extracted_paths.append({
                    "path": normalized,
                    "page": page["page_number"],
                    "context": _get_path_context(content, match)
                })
    
    return {
        "success": True,
        "total_paths": len(extracted_paths),
        "paths": extracted_paths,
        "unique_files": list(set(p["path"] for p in extracted_paths))
    }


def _get_path_context(content: str, path: str, context_chars: int = 100) -> str:
    """
    Extract context around a file path mention.
    
    Args:
        content: Page content
        path: File path found in content
        context_chars: Characters to extract before and after
        
    Returns:
        Context string showing how path is referenced
    """
    idx = content.find(path)
    if idx == -1:
        return ""
    
    start = max(0, idx - context_chars)
    end = min(len(content), idx + len(path) + context_chars)
    
    return f"...{content[start:end]}..."


def verify_claimed_paths(claimed_paths: List[str], repo_file_tree: List[str]) -> Dict[str, Any]:
    """
    Forensic Protocol: Cross-reference claimed paths against actual repo structure.
    
    Evidence Class: Report Accuracy (Protocol A.2)
    Success Pattern: All claimed paths exist in repo
    Failure Pattern: Hallucinated paths (claimed but don't exist)
    
    Args:
        claimed_paths: List of file paths mentioned in PDF report
        repo_file_tree: List of actual files in repository (from RepoInvestigator)
        
    Returns:
        Dictionary containing verification results
    """
    verified = []
    hallucinated = []
    
    for claimed in claimed_paths:
        # Normalize paths for comparison
        claimed_normalized = claimed.strip('/').lower()
        
        found = False
        for actual in repo_file_tree:
            actual_normalized = actual.strip('/').lower()
            if claimed_normalized == actual_normalized or claimed_normalized in actual_normalized:
                verified.append({
                    "claimed": claimed,
                    "actual": actual,
                    "status": "VERIFIED"
                })
                found = True
                break
        
        if not found:
            hallucinated.append({
                "claimed": claimed,
                "status": "HALLUCINATED",
                "rationale": "File path mentioned in report does not exist in repository"
            })
    
    return {
        "success": True,
        "total_claimed": len(claimed_paths),
        "verified_count": len(verified),
        "hallucinated_count": len(hallucinated),
        "accuracy_score": len(verified) / len(claimed_paths) if claimed_paths else 1.0,
        "verified_paths": verified,
        "hallucinated_paths": hallucinated
    }


# =============================================================================
# THEORETICAL CONCEPT VERIFICATION
# =============================================================================

def verify_theoretical_depth(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Forensic Protocol: Comprehensive theoretical depth analysis.
    
    Evidence Class: Theoretical Depth (Protocol A.2)
    Searches for key architectural concepts per rubric v3.0.0.
    
    Args:
        doc: Parsed document from ingest_pdf()
        
    Returns:
        Dictionary containing depth analysis results
    """
    # Key terms per rubric v3.0.0 Protocol A.2
    key_terms = [
        "Dialectical Synthesis",
        "Fan-In",
        "Fan-Out",
        "Metacognition",
        "State Synchronization",
        "Pydantic",
        "operator.add",
        "operator.ior",
        "StateGraph",
        "Parallel Execution"
    ]
    
    search_results = search_document_terms(doc, key_terms)
    
    # Categorize findings
    deep_understanding = []
    surface_mentions = []
    not_found = []
    
    for term, result in search_results.get("findings", {}).items():
        if not result["found"]:
            not_found.append(term)
        elif result["depth_score"] >= 2:
            deep_understanding.append({
                "term": term,
                "count": result["count"],
                "depth_score": result["depth_score"]
            })
        else:
            surface_mentions.append({
                "term": term,
                "count": result["count"],
                "depth_score": result["depth_score"],
                "warning": "Keyword dropping detected - term appears without implementation details"
            })
    
    return {
        "success": search_results.get("success", False),
        "terms_searched": key_terms,
        "deep_understanding": deep_understanding,
        "surface_mentions": surface_mentions,
        "not_found": not_found,
        "overall_depth_score": search_results.get("overall_depth_score", 0),
        "assessment": _generate_depth_assessment(deep_understanding, surface_mentions, not_found)
    }


def _generate_depth_assessment(deep: List, surface: List, not_found: List) -> str:
    """
    Generate human-readable assessment of theoretical depth.
    
    Args:
        deep: Terms with deep understanding
        surface: Terms with surface mentions only
        not_found: Terms not found
        
    Returns:
        Assessment string
    """
    if len(deep) >= 6:
        return "EXCELLENT: Document demonstrates comprehensive understanding of architectural concepts with implementation details."
    elif len(deep) >= 3:
        return "GOOD: Document shows solid understanding of key concepts, though some terms lack implementation context."
    elif len(deep) >= 1 or len(surface) >= 3:
        return "MODERATE: Document mentions key terms but lacks substantive architectural explanations. Risk of keyword dropping."
    else:
        return "INSUFFICIENT: Document lacks theoretical depth. Key architectural concepts are missing or superficial."


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_document_statistics(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract document statistics for forensic analysis.
    
    Args:
        doc: Parsed document from ingest_pdf()
        
    Returns:
        Dictionary containing document statistics
    """
    if not doc.get("success"):
        return {"success": False, "error": doc.get("error")}
    
    pages = doc.get("pages", [])
    
    return {
        "success": True,
        "total_pages": doc.get("total_pages", 0),
        "total_chars": doc.get("total_chars", 0),
        "total_words": doc.get("total_words", 0),
        "avg_chars_per_page": doc.get("total_chars", 0) / max(1, doc.get("total_pages", 1)),
        "avg_words_per_page": doc.get("total_words", 0) / max(1, doc.get("total_pages", 1)),
        "is_encrypted": doc.get("metadata", {}).get("is_encrypted", False)
    }