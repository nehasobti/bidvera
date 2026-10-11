"""
Script to generate sample tenders data including tender.json, tenders_registry.json,
and realistic structured .docx tender documents using python-docx.
"""
from pathlib import Path
import json
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

BASE_DIR = Path(__file__).resolve().parent
TENDERS_DIR = BASE_DIR / "sample-data" / "tenders"
TENDERS_DIR.mkdir(parents=True, exist_ok=True)

registry = [
    {
        "id": "tender-001",
        "title": "Cloud Migration & Hybrid DevOps Infrastructure",
        "buyer": "EuroRailways Digital GmbH",
        "country": "EU",
        "category": "Cloud Migration",
        "deadline": "2026-11-20T17:00:00Z",
        "estimated_budget_eur": 2500000,
        "summary": "EuroRailways Digital seeks an experienced cloud integration partner to migrate 380+ legacy virtual workloads to AWS and establish automated GitOps DevOps pipelines with 99.95% availability SLA.",
        "documents": [
            {
                "id": "doc-001-main",
                "name": "RFP_EuroRailways_Cloud_Migration.docx",
                "type": "main_rfp",
                "pages": 14
            },
            {
                "id": "doc-001-sec",
                "name": "RFP_EuroRailways_Cloud_Migration_Annex_Security.docx",
                "type": "security_annex",
                "pages": 6
            }
        ],
        "eligibility_criteria": [
            {"criterion": "Annual Turnover", "threshold": "Minimum €10,000,000 average over last 3 years", "type": "mandatory"},
            {"criterion": "Years in Business", "threshold": "Minimum 8 years in IT consultancy", "type": "mandatory"},
            {"criterion": "ISO 27001 Certification", "threshold": "Valid ISO/IEC 27001 certificate at time of submission", "type": "mandatory"},
            {"criterion": "Cloud Partner Status", "threshold": "AWS Premier or Advanced Tier Partner", "type": "mandatory"},
            {"criterion": "Prior Experience", "threshold": "At least 2 enterprise cloud migrations exceeding 250 VMs", "type": "mandatory"}
        ]
    },
    {
        "id": "tender-002",
        "title": "Enterprise Healthcare Data Lakehouse & AI Analytics",
        "buyer": "National Health Consortium",
        "country": "India",
        "category": "Data & AI",
        "deadline": "2026-12-05T18:00:00Z",
        "estimated_budget_eur": 1950000,
        "summary": "Implementation of a centralized, secure clinical data lakehouse, real-time HL7/FHIR streaming ingestion, and predictive AI analytics platform across regional medical hubs.",
        "documents": [
            {
                "id": "doc-002-main",
                "name": "RFP_NHC_Healthcare_Data_Platform.docx",
                "type": "main_rfp",
                "pages": 12
            },
            {
                "id": "doc-002-tech",
                "name": "RFP_NHC_Technical_Specs.docx",
                "type": "technical_specs",
                "pages": 8
            }
        ],
        "eligibility_criteria": [
            {"criterion": "Annual Turnover", "threshold": "Minimum ₹100 Crore / €11M", "type": "mandatory"},
            {"criterion": "Healthcare Data Experience", "threshold": "Demonstrated lakehouse deployment with >10M records", "type": "mandatory"},
            {"criterion": "CMMI Level", "threshold": "CMMI Maturity Level 3 or higher", "type": "mandatory"},
            {"criterion": "ISO 9001 / ISO 27001", "threshold": "Active certifications required", "type": "mandatory"}
        ]
    },
    {
        "id": "tender-003",
        "title": "Core Banking Microservices Modernization",
        "buyer": "Nordic Logistics & FinServices AB",
        "country": "EU",
        "category": "Software Development",
        "deadline": "2026-11-30T16:00:00Z",
        "estimated_budget_eur": 3200000,
        "summary": "Decomposition of monolithic transaction processing into domain-driven microservices on Kubernetes, API gateway integration, and PCI-DSS compliance.",
        "documents": [
            {
                "id": "doc-003-main",
                "name": "RFP_Nordic_Microservices_Modernization.docx",
                "type": "main_rfp",
                "pages": 15
            }
        ],
        "eligibility_criteria": [
            {"criterion": "Annual Turnover", "threshold": "Minimum €12,000,000", "type": "mandatory"},
            {"criterion": "Financial Services Experience", "threshold": "At least 1 core banking / payment modernization project", "type": "mandatory"},
            {"criterion": "ISO 27001", "threshold": "Mandatory active certification", "type": "mandatory"}
        ]
    }
]

# Write registry
with open(TENDERS_DIR / "tenders_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2)

print("Created tenders_registry.json")

def create_doc(file_path: Path, title: str, subtitle: str, sections_data: list[tuple[str, list[str]]], table_data: list[list[str]] | None = None) -> None:
    doc = docx.Document()
    
    # Title
    p_title = doc.add_paragraph()
    run_title = p_title.add_run(title)
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(16, 44, 87)
    
    p_sub = doc.add_paragraph()
    run_sub = p_sub.add_run(subtitle)
    run_sub.font.size = Pt(13)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(80, 80, 80)
    
    doc.add_paragraph() # spacer
    
    # Sections
    for sec_heading, paragraphs in sections_data:
        h = doc.add_heading(sec_heading, level=1)
        for p_text in paragraphs:
            doc.add_paragraph(p_text)
            
    # Table if present
    if table_data:
        doc.add_heading("Requirements & Evaluation Criteria", level=2)
        table = doc.add_table(rows=len(table_data), cols=len(table_data[0]))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for r_idx, row in enumerate(table_data):
            for c_idx, val in enumerate(row):
                cell = table.cell(r_idx, c_idx)
                cell.text = val
                if r_idx == 0:
                    for p in cell.paragraphs:
                        for run in p.runs:
                            run.font.bold = True
                            
    doc.save(file_path)
    print(f"Generated {file_path}")

# Tender 1
t1_dir = TENDERS_DIR / "tender-001"
t1_dir.mkdir(exist_ok=True)
with open(t1_dir / "tender.json", "w", encoding="utf-8") as f:
    json.dump(registry[0], f, indent=2)

create_doc(
    t1_dir / "RFP_EuroRailways_Cloud_Migration.docx",
    "Request for Proposals: Cloud Migration & Hybrid DevOps",
    "EuroRailways Digital GmbH · Tender Ref: ERD-2026-CLD-09",
    [
        ("1. Introduction and Objectives", [
            "EuroRailways Digital GmbH invites qualified IT service providers to submit proposals for the migration of 380+ application virtual machines to Amazon Web Services (AWS) and modernizing the underlying deployment ecosystem.",
            "The objective is to establish an agile, resilient, multi-region cloud topology ensuring 99.95% availability for critical rail logistics scheduling."
        ]),
        ("2. Scope of Work", [
            "2.1 Infrastructure Discovery: Complete dependency mapping of all existing VMware VMs, Oracle/PostgreSQL databases, and internal APIs.",
            "2.2 Landing Zone Design: AWS multi-account landing zone leveraging AWS Organizations, Transit Gateway, and Infrastructure as Code via Terraform.",
            "2.3 Wave Migration: Phased workload cutover in 4 discrete migration waves with zero unplanned downtime during rail operating hours.",
            "2.4 CI/CD and GitOps: Establishment of GitLab CI / ArgoCD automation for automated container builds and deployments to Amazon EKS."
        ]),
        ("3. Mandatory Eligibility Criteria", [
            "Bidders must satisfy the following minimum requirements: (a) Documented corporate turnover exceeding €10M annually over the past 3 fiscal years; (b) Minimum 8 years of operational experience in enterprise software consultancy; (c) Valid ISO/IEC 27001 accreditation; (d) Official AWS Premier or Advanced Tier Partner status."
        ])
    ],
    [
        ["Req ID", "Requirement Description", "Type", "Weight", "Section Ref"],
        ["REQ-001", "Bidders must have minimum €10M annual turnover and 8 years operational history", "Mandatory", "Pass/Fail", "Section 3.1"],
        ["REQ-002", "Provide valid ISO/IEC 27001:2022 accreditation certificate", "Mandatory", "Pass/Fail", "Section 3.2"],
        ["REQ-003", "Achieve zero unplanned downtime during production database cutover", "Mandatory", "25%", "Section 2.3"],
        ["REQ-004", "Deploy automated Terraform landing zone with CIS Benchmark Level 2 compliance", "Mandatory", "20%", "Section 2.2"],
        ["REQ-005", "Implement ArgoCD GitOps pipelines on Amazon EKS with automated canary rollouts", "Scored", "15%", "Section 2.4"],
        ["REQ-006", "Provide 24/7 hypercare support with 15-minute P1 incident response time SLA", "Optional", "10%", "Section 2.5"]
    ]
)

create_doc(
    t1_dir / "RFP_EuroRailways_Cloud_Migration_Annex_Security.docx",
    "Annex B: Security and Compliance Specifications",
    "EuroRailways Digital GmbH · Information Security Directive 2026",
    [
        ("1. Information Security Standards", [
            "All cloud architectures must comply with the BSI IT-Grundschutz baseline and GDPR Art. 32 requirements.",
            "Customer data encryption in transit via TLS 1.3 and at rest with AWS KMS Customer Managed Keys (CMK) is strictly mandatory."
        ]),
        ("2. Security Audit & Governance", [
            "The vendor must provide dedicated DevSecOps governance including static code scanning (SAST), software bill of materials (SBOM), and quarterly penetration testing."
        ])
    ]
)

# Tender 2
t2_dir = TENDERS_DIR / "tender-002"
t2_dir.mkdir(exist_ok=True)
with open(t2_dir / "tender.json", "w", encoding="utf-8") as f:
    json.dump(registry[1], f, indent=2)

create_doc(
    t2_dir / "RFP_NHC_Healthcare_Data_Platform.docx",
    "Request for Proposals: Healthcare Data Lakehouse & AI Platform",
    "National Health Consortium · Tender Ref: NHC-2026-DATA-04",
    [
        ("1. Executive Summary", [
            "National Health Consortium invites bids for designing and deploying an enterprise Data Lakehouse on Azure Databricks handling aggregated clinical records across regional diagnostic hubs."
        ]),
        ("2. Functional Requirements", [
            "2.1 Ingestion of HL7 v2 and FHIR clinical messages via streaming pipelines.",
            "2.2 Automated de-identification and pseudonymization of patient personal health info (PHI).",
            "2.3 Sub-2-second query performance on analytical cohorts exceeding 10 million records."
        ])
    ],
    [
        ["Req ID", "Requirement Description", "Type", "Weight", "Section Ref"],
        ["REQ-010", "Bidder must possess active ISO 27001 and CMMI Level 3 certifications", "Mandatory", "Pass/Fail", "Section 1.3"],
        ["REQ-011", "Streaming ingestion of FHIR/HL7 clinical messages with <= 5 sec latency", "Mandatory", "30%", "Section 2.1"],
        ["REQ-012", "Automated HIPAA and DISHA data tokenization & encryption at rest", "Mandatory", "25%", "Section 2.2"],
        ["REQ-013", "AI-based patient cohort risk stratification models with explainable metrics", "Scored", "20%", "Section 2.4"]
    ]
)

create_doc(
    t2_dir / "RFP_NHC_Technical_Specs.docx",
    "Technical Specifications & Interoperability Guidelines",
    "National Health Consortium · Architecture Working Group",
    [
        ("1. Data Governance Architecture", [
            "The solution must implement Azure Purview or Unity Catalog for automated lineage and data cataloging.",
            "Role-Based Access Control (RBAC) must restrict doctor and researcher views according to national privacy guidelines."
        ])
    ]
)

# Tender 3
t3_dir = TENDERS_DIR / "tender-003"
t3_dir.mkdir(exist_ok=True)
with open(t3_dir / "tender.json", "w", encoding="utf-8") as f:
    json.dump(registry[2], f, indent=2)

create_doc(
    t3_dir / "RFP_Nordic_Microservices_Modernization.docx",
    "RFP: Core Banking Microservices Modernization",
    "Nordic Logistics & FinServices AB · Ref: NLFS-2026-FIN-01",
    [
        ("1. Project Background", [
            "Nordic Logistics & FinServices AB seeks an engineering partner to modernize its transaction engine into lightweight Spring Boot microservices deployed on Kubernetes with strict PCI-DSS compliance."
        ]),
        ("2. Technical Scope", [
            "2.1 Decompose monolithic ledger into event-driven microservices using Apache Kafka.",
            "2.2 Guarantee 99.99% system availability and sub-50ms p99 response times for credit processing."
        ])
    ],
    [
        ["Req ID", "Requirement Description", "Type", "Weight", "Section Ref"],
        ["REQ-020", "Minimum €12M turnover and proven financial microservices track record", "Mandatory", "Pass/Fail", "Section 1.2"],
        ["REQ-021", "End-to-end mTLS encryption and PCI-DSS Level 1 compliant architecture", "Mandatory", "30%", "Section 2.2"],
        ["REQ-022", "High-throughput Kafka streaming pipeline handling 10k transactions/sec", "Mandatory", "25%", "Section 2.1"]
    ]
)

print("All sample tenders and .docx documents created successfully.")
