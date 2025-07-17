from flask import Flask, request, jsonify
import cccc
import threading
import logging

app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

# 设置最大并发请求数
MAX_CONCURRENT_REQUESTS = 5
semaphore = threading.BoundedSemaphore(MAX_CONCURRENT_REQUESTS)

@app.route('/')
def index():
    return "Flask 视频解析服务已启动！使用 /api/parse 接口解析视频。"

@app.route('/api/parse', methods=['GET'])
def parse_video_route():
    # 获取视频链接
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"success": False, "error": "缺少视频链接参数"}), 400

    app.logger.info(f"收到解析请求：{video_url}")

    # 尝试获取信号量（最多 MAX_CONCURRENT_REQUESTS 个并发）
    if not semaphore.acquire(blocking=False):
        app.logger.warning("并发限制已达到，拒绝请求")
        return jsonify({
            "success": False,
            "error": f"服务繁忙，请稍后再试（当前最大并发数：{MAX_CONCURRENT_REQUESTS}）"
        }), 429  # Too Many Requests

    try:
        app.logger.info(f"开始解析视频：{video_url}")
        result = cccc.parse_video(video_url)
        if result:
            return jsonify({"success": True, "video_url": result})
        else:
            return jsonify({"success": False, "error": "解析失败，请检查链接是否有效"}), 500
    finally:
        semaphore.release()  # 释放信号量

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)