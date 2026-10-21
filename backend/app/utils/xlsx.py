"""Create a small standards-based XLSX workbook without runtime dependencies."""

from io import BytesIO
from typing import Any, Dict
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


def _cell(column: str, value: Any) -> str:
    return (
        f'<c r="{column}1" t="inlineStr"><is><t>'
        f"{escape(str(value if value is not None else ''))}</t></is></c>"
    )


def illustrative_xlsx(payload: Dict[str, Any]) -> bytes:
    """Return a one-header/one-value-row workbook for a mock Myntra sample."""

    values = [(key, value if not isinstance(value, (list, dict)) else str(value)) for key, value in payload.items()]
    columns = []
    for index in range(len(values)):
        number = index + 1
        letters = ""
        while number:
            number, remainder = divmod(number - 1, 26)
            letters = chr(65 + remainder) + letters
        columns.append(letters)
    header = "".join(
        f'<c r="{column}1" t="inlineStr"><is><t>{escape(key)}</t></is></c>'
        for column, (key, _) in zip(columns, values)
    )
    row = "".join(
        f'<c r="{column}2" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'
        for column, (_, value) in zip(columns, values)
    )
    sheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData><row r="1">{header}</row><row r="2">{row}</row></sheetData></worksheet>'
    )
    files = {
        "[Content_Types].xml": '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>',
        "_rels/.rels": '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "xl/workbook.xml": '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Illustrative sample" sheetId="1" r:id="rId1"/></sheets></workbook>',
        "xl/_rels/workbook.xml.rels": '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>',
        "xl/worksheets/sheet1.xml": sheet,
    }
    output = BytesIO()
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for path, content in files.items():
            archive.writestr(path, content)
    return output.getvalue()
