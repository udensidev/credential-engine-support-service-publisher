import os
from flask import Flask, request, render_template, redirect, url_for, flash, send_file
from src.scraper import crawl_and_filter_content, extract_subdomains, scrape_page
from src.gemini_query import gemini_query_api, gemini_query_but, save_ctdl_to_json
from src.convert_csv import json_file_to_csv
from src.publish import post_bulk_publish
from src.validate import validate_json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to the uploaded files
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, 'uploads')

# Path to the keywords file
KEYWORDS_FILE = os.path.join(BASE_DIR, 'config', 'keywords.txt')

@app.route('/')
def index():
    return render_template('index.html', ctdl_json=None)

@app.route('/scrape', methods=['POST'])
def scrape():
    ctdl_json = None
    domain_input = request.form['domain']
    publish_method = request.form.get('publishMethod', 'api')  # Default to 'api' if not specified
    
    if not domain_input:
        flash("Please provide a domain.", "error")
        return redirect(url_for('index'))
    
    # Read keywords from the file
    if not os.path.exists(KEYWORDS_FILE):
        flash("Keywords file not found. Please ensure 'keywords.txt' exists in the app directory.", "error")
        return redirect(url_for('index'))
    
    with open(KEYWORDS_FILE, 'r') as f:
        keywords = [line.strip() for line in f]

    # Extract URLs and crawl
    LinkTree = f"https://{domain_input}"
    urls_to_scrape = extract_subdomains(LinkTree)
    filtered_links_with_keywords = []
    visited_links = set()
    for url in urls_to_scrape:
        filtered_links_with_keywords = crawl_and_filter_content(url, keywords, visited=visited_links)
    print("Relevant links and keywords saved to 'relevant_links.json'.")

    # Scrape content
    if not filtered_links_with_keywords:
        flash("No links found with the specified keywords. Please check your input.", "error")
    with open(os.path.join(app.config['UPLOAD_FOLDER'], "scraped_content.txt"), "w", encoding="utf-8") as file:
        for entry in filtered_links_with_keywords:
            scrape_page(entry['url'], file)
    
    # Query Google Gemini
    with open(os.path.join(app.config['UPLOAD_FOLDER'], "scraped_content.txt"), "r", encoding="utf-8") as file:
        text = file.read()
    
    # Use different API calls based on publish method
    if publish_method == 'api':
        ctdl_json = gemini_query_api(text)
        if ctdl_json:
            save_ctdl_to_json(ctdl_json, filepath=os.path.join(app.config['UPLOAD_FOLDER'], "support_services_api.json"))
            json_filepath = os.path.join(app.config["UPLOAD_FOLDER"], "support_services_api.json")

            try:
                post_bulk_publish(ctdl_json)  # Publish to API
                flash("Support services published to API successfully.", "success")
            except Exception as e:
                flash(f"Error publishing to API: {str(e)}", "error")
    else:  # bulk
        ctdl_json = gemini_query_but(text)
        if ctdl_json:
            save_ctdl_to_json(ctdl_json, filepath=os.path.join(app.config['UPLOAD_FOLDER'], "support_services_but.json"))
            json_filepath = os.path.join(app.config["UPLOAD_FOLDER"], "support_services_but.json")
            filtered_json_filepath = os.path.join(app.config["UPLOAD_FOLDER"], "filtered_output.json")
            output_csv = os.path.join(app.config["UPLOAD_FOLDER"], "support_services_but.csv")
            
            validate_json(json_filepath, filtered_json_filepath) # Validate and filter JSON
            json_file_to_csv(filtered_json_filepath, output_csv) # Convert JSON to CSV for bulk upload
            flash("Support services prepared for bulk upload successfully.", "success")
    
    if not ctdl_json:
        flash("No data returned from the Gemini API. Please check your input.", "error")
        return redirect(url_for('index'))
    
    return render_template('index.html', ctdl_json=ctdl_json, publish_method=publish_method)
    
#Download csv
@app.route('/download')
def download_csv():
    output_csv = os.path.join(app.config["UPLOAD_FOLDER"], "support_services_but.csv")
    if os.path.exists(output_csv):
        return send_file(output_csv, as_attachment=True) 
    else:
        return "File not found!", 404

if __name__ == '__main__':
    app.run(debug=True, port=8000)
