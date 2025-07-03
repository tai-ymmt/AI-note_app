from flask import Flask, render_template, request, redirect, jsonify
from google import genai 


app = Flask(__name__)

# 仮のノートデータ
notes = [
    {'id': 1, 'title': 'サンプルノート1', 'content': '<b>これはサンプルです。</b>'},
    {'id': 2, 'title': 'メモ', 'content': '本文2'},
    {'id': 3, 'title': 'サンプルノート2', 'content': '<b>これはサンプルです。</b>'},
    {'id': 4, 'title': '削除ノート', 'content': '削除確認のノート'}
]

def find_note(note_id):
    for note in notes:
        if note['id'] == note_id:
            return note
    return None

# APIキーの設定
GENAI_API_KEY = "AIzaSyCjjC-YoxhZIzNlCfznMeKQg138BptwDHU"
client = genai.Client(api_key=GENAI_API_KEY)

# トップページはノート一覧（index.html）
@app.route('/')
def index():
    return render_template('index.html', notes=notes)

# ノート編集ページ（note.html）
@app.route('/note/<int:note_id>')
def edit_note(note_id):
    note = find_note(note_id)
    if not note:
        return "ノートが見つかりません", 404
    return render_template('note.html', note=note)

next_note_id = max(note['id'] for note in notes) + 1 if notes else 1

@app.route('/note/create', methods=['POST'])
def create_note():
    global notes, next_note_id
    new_note = {
        'id': next_note_id,
        'title': '新しいノート',
        'content': ''
    }
    notes.append(new_note)
    note_id = next_note_id
    next_note_id += 1
    return jsonify({'note_id': note_id})


@app.route('/note/<int:note_id>/save', methods=['POST'])
def save_note(note_id):
    note = find_note(note_id)
    if not note:
        return jsonify({'error': 'ノートが見つかりません'}), 404
    data = request.json
    note['title'] = data.get('title', note['title'])
    note['content'] = data.get('content', note['content'])
    return jsonify({'message': '保存しました'})

@app.route('/note/<int:note_id>/delete', methods=['POST'])
def delete_note(note_id):
    global notes
    notes = [note for note in notes if note['id'] != note_id]
    return jsonify({'message': '削除しました'})

# AI関連API
@app.route('/api/ai_search', methods=['POST'])
def ai_search():
    data = request.json
    keyword = data.get('keyword', '').strip()
    if not keyword:
        return jsonify({'result': 'キーワードを入力してください'}), 400

    prompt = f"{keyword}について日本語で**200文字程度で**解説してください。"
    try:
        # APIキーをここで渡す
        client = genai.Client(api_key=GENAI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        summary = response.text.strip()
    except Exception:
        import traceback
        traceback.print_exc()
        summary = "AIによる解説の取得中にエラーが発生しました"
    return jsonify({'result': summary})


@app.route('/api/ai_settings', methods=['POST'])
def ai_settings():
    return jsonify({'message': 'AI設定を保存しました'})

if __name__ == '__main__':
    app.run(debug=True)
