from flask import Flask, jsonify, send_file
from io import BytesIO
import PyPDF2

app = Flask(__name__)

@app.route('/fill_pdf', methods=['POST'])
def fill_pdf():
    # Mock data for testing
    mock_data = {
        "month": "January 2025",
        "operator": "ABC Oil Company",
        "well_name": "Well A",
        "oil_sold": 1500,
        "gas_sold": 5000,
        "water_produced": 0,
        "beginning_stock": 1000,
        "ending_stock": 1500,
        "production_volume": 1500
    }

    # Use the mock data to fill the PDF (for now, we're just simulating this)
    pdf_output = fill_pdf_with_data(mock_data)

    # Send the filled PDF back to the user
    return send_file(pdf_output, as_attachment=True, download_name="filled_form.pdf", mimetype='application/pdf')


def fill_pdf_with_data(data):
    # Mock-up the filling process: For now, just return a basic PDF with the data in it.
    # Normally, this function would take the data and fill a template PDF using PyPDF2.
    
    # For demonstration, let's create a simple PDF and use PyPDF2 to add data to it (this can be improved).
    pdf_writer = PyPDF2.PdfWriter()
    pdf_output = BytesIO()

    # Create a simple PDF for demonstration purposes
    # Normally you would use PyPDF2 to fill fields here, but let's skip that for simplicity.

    # Adding a page with text for now
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(pdf_output)
    c.drawString(100, 800, f"Month: {data['month']}")
    c.drawString(100, 780, f"Operator: {data['operator']}")
    c.drawString(100, 760, f"Well Name: {data['well_name']}")
    c.drawString(100, 740, f"Oil Sold: {data['oil_sold']} BBL")
    c.drawString(100, 720, f"Gas Sold: {data['gas_sold']} MCF")
    c.drawString(100, 700, f"Water Produced: {data['water_produced']} BBL")
    c.drawString(100, 680, f"Beginning Stock: {data['beginning_stock']} BBL")
    c.drawString(100, 660, f"Ending Stock: {data['ending_stock']} BBL")
    c.drawString(100, 640, f"Production Volume: {data['production_volume']} BBL")

    # Finish writing the PDF
    c.showPage()
    c.save()

    # Save to the in-memory PDF file
    pdf_output.seek(0)

    return pdf_output


if __name__ == '__main__':
    app.run(debug=True)
