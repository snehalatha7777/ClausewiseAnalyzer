import streamlit as st
import pdfplumber
import json
import re
st.set_page_config(page_title="Clausewise Legal Analyzer", layout="wide")

st.title("Clausewise Legal Analyzer – Demo")
st.write("Upload a contract (PDF or TXT) or paste text to extract clauses and run simple risk checks.")

# Upload PDF/TXT or paste text
uploaded_file = st.file_uploader("Upload PDF/TXT", type=["pdf", "txt"])
text_input = st.text_area("Or paste contract text here...", height=200)

# Sample button
if st.button("Load Sample"):
    text_input = """1. Confidentiality. The Vendor shall maintain the confidentiality of all Client data.
2. Termination. Either party may terminate this Agreement upon thirty (30) days notice.
3. Limitation of Liability. In no event shall either party be liable for indirect, incidental, or consequential damages.
4. Indemnification. Client agrees to indemnify and hold harmless Vendor.
5. Governing Law and Arbitration. Any dispute shall be resolved by binding arbitration.
6. Waiver and Assignment. No waiver of any term shall be deemed a further waiver."""

# Extract clauses
clauses = []
if st.button("Extract Clauses"):
    content = ""
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".pdf"):
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    content += page.extract_text() + "\n"
        elif uploaded_file.name.endswith(".txt"):
            content = uploaded_file.read().decode("utf-8")
    if text_input:
        content += "\n" + text_input

    # Simple clause splitting by numbered headings
    import re
    raw_clauses = re.split(r"\n?\s*\d+\. ", content)
    clauses = [c.strip() for c in raw_clauses if len(c.strip()) > 20]
    st.session_state.clauses = clauses
    st.success(f"Extracted {len(clauses)} clauses.")

# Display clauses and heuristic analysis
if "clauses" in st.session_state:
    st.subheader("Extracted Clauses and Flags")
    risk_keywords = {
        "Confidentiality": ["confidential", "non-disclosure", "nda", "privacy"],
        "Termination/Notice": ["terminate", "termination", "notice", "days notice"],
        "Indemnity": ["indemnify", "indemnification", "hold harmless"],
        "Liability/Cap": ["liability", "liable", "consequential", "cap"],
        "Arbitration/Law": ["arbitration", "governing law", "jurisdiction", "dispute resolution"],
        "Waiver/Assignment": ["waive", "waiver", "assignment"]
    }
    for i, clause in enumerate(st.session_state.clauses, 1):
        flags = []
        for key, keywords in risk_keywords.items():
            if any(k.lower() in clause.lower() for k in keywords):
                flags.append(key)
        st.markdown(f"**Clause {i}:** {clause}")
        st.markdown(f"**Flags:** {', '.join(flags) if flags else 'None'}")
        st.markdown("---")
