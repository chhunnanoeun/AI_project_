import os
from flask import Flask, request, jsonify, render_template
import pdfplumber
import re

app = Flask(__name__)

def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()
    return text

def extract_invoice_details(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()

        invoice_number = extract_invoice_number(text)
        invoice_date = extract_invoice_date(text)
        total_amount = extract_total_amount(text)
        line_items = extract_line_items(first_page)

    return {
        "invoice_number": invoice_number,
        "invoice_date": invoice_date,
        "total_amount": total_amount,
        "line_items": line_items
    }

def extract_invoice_number(text):
    return "INV-1234"

def extract_invoice_date(text):
    return "2024-06-23"

def extract_total_amount(text):
    return "$1500.00"

def extract_line_items(page):
    return [
        {"item": "Product A", "quantity": 2, "price": "$500.00", "total": "$1000.00"},
        {"item": "Product B", "quantity": 1, "price": "$500.00", "total": "$500.00"}
    ]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)
        
        response_message = f"Uploaded file: {file.filename}"
        return jsonify({
            "message": response_message,
            "filename": file.filename
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.get_json()
        question = data.get('question', '')
        filename = data.get('filename', '')

        file_path = os.path.join('uploads', filename)
        
        pdf_text = extract_text_from_pdf(file_path)

        answer = generate_answer(question, pdf_text)

        return jsonify({"answer": answer})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/invoice_details', methods=['POST'])
def get_invoice_details():
    try:
        data = request.get_json()
        filename = data.get('filename', '')

        file_path = os.path.join('uploads', filename)

        invoice_details = extract_invoice_details(file_path)

        return jsonify(invoice_details)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True, port=8000)
