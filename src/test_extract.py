import requests
import base64
import json
from pathlib import Path


class PDFExtractorClient:
    """
    Cliente para interagir com a API de extração de informações em PDFs.
    Responsável por enviar arquivos PDF codificados em Base64 e salvar os resultados.
    """

    def __init__(self, api_url: str, pdf_dir: Path):
        self.api_url = api_url
        self.pdf_dir = pdf_dir
        self.schemas = {
            "oab": {
                "nome": "Nome do advogado",
                "numero_oab": "Número OAB"
            },
            "tela_sistema": {
                "data_referencia": "Data de referência das parcelas",
                "saldo_vencido": "Valor vencido",
                "saldo_a_vencer": "Valor a vencer",
                "total": "Valor total"
            }
        }

    def _encode_pdf(self, pdf_path: Path) -> str:
        with open(pdf_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _detect_schema(self, filename: str) -> dict:
        if filename.startswith("oab"):
            return self.schemas["oab"]
        return self.schemas["tela_sistema"]

    def process_pdfs(self) -> dict:
        pdf_files = list(self.pdf_dir.glob("oab_*.pdf")) + list(self.pdf_dir.glob("tela_sistema_*.pdf"))
        results = {}

        for pdf_path in pdf_files:
            label = pdf_path.stem
            schema = self._detect_schema(label)
            encoded_pdf = self._encode_pdf(pdf_path)

            data = {
                "label": label,
                "extraction_schema": schema,
                "pdf": encoded_pdf
            }

            try:
                response = requests.post(f"{self.api_url}/extract", json=data)
                if response.status_code == 200:
                    results[label] = response.json()
                    print(f"{label} processado com sucesso.")
                else:
                    print(f"Erro ao processar {label}: {response.status_code} - {response.text}")
            except requests.RequestException as e:
                print(f"Erro de conexão com a API: {e}")

        return results

    def save_results(self, results: dict, filename: str = "relatorio_extracao.json") -> None:
        output_path = self.pdf_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Relatório gerado: {output_path.name}")


if __name__ == "__main__":
    
    pdf_dir = Path(__file__).parent
    client = PDFExtractorClient(api_url="http://127.0.0.1:8000", pdf_dir=pdf_dir)
    results = client.process_pdfs()
    client.save_results(results)
