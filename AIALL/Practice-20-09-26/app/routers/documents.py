import io
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from pypdf import PdfReader
from app.services.vector_service import vector_service

router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents & Ingestion"]
)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """PDF binary data se plain text nikalta hai"""
    pdf = PdfReader(io.BytesIO(file_bytes))
    extracted_text = []
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            extracted_text.append(page_text)
    return "\n".join(extracted_text)


@router.post("/upload-pdf", status_code=status.HTTP_201_CREATED)
async def upload_pdf_document(
    file: UploadFile = File(...),
    title: str = Form(..., description="Document ka title e.g. 'Annual Report 2025'"),
    section: str = Form(default="General Upload", description="Section ya Chapter name")
):
    # 1. Check file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sirf PDF files (.pdf) allowed hain."
        )

    # 2. PDF read aur text extraction
    content_bytes = await file.read()
    try:
        raw_text = extract_text_from_pdf(content_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"PDF read karne mein error aayi: {str(e)}"
        )

    if not raw_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="PDF khali hai ya scanned image hai jisse text read nahi ho saka."
        )

    # 3. Vector service ke add_document mein store karna
    doc_id = vector_service.add_document(
        title=title,
        section=section,
        content=raw_text,
        tags=["uploaded_pdf", file.filename]
    )

    return {
        "status": "success",
        "doc_id": doc_id,
        "filename": file.filename,
        "indexed_characters": len(raw_text),
        "message": "PDF successfully extract hokar Vector Store me index ho gayi."
    }