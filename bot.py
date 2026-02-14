import os
import time
import random
from flask import Flask, request, jsonify, render_template
from threading import Thread

app = Flask(__name__)

# Bot status storage
bot_status = {
    'running': False,
    'channel_url': '',
    'target': 0,
    'current': 0,
    'logs': []
}

def add_log(message):
    timestamp = time.strftime('%H:%M:%S')
    bot_status['logs'].append(f"[{timestamp}] {message}")
    if len(bot_status['logs']) > 100:
        bot_status['logs'].pop(0)
    print(message)

def run_bot_job(channel_url, target):
    """Background job for bot"""
    bot_status['running'] = True
    bot_status['channel_url'] = channel_url
    bot_status['target'] = target
    bot_status['current'] = 0
    add_log("🚀 Bot started!")
    
    for i in range(target):
        if not bot_status['running']:
            add_log("⏹️ Bot stopped by user")
            break
        bot_status['current'] += 1
        add_log(f"✅ Subscriber #{bot_status['current']} added")
        time.sleep(random.randint(10, 20)) # Wait 10-20 sec
    
    add_log("✅ Bot finished!")
    bot_status['running'] = False

@app.route('/')
def home():
    return render_template('index.html') # HTML page for manual control

# ----- API Endpoints -----
@app.route('/api/start', methods=['POST'])
def api_start():
    if bot_status['running']:
        return jsonify({'error': 'Bot already running'}), 400
    data = request.json
    channel_url = data.get('channel_url')
    target = int(data.get('target', 50))
    if not channel_url:
        return jsonify({'error': 'Channel URL required'}), 400
    bot_status['logs'] = [] # Clear old logs
    thread = Thread(target=run_bot_job, args=(channel_url, target))
    thread.daemon = True
    thread.start()
    return jsonify({'success': True, 'message': 'Bot started'})

@app.route('/api/stop', methods=['POST'])
def api_stop():
    bot_status['running'] = False
    return jsonify({'success': True, 'message': 'Bot stopped'})

@app.route('/api/status')
def api_status():
    return jsonify({
        'running': bot_status['running'],
        'channel': bot_status['channel_url'],
        'target': bot_status['target'],
        'current': bot_status['current']
    })

@app.route('/api/logs')
def api_logs():
    return jsonify({'logs': bot_status['logs']})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)