from io import BytesIO
from flask import Flask, request, send_file, abort
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NumberObject, DictionaryObject, BooleanObject

TEMPLATE_PATH = "DISTRICT_5.pdf"  # your blank form

app = Flask(__name__)

def set_need_appearances_and_rotation(writer: PdfWriter, rotation_deg: int = 90):
    # NeedAppearances = True so viewers render the typed values
    acro = writer._root_object.get("/AcroForm")
    if acro:
        acro.update({NameObject("/NeedAppearances"): BooleanObject(True)})

    # rotate all widgets’ text (0, 90, 180, 270)
    rot = int(rotation_deg) % 360
    for page in writer.pages:
        for annot_ref in page.get("/Annots", []):
            annot = annot_ref.get_object()
            mk = annot.get("/MK")
            if mk:
                mk.update({NameObject("/R"): NumberObject(rot)})
            else:
                annot[NameObject("/MK")] = DictionaryObject({NameObject("/R"): NumberObject(rot)})
            # drop cached appearance so it’s redrawn at the new rotation
            if "/AP" in annot:
                del annot["/AP"]

@app.post("/fill-d5")
def fill_district5():
    """
    JSON body:
    {
      "rotation": 90,                # optional, defaults 90
      "fields": {                    # required: keys are PDF field names
        "fieldname1": "SMI1",
        "lease name1": "SMITHERMAN #1",
        "ogp1": "G",
        "lease/gas#1": "204225",
        "stock on hand1": "140",
        "production1": "150",
        "volume1": "0",
        "code1": "1",
        "stockendmonth1": "100",
        "formation1": "568",
        "dispositionvolume1": "568",
        "dispostioncode1": "2"
      }
    }
    """
    data = request.get_json(silent=True)
    if not data or "fields" not in data or not isinstance(data["fields"], dict):
        abort(400, "POST JSON must include a 'fields' object")

    rotation = int(data.get("rotation", 90))
    fields = data["fields"]

    # load template each request
    reader = PdfReader(TEMPLATE_PATH)
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)

    # copy AcroForm dict to writer root (so NeedAppearances edit works)
    root = reader.trailer["/Root"]
    acro = root.get("/AcroForm")
    if acro:
        writer._root_object.update({NameObject("/AcroForm"): acro.get_object()})

    set_need_appearances_and_rotation(writer, rotation)

    # fill page 1 (index 0)
    page = writer.pages[0]
    writer.update_page_form_field_values(page, fields)

    # return as PDF bytes
    buf = BytesIO()
    writer.write(buf)
    buf.seek(0)
    return send_file(
        buf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="DISTRICT_5_filled.pdf",
    )

if __name__ == "__main__":
    # simple dev server
    app.run(host="0.0.0.0", port=5000)
