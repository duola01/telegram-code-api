from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return "Telegram Code API running with CORS."

@app.route("/batch-codes", methods=["POST"])
def batch_codes():
    data = request.get_json()
    results = []

    for entry in data:
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

        results.append(f"{phone} - {code} - {pwd}")

    return "\n".join(results)