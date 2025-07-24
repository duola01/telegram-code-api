
from flask import Flask, request, Response
import requests
from bs4 import BeautifulSoup
import concurrent.futures

app = Flask(__name__)

def process_entry(entry):
    phone = entry.get("phone", "").strip()
    url = entry.get("url", "").strip()

    if not url:
        return f"{phone or '[无号码]'} - 无效链接"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10, verify=False)
        resp.raise_for_status()
        html = resp.text
    except requests.exceptions.RequestException as e:
        return f"{phone or '[无号码]'} - 请求失败: {e}"

    soup = BeautifulSoup(html, "html.parser")
    code_elem = soup.find("input", {"id": "code"})
    pass_elem = soup.find("input", {"id": "pass2fa"})

    code = code_elem["value"].strip() if code_elem and code_elem.has_attr("value") else "未找到验证码"
    passwd = pass_elem["value"].strip() if pass_elem and pass_elem.has_attr("value") else "无密码"

    return f"{phone or '[无号码]'} - {code} - {passwd}"

@app.route("/batch-codes", methods=["POST"])
def batch_codes():
    data = request.get_json()
    if not isinstance(data, list):
        return Response("请求体必须是一个 JSON 数组", status=400)

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(process_entry, data))
        return Response("\n".join(results), mimetype="text/plain")
    except Exception as e:
        return Response(f"处理请求时出错: {e}", status=500)

@app.route("/")
def index():
    return "Telegram Code Extractor API"

@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    traceback.print_exc()
    return Response(f"服务器内部错误: {e}", status=500)
