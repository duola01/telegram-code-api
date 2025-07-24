from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import concurrent.futures

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return "Telegram Code API with CORS and POST fixed."

def process_entry(entry):
    phone = entry.get("phone", "")
    url = entry.get("url", "")
    code = ""
    pwd = ""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10, verify=False)
        soup = BeautifulSoup(resp.text, "html.parser")
        code_tag = soup.find("input", {"id": "code"})
        pwd_tag = soup.find("input", {"id": "password"})

        if code_tag and code_tag.has_attr("value"):
            code = code_tag["value"]
        if pwd_tag and pwd_tag.has_attr("value"):
            pwd = pwd_tag["value"]

    except Exception as e:
        code = "错误"
        pwd = str(e)

    return f"{phone} - {code} - {pwd}"

@app.route("/batch-codes", methods=["POST"])
def batch_codes():
    entries = request.get_json(force=True)
    if not isinstance(entries, list):
        return jsonify({"error": "Expected a list of {phone, url} objects"}), 400

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_entry, entries))

    return "\n".join(results), 200, {"Content-Type": "text/plain; charset=utf-8"}