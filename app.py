from flask import Flask, request, send_file, jsonify, render_template
import pandas as pd
import os

app = Flask(__name__)

# Define directories for uploaded files and filtered output
UPLOAD_FOLDER = 'uploads'
FILTERED_FOLDER = 'filtered'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(FILTERED_FOLDER, exist_ok=True)

# To store the uploaded filename and filtered filename
uploaded_file_name = ''
filtered_file_name = ''

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global uploaded_file_name
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    # Save the uploaded file
    uploaded_file_name = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(uploaded_file_name)
    
    return 'File uploaded successfully', 200

@app.route('/filter', methods=['POST'])
def filter_students():
    global uploaded_file_name, filtered_file_name
    branch = request.form.get('branch', '').strip()
    gender = request.form.get('gender', '').strip()
    city = request.form.get('city', '').strip()

    try:
        # Load the uploaded Excel file
        df = pd.read_excel(uploaded_file_name)

        # Apply filters based on user input
        if branch and branch != "all":
            df = df[df['Branch'].str.contains(branch, case=False, na=False)]
        if gender and gender != "all":
            df = df[df['Gender'].str.contains(gender, case=False, na=False)]
        if city:
            df = df[df['City'].str.contains(city, case=False, na=False)]

        # Check if there are any results after filtering
        if df.empty:
            return jsonify({"status": "error", "message": "No matching students found."}), 404

        # Save the filtered data to a new Excel file
        filtered_file_name = os.path.join(FILTERED_FOLDER, 'filtered_students.xlsx')
        df.to_excel(filtered_file_name, index=False)

        # Return the link to download the file
        return jsonify({"status": "success", "download_link": f"/download/{os.path.basename(filtered_file_name)}"}), 200
    except Exception as e:
        print(f"Error: {e}")  # Log the error for debugging
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_file(os.path.join(FILTERED_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
