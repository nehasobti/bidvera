"""Knowledge store and hybrid retrieval engine for company-knowledge MCP server."""

from __future__ import annotations

import datetime
import json
import os
import re
from pathlib import Path
from typing import Any

from knowledge_models import (
    CaseStudyItem,
    CertificationItem,
    CompanyProfile,
    KnowledgeChunk,
    StaffCV,
)


def get_company_data_dir() -> Path:
    env_dir = os.environ.get("COMPANY_DATA_DIR")
    if env_dir and Path(env_dir).exists():
        return Path(env_dir)
    candidates = [
        Path.cwd() / "sample-data" / "company",
        Path(__file__).resolve().parent.parent.parent / "sample-data" / "company",
        Path(__file__).resolve().parent / "data",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]


class CompanyKnowledgeStore:
    """Manages Tychon Software data, indexing, and hybrid retrieval."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or get_company_data_dir()
        self.profile: CompanyProfile | None = None
        self.certifications: list[CertificationItem] = []
        self.case_studies: list[CaseStudyItem] = []
        self.cvs: list[StaffCV] = []
        self.past_proposals: list[dict[str, Any]] = []
        self.chunks: list[KnowledgeChunk] = []
        self.load_data()

    def load_data(self) -> None:
        """Loads and parses all company JSON data files."""
        # 1. Profile
        profile_path = self.data_dir / "profile.json"
        if profile_path.exists():
            with open(profile_path, encoding="utf-8") as f:
                p_data = json.load(f)
                self.profile = CompanyProfile(**p_data)

        # 2. Certifications
        certs_path = self.data_dir / "certifications.json"
        if certs_path.exists():
            with open(certs_path, encoding="utf-8") as f:
                c_data = json.load(f)
                today = datetime.date.today().isoformat()
                self.certifications = []
                for item in c_data:
                    # Check expiry
                    exp = item.get("expiry_date", "2099-01-01")
                    is_valid = item.get("status") == "active" and exp >= today
                    self.certifications.append(
                        CertificationItem(**item, is_valid=is_valid)
                    )

        # 3. Case Studies
        cs_path = self.data_dir / "case_studies.json"
        if cs_path.exists():
            with open(cs_path, encoding="utf-8") as f:
                cs_data = json.load(f)
                self.case_studies = [CaseStudyItem(**item) for item in cs_data]

        # 4. CVs
        cvs_path = self.data_dir / "cvs.json"
        if cvs_path.exists():
            with open(cvs_path, encoding="utf-8") as f:
                cvs_data = json.load(f)
                self.cvs = [StaffCV(**item) for item in cvs_data]

        # 5. Past Proposals
        props_path = self.data_dir / "past_proposals.json"
        if props_path.exists():
            with open(props_path, encoding="utf-8") as f:
                self.past_proposals = json.load(f)

        self._build_chunks()

    def _build_chunks(self) -> None:
        """Creates granular searchable knowledge chunks from all documents."""
        self.chunks.clear()

        # Corporate Profile chunk
        if self.profile:
            self.chunks.append(
                KnowledgeChunk(
                    chunk_id="chk-profile-01",
                    doc_type="profile",
                    source_id=self.profile.company_id,
                    title="Tychon Software Corporate Profile & Competencies",
                    text=f"{self.profile.legal_name} ({self.profile.trade_name}) founded in {self.profile.founded_year}. "
                    f"Turnover €{self.profile.financials['turnover'][0]['turnover_eur']:,}. "
                    f"Headcount: {self.profile.workforce['total_full_time_employees']} full-time staff. "
                    f"Overview: {self.profile.overview} "
                    f"Core competencies: {', '.join(self.profile.core_competencies)}.",
                    date="2026-01-01",
                    metadata={"headquarters": self.profile.headquarters},
                )
            )

        # Case Study chunks
        for cs in self.case_studies:
            self.chunks.append(
                KnowledgeChunk(
                    chunk_id=f"chk-cs-{cs.id}",
                    doc_type="case_study",
                    source_id=cs.id,
                    title=f"Case Study: {cs.title}",
                    text=f"Client: {cs.client} ({cs.industry}, {cs.country}). "
                    f"Challenge: {cs.challenge} "
                    f"Solution: {cs.solution} "
                    f"Outcomes: {cs.outcomes} "
                    f"Metrics: {json.dumps(cs.metrics)} "
                    f"Technologies: {', '.join(cs.technologies)}.",
                    date=f"{cs.year}-01-01",
                    metadata={"industry": cs.industry, "tags": cs.tags, "year": cs.year},
                )
            )

        # Certification chunks (only active valid certs generate authoritative evidence chunks)
        for cert in self.certifications:
            if cert.is_valid:
                self.chunks.append(
                    KnowledgeChunk(
                        chunk_id=f"chk-cert-{cert.id}",
                        doc_type="certification",
                        source_id=cert.id,
                        title=f"Certification: {cert.name}",
                        text=f"Certification: {cert.name} issued by {cert.issuing_body}. "
                        f"Cert Number: {cert.certificate_number}. Valid from {cert.issue_date} to {cert.expiry_date}. "
                        f"Scope: {cert.scope}. Verification: {cert.verification_url}.",
                        date=cert.issue_date,
                        metadata={"status": cert.status, "expiry": cert.expiry_date},
                    )
                )

        # CV chunks
        for cv in self.cvs:
            proj_text = " ".join([f"{p['title']}: {p['impact']}" for p in cv.selected_projects])
            self.chunks.append(
                KnowledgeChunk(
                    chunk_id=f"chk-cv-{cv.id}",
                    doc_type="cv",
                    source_id=cv.id,
                    title=f"CV: {cv.name} ({cv.role})",
                    text=f"{cv.name}, {cv.role} with {cv.years_of_experience} years experience in {cv.location}. "
                    f"Bio: {cv.bio} Skills: {', '.join(cv.skills)}. "
                    f"Certifications: {', '.join(cv.certifications)}. "
                    f"Projects: {proj_text}",
                    date="2026-01-01",
                    metadata={"role": cv.role, "skills": cv.skills},
                )
            )

        # Past proposals
        for prop in self.past_proposals:
            self.chunks.append(
                KnowledgeChunk(
                    chunk_id=f"chk-prop-{prop['id']}",
                    doc_type="past_proposal",
                    source_id=prop["id"],
                    title=f"Past Proposal: {prop['topic']}",
                    text=f"Topic: {prop['topic']} (Category: {prop['section_category']}). "
                    f"Approved Answer: {prop['approved_text']}",
                    date="2025-06-01",
                    metadata={"category": prop["section_category"], "citations": prop.get("citations", [])},
                )
            )

    def search_hybrid(
        self,
        query: str,
        doc_types: list[str] | None = None,
        top_k: int = 5,
    ) -> list[KnowledgeChunk]:
        """Performs hybrid token and keyword retrieval with recency re-ranking."""
        if not query.strip():
            selected = self.chunks[:top_k]
            return selected

        # Tokenize query
        tokens = set(re.findall(r"\w+", query.lower()))
        scored_chunks: list[tuple[float, KnowledgeChunk]] = []

        for chk in self.chunks:
            if doc_types and chk.doc_type not in doc_types:
                continue

            # Token overlap & BM25 approximation
            chk_tokens = re.findall(r"\w+", chk.text.lower() + " " + chk.title.lower())
            chk_set = set(chk_tokens)
            if not chk_set:
                continue

            matches = tokens.intersection(chk_set)
            if not matches:
                continue

            # Frequency score
            term_score = sum(chk_tokens.count(t) for t in matches)
            overlap_ratio = len(matches) / len(tokens)
            base_score = (term_score * 0.5) + (overlap_ratio * 3.0)

            # Recency boost (up to +0.5 for newer documents)
            year_match = re.search(r"202[0-9]", chk.date)
            if year_match:
                year = int(year_match.group(0))
                recency_boost = max(0.0, (year - 2020) * 0.1)
                base_score += recency_boost

            chk_copy = chk.model_copy()
            chk_copy.score = round(base_score, 3)
            scored_chunks.append((base_score, chk_copy))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored_chunks[:top_k]]
