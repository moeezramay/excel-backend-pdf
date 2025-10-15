from io import BytesIO
import os
from flask import Flask, request, send_file, abort
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NumberObject, DictionaryObject, BooleanObject

app = Flask(__name__)

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "DISTRICT_5.pdf")

def set_need_appearances_and_rotation(writer: PdfWriter, rotation_deg: int = 90):
    acro = writer._root_object.get("/AcroForm")
    if acro:
        acro.update({NameObject("/NeedAppearances"): BooleanObject(True)})
    rot = int(rotation_deg) % 360
    for page in writer.pages:
        for annot_ref in page.get("/Annots", []):
            annot = annot_ref.get_object()
            mk = annot.get("/MK")
            if mk:
                mk.update({NameObject("/R"): NumberObject(rot)})
            else:
                annot[NameObject("/MK")] = DictionaryObject({NameObject("/R"): NumberObject(rot)})
            if "/AP" in annot:
                del annot["/AP"]

@app.post("/")
def fill_d5():
    data = request.get_json(silent=True)
    if not data or "fields" not in data or not isinstance(data["fields"], dict):
        abort(400, "POST JSON must include a 'fields' object")
    rotation = int(data.get("rotation", 90))
    fields = data["fields"]

    reader = PdfReader(TEMPLATE_PATH)
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)

    # copy AcroForm so NeedAppearances applies
    root = reader.trailer["/Root"]
    acro = root.get("/AcroForm")
    if acro:
        writer._root_object.update({NameObject("/AcroForm"): acro.get_object()})

    set_need_appearances_and_rotation(writer, rotation)

    page = writer.pages[0]
    writer.update_page_form_field_values(page, fields)

    buf = BytesIO()
    writer.write(buf)
    buf.seek(0)
    return send_file(buf, mimetype="application/pdf",
                     as_attachment=True, download_name="DISTRICT_5_filled.pdf")
