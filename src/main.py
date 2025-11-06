from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json
import base64

from utils.pdf_utils import PDFExtractor


class KnowledgeBase:
    """
    Classe responsável por gerenciar o armazenamento e recuperação
    da base de conhecimento local (knowledge_base.json).
    """

    def __init__(self, filepath: Path):
        """
        Inicializa o gerenciador da base de conhecimento.

        Args:
            filepath (Path): Caminho do arquivo JSON de conhecimento.
        """
        self.filepath = filepath

    def load(self) -> dict:
        """
        Carrega o conteúdo da base de conhecimento.

        Returns:
            dict: Dados armazenados ou dicionário vazio se o arquivo não existir.
        """
        if self.filepath.exists():
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save(self, data: dict) -> None:
        """
        Salva os dados na base de conhecimento em formato JSON.

        Args:
            data (dict): Dados a serem salvos.
        """
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


class ExtractionRequest(BaseModel):
    """Modelo de entrada da requisição de extração."""
    label: str
    extraction_schema: dict
    pdf: str  # Base64 do PDF


class ExtractionResponse(BaseModel):
    """Modelo de resposta da API após extração."""
    label: str
    extracted_text: str
    extracted_fields: dict


class PDFExtractionService:
    """
    Serviço responsável por orquestrar a extração de informações de PDFs,
    integrando o extrator de texto e a base de conhecimento.
    """

    def __init__(self, extractor: PDFExtractor, knowledge_base: KnowledgeBase):
        """
        Inicializa o serviço de extração.

        Args:
            extractor (PDFExtractor): Instância da classe responsável pela extração de texto e campos.
            knowledge_base (KnowledgeBase): Instância da classe de gerenciamento da base de conhecimento.
        """
        self.extractor = extractor
        self.knowledge_base = knowledge_base

    def process(self, label: str, extraction_schema: dict, pdf_b64: str) -> dict:
        """
        Realiza a extração de texto e campos estruturados de um PDF.

        Args:
            label (str): Identificador do documento.
            extraction_schema (dict): Estrutura esperada dos campos.
            pdf_b64 (str): Arquivo PDF em Base64.

        Returns:
            dict: Resultado contendo texto e campos extraídos.
        """
        pdf_bytes = base64.b64decode(pdf_b64)
        if not pdf_bytes:
            raise HTTPException(status_code=400, detail="PDF inválido ou vazio")

        text = self.extractor.extract_text_from_pdf_bytes(pdf_bytes)
        if "__ERROR__" in text:
            raise HTTPException(status_code=400, detail=f"Erro na extração de texto: {text}")

        fields = self.extractor.extract_fields_from_text_generic(text, extraction_schema)

        for field in extraction_schema.keys():
            fields.setdefault(field, None)

        knowledge = self.knowledge_base.load()
        knowledge.setdefault(label, []).append(fields)
        self.knowledge_base.save(knowledge)

        return {"label": label, "extracted_text": text, "extracted_fields": fields}


app = FastAPI(title="Take Home Enter AI - PDF Extractor API")
knowledge_base = KnowledgeBase(Path(__file__).parent / "knowledge_base.json")
extractor = PDFExtractor()
service = PDFExtractionService(extractor, knowledge_base)


@app.post("/extract", response_model=ExtractionResponse)
def extract_info(req: ExtractionRequest):
    """
    Endpoint principal para extração de informações de arquivos PDF.

    Args:
        req (ExtractionRequest): Requisição contendo label, schema e PDF em Base64.

    Returns:
        ExtractionResponse: Resultado com texto e campos extraídos.
    """
    try:
        return service.process(req.label, req.extraction_schema, req.pdf)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro na extração: {str(e)}")
