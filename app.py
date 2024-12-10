import requests
import random
from flask import Flask, jsonify
from threading import Thread, Event

app = Flask(__name__)

# In-memory log storage and control
logs = []
running_event = Event()

# Function to log in to an account
def login(session, email, password):
    login_url = 'https://golperjhuri.com/login.php'
    login_payload = {
        'user_email': email,
        'user_pass': password,
        'remamber': 'on'
    }
    response = session.post(login_url, data=login_payload)
    return response.status_code == 200

# Function to post a comment
def post_comment(session, story_id, comment, account_name):
    story_url = f'https://golperjhuri.com/story.php?id={story_id}'
    headers = {
        'origin': 'https://golperjhuri.com',
        'referer': story_url,
        'user-agent': 'Mozilla/5.0 (Linux; Android 11; CPH2127 Build/RKQ1.201217.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/101.0.4951.61 Mobile Safari/537.36 FB_IAB/Orca-Android;FBAV/362.0.0.8.108;',
    }
    comment_data = {
        'member_name': '',
        'c_name': account_name,
        'c_email': '',
        'c_story': story_id,
        'c_comment': comment,
        'comment_submit': 'মন্তব্য করুন'
    }
    response = session.post(story_url, headers=headers, data=comment_data)
    return response.status_code == 200

# Function to get a response from the Gemini API
def get_gemini_response(prompt):
    gemini_url = f'https://api.pikaapis.my.id/gemini.php?prompt={prompt}'
    response = requests.get(gemini_url)
    if response.status_code == 200:
        gemini_data = response.json()
        return gemini_data.get('content', '').strip()
    return None

# Function to generate a new prompt based on previous response
def generate_new_prompt():
    prompt_variations = [
        "তুমি কি মনে করো কৃত্রিম বুদ্ধিমত্তা ভবিষ্যতে মানুষকে প্রতিস্থাপন করতে পারবে?",
        "কৃত্রিম বুদ্ধিমত্তা কি মানব জীবনের কোন কোন ক্ষেত্রে সর্বাধিক প্রভাব ফেলতে পারে?",
        "তুমি কি মনে করো AI এর সাহায্যে আমরা পরিবেশগত সমস্যাগুলি সমাধান করতে পারি?",
        "ভবিষ্যতের প্রযুক্তি কি মানবিক মূল্যবোধকে প্রভাবিত করবে? কিভাবে?",
        "তুমি কি মনে করো যে কৃত্রিম বুদ্ধিমত্তা মানুষের সৃজনশীলতাকে অতিক্রম করতে পারবে?",
        "কিভাবে AI এবং মানুষের সহযোগিতা সমাজের উন্নয়নে সাহায্য করতে পারে?",
        "তুমি কি মনে করো যে AI শিক্ষা ব্যবস্থায় বিপ্লব ঘটাতে পারে? কিভাবে?",
        "AI এর নিরাপত্তা নিয়ে তোমার কি ধরণের উদ্বেগ আছে?",
        "তুমি কি মনে করো AI এবং রোবোটিক্সের উন্নতি আমাদের কাজের পরিবেশ পরিবর্তন করবে?",
        "কৃত্রিম বুদ্ধিমত্তার উন্নয়নে কোন ধরনের নৈতিক দিকগুলি বিবেচনা করা উচিত?",
        "তুমি কি মনে করো AI এর বিকাশে কোন ধরনের আইনি সীমাবদ্ধতা থাকা উচিত?",
        "ভবিষ্যতে AI কি মানব সম্পর্কগুলোকে প্রভাবিত করবে?"
    ]
    return random.choice(prompt_variations)

# Function to perform interactions
def perform_interactions():
    session1 = requests.Session()
    session2 = requests.Session()

    # Account credentials and names
    account1 = {'email': 'm1hyl25w@gmail.com', 'password': '@@@@11Aa', 'name': 'ROBO ONE'}
    account2 = {'email': 'jy7485ocx@gmail.com', 'password': '@@@@11Aa', 'name': 'ROBO TWO'}

    # Story ID to comment on
    story_id = '41225'
    posted_comments = set()

    # Login both accounts
    if login(session1, account1['email'], account1['password']):
        logs.append(f'{account1["name"]} logged in successfully.')
    else:
        logs.append(f'Failed to log in {account1["name"]}.')
        return

    if login(session2, account2['email'], account2['password']):
        logs.append(f'{account2["name"]} logged in successfully.')
    else:
        logs.append(f'Failed to log in {account2["name"]}.')
        return

    # Initial prompt with a random topic
    current_prompt = generate_new_prompt()
    current_account = account1
    other_account = account2

    if current_prompt not in posted_comments and post_comment(session1, story_id, current_prompt, current_account['name']):
        logs.append(f'{current_account["name"]} posted a comment successfully.')
        posted_comments.add(current_prompt)

    while running_event.is_set():
        current_account, other_account = other_account, current_account

        retries = 0
        max_retries = 2
        gemini_response = None

        while retries < max_retries:
            gemini_response = get_gemini_response(prompt=current_prompt)
            retries += 1
            if gemini_response and gemini_response not in posted_comments:
                break
            else:
                logs.append('Retrying to get a unique response from the Gemini API...')
        
        if gemini_response and gemini_response not in posted_comments:
            if post_comment(session1 if current_account == account1 else session2, story_id, gemini_response, current_account['name']):
                logs.append(f'{current_account["name"]} responded successfully using Gemini API.')
                posted_comments.add(gemini_response)
                current_prompt = gemini_response
            else:
                logs.append(f'Failed to post response from {current_account["name"]}.')
        else:
            logs.append('Failed to get a unique response after several attempts. Switching to a new topic.')
            current_prompt = generate_new_prompt()

# Flask route to start the bot
@app.route('/start', methods=['GET'])
def start_bot():
    if not running_event.is_set():
        running_event.set()
        thread = Thread(target=perform_interactions)
        thread.start()
        logs.append("Bot started.")
        return jsonify({"status": "Bot started"}), 200
    else:
        return jsonify({"status": "Bot is already running"}), 200

# Flask route to stop the bot
@app.route('/stop', methods=['GET'])
def stop_bot():
    if running_event.is_set():
        running_event.clear()
        logs.append("Bot stopped.")
        return jsonify({"status": "Bot stopped"}), 200
    else:
        return jsonify({"status": "Bot is not running"}), 200

# Endpoint to view logs
@app.route('/logs', methods=['GET'])
def view_logs():
    return jsonify(logs[-100:]), 200  # Return the last 100 logs

# Auto-ping endpoint
@app.route('/ping', methods=['GET'])
def ping():
    return "Pong!", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
