import pandas as pd
from typing import List, Dict
import io

class SheetParser:
    @staticmethod
    def parse_csv(content: bytes) -> List[Dict]:
        """Parse CSV file and return list of dicts"""
        try:
            df = pd.read_csv(io.BytesIO(content))
            return df.to_dict('records')
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {str(e)}")

    @staticmethod
    def parse_xlsx(content: bytes) -> List[Dict]:
        """Parse XLSX file and return list of dicts"""
        try:
            df = pd.read_excel(io.BytesIO(content))
            return df.to_dict('records')
        except Exception as e:
            raise ValueError(f"Failed to parse XLSX: {str(e)}")

    @staticmethod
    def parse_file(filename: str, content: bytes) -> List[Dict]:
        """Auto-detect and parse file"""
        if filename.endswith('.csv'):
            return SheetParser.parse_csv(content)
        elif filename.endswith(('.xlsx', '.xls')):
            return SheetParser.parse_xlsx(content)
        else:
            raise ValueError("Unsupported file format. Use CSV or XLSX.")

sheet_parser = SheetParser()
