# 🎙️ RealTime 文字おこし

マイク入力とデスクトップ音声(会議アプリ・動画などの再生音)を**同時に録音**しながら、**リアルタイムで文字起こし**し、**ワンクリックでAIが議事録をまとめる**ブラウザアプリです。

**ビルド不要・サーバー不要・単一HTMLファイル** — `index.html` をブラウザで開くだけで動きます。

## ✨ 機能

- 🎤 **マイク + 🖥️ デスクトップ音声の同時キャプチャ**(Web Audio APIでミックスして録音・保存)
- 🔇 **3段階のマイクノイズ除去** — 「強」ではブラウザ内蔵処理に声帯域フィルターと適応型ノイズゲートを重ね、サーキュレーターなどの定常音を低減
- 📝 **リアルタイム文字起こし**(4エンジン切り替え)
  - **ブラウザ内蔵 (Web Speech API)** — 無料・設定不要。マイク音声のみ(Chrome / Edge / Android Chrome)
  - **ローカル faster-whisper** — クラウドAPI・APIキー不要。端末内でマイクとデスクトップ音声を文字起こし
  - **Whisper互換API** — マイクとデスクトップ音声を*別々に*文字起こしし、`[マイク]` / `[デスクトップ]` の話者ラベル付きで表示(OpenAI / Groq / ローカルWhisperサーバー対応)
  - **ハイブリッド** — マイクは内蔵エンジン(低遅延・無料)、デスクトップ音声はWhisper API
- 📋 **ワンクリック議事録生成** — 文字起こし全文をAIに渡し、概要・決定事項・TODOを整理(ストリーミング表示、プロンプト編集可)
- 🤖 **AI連携**(プロバイダ切り替え式)
  - **LM Studio**(ローカル) / **Ollama**(ローカル)
  - **OpenAI** / **Groq** / **Anthropic (Claude)** / 任意のOpenAI互換API
- 📱 **タブレット対応** — レスポンシブUI・44px以上のタッチターゲット・録音中の画面スリープ防止(Wake Lock)
- 💾 録音音声(**MP3**・どこでも再生可/webm切替可)・文字起こし(.md)・議事録(.md)のダウンロード、タイムスタンプ付き表示、入力レベルメーター
- 🔒 データはブラウザ内、または自分で起動したローカル faster-whisper で処理。外部送信されるのは自分で設定したAPIへの音声チャンク/テキストのみ。設定は localStorage に保存

## 🚀 使い方

### 1. 開く

- `index.html` をダブルクリックしてブラウザ(**Chrome / Edge 推奨**)で開く
- または GitHub Pages 等の HTTPS でホスト
- ローカルサーバーでもOK: `python3 -m http.server 8080` → `http://localhost:8080`

> マイク権限のため、HTTPS / localhost / file:// のいずれかで開く必要があります。

### 2. 録音する

1. 「🎤 マイク」「🖥️ デスクトップ音声」の使う方にチェック（サーキュレーターなどの定常音がある場合は、⚙️設定 →「マイクのノイズ除去」を「強」に設定）
2. **● 録音開始** を押す
3. デスクトップ音声を使う場合、画面共有ダイアログで **「タブ」または「画面全体」を選び、「音声も共有」に必ずチェック**
   - Chrome (Windows): 「画面全体」でシステム音声を共有可能
   - Chrome (macOS): 「タブ」の音声のみ共有可能(Meet/Zoomのタブなどを選択)
4. 文字起こしがリアルタイムで流れます。**⏸ 一時停止**では録音と文字起こしの両方を止め、**▶ 再開**で同じセッションを継続できます。**■ 停止**で終了します(録音音声のダウンロードボタンが出ます)

> 録音は既定で **MP3**(モノラル128kbps・リアルタイムエンコード)で保存されます。⚙️設定の「録音の保存形式」で WebM/M4A に切り替え可能です。

### 3. 議事録を作る

1. ⚙️ **設定** タブで議事録AIを設定(下記)
2. 📋 **議事録** タブ → **✨ 議事録を作成** をクリック
3. 生成された議事録をコピー / .md でダウンロード

### ローカル faster-whisper を使う（クラウドAPI不要）

ブラウザだけでは Python の faster-whisper を直接実行できないため、付属のローカルプロセスを起動します。音声は `localhost` にだけ送られ、外部の文字起こしAPIやAPIキーは使いません。

#### Windows（推奨・ダブルクリックで環境を準備）

1. Python 3.10以上を [python.org](https://www.python.org/downloads/windows/) からインストールする。その際、インストーラーの **Add python.exe to PATH** をオンにする
2. `start_local_whisper_windows.bat` をダブルクリックする
3. 初回は仮想環境の作成と必要パッケージのインストールに数分かかる。`Starting local faster-whisper at http://127.0.0.1:8000` と表示された黒い画面を閉じない
4. アプリの「⚙️ 設定」→「ローカル faster-whisper」で「接続テスト」を押す
5. 接続成功後に録音を開始する

この起動ファイルはプロジェクト専用の `.venv` を作り、`fastapi`、`faster-whisper` など不足している環境を自動的にインストールします。エラー時には画面を閉じずに停止するため、表示内容を確認できます。

#### macOS / Linux（手動セットアップ）

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-local-whisper.txt
python local_whisper_server.py
```

初回の文字起こし時には選択したモデルがダウンロードされます。アプリの「⚙️ 設定」でエンジンを「ローカル faster-whisper」にし、URL（既定 `http://localhost:8000`）とモデルを選択してください。NVIDIA GPUを明示的に使う場合は `python local_whisper_server.py --device cuda --compute-type float16`、CPUで軽量に動かす場合は `--device cpu --compute-type int8` を指定できます。

#### `ModuleNotFoundError: No module named 'fastapi'` / `Failed to fetch` の場合

- `ModuleNotFoundError` は、必要なPythonパッケージがまだインストールされていないことを示します。IDLEの「Run Module」や `local_whisper_server.py` の直接ダブルクリックではなく、Windowsでは `start_local_whisper_windows.bat` を実行してください
- `Failed to fetch` は、多くの場合サーバーが起動していないために表示されます。起動用の黒い画面を閉じず、設定画面の「接続テスト」が成功することを確認してください
- ブラウザで <http://127.0.0.1:8000/health> を開き、`{"status":"ok"}` が表示されればサーバーは正常です
- URL欄は `http://localhost:8000` または `http://127.0.0.1:8000` とします。末尾に `/v1` は付けません
- アプリ自体も `python3 -m http.server 8080`（Windowsでは `py -3 -m http.server 8080`）で配信し、ChromeまたはEdgeから `http://localhost:8080` を開くことを推奨します

#### 「Unable to load a worklet's module」と表示される場合

これは faster-whisper の設定ではなく、マイクの「強」ノイズ除去に使う AudioWorklet をブラウザが読み込めない場合に発生するエラーです。更新後のアプリでは自動的にブラウザ標準のノイズ除去へ切り替えて録音を続行します。回避したい場合は、次のいずれかを行ってください。

- `index.html` の直接起動（`file://`）ではなく、リポジトリで `python3 -m http.server 8080` を実行し、ChromeまたはEdgeで `http://localhost:8080` を開く
- 「⚙️ 設定」→「マイクのノイズ除去」を「標準」にする（AudioWorkletを使用しません）

なお、ローカル faster-whisper を選ぶ場合は、別のターミナルで `python local_whisper_server.py` も起動したままにしてください。

## ⚙️ AI設定

### LM Studio(ローカル・無料)

1. LM Studio でモデルをロードし、ローカルサーバーを起動(既定: `http://localhost:1234`)
2. **重要**: Developer タブ → Settings → **Enable CORS** をオンにする
3. アプリの設定でプロバイダ「LM Studio」を選択し、`Reachable at:` の URL をベースURLへ入力 → 「一覧取得」でモデルを選択

`Reachable at:` が `http://192.168.1.10:1234` のように表示される場合、そのまま入力できます。OpenAI互換APIに必要な末尾の `/v1` はアプリが自動補完します。手動で `http://192.168.1.10:1234/v1` と入力しても構いません。

#### 議事録ではなく思考過程が表示される場合

`Here's a thinking process...` のような分析文は議事録ではなく、Qwenなどのthinkingモデルが出力する内部推論です。アプリはLM Studioへthinkingを無効化する設定と `/no_think` を送信し、内部推論を議事録として採用しません。

それでも最終回答が返らない場合は、LM Studioで **Instruct / Chat版** のモデルがロードされているか確認してください。Base版ではなく、日本語指示への追従性能があるモデルを推奨します。9BクラスのInstructモデルで通常は要約できますが、長い文字起こしではコンテキスト長と予測トークン数も十分に設定してください。

`receivedAnswer is not defined` と表示された場合はモデルやLM Studioへの接続の問題ではなく、更新前のJavaScriptがブラウザに残っています。最新版では接続テストを議事録のストリーミング処理から分離しています。最新版の `index.html` を開き直し、Chrome / Edgeで `Ctrl+Shift+R`（macOSは `Command+Shift+R`）を押してキャッシュを無視して再読み込みしてください。

### Ollama(ローカル・無料)

- ベースURL: `http://localhost:11434/v1`
- ブラウザから接続できない場合は環境変数 `OLLAMA_ORIGINS=*` を設定して再起動

### クラウドAI

| プロバイダ | ベースURL | 備考 |
|---|---|---|
| OpenAI | `https://api.openai.com/v1` | APIキー必須 |
| Groq | `https://api.groq.com/openai/v1` | 無料枠あり・高速 |
| Anthropic | `https://api.anthropic.com/v1` | APIキー必須(例: `claude-sonnet-5`) |
| その他 | 任意のOpenAI互換URL | プロバイダ「カスタム」を選択 |

### Whisper互換API(音声認識)

デスクトップ音声の文字起こしや、Web Speech API非対応ブラウザで使用します。

| サービス | ベースURL | モデル例 |
|---|---|---|
| OpenAI | `https://api.openai.com/v1` | `whisper-1` |
| Groq | `https://api.groq.com/openai/v1` | `whisper-large-v3` |
| ローカル ([speaches](https://github.com/speaches-ai/speaches) / faster-whisper-server 等) | `http://localhost:8000/v1` | サーバー依存 |

音声は「Whisper送信間隔」(既定15秒)ごとに区切ってAPIへ送信されます。ほぼ無音の区間は送信をスキップしてコストを抑えます。

## 📱 タブレットでの利用

- **Android タブレット (Chrome)**: マイク文字起こし(内蔵エンジン)・議事録生成が動作。デスクトップ音声キャプチャは非対応のため自動的に無効化されます
- **iPad (Safari)**: Whisper互換APIエンジンでのマイク文字起こしを推奨(Web Speech APIの対応が不安定なため)
- 録音中は画面がスリープしないよう Wake Lock を取得します

## ⚠️ 注意事項

- APIキーはブラウザの localStorage に保存されます。共用端末では使用後に「設定をリセット」してください
- 内蔵エンジン(Web Speech API)は音声をブラウザベンダーのサーバーに送信して認識します
- 会議の録音は参加者の同意を得た上で行ってください

## 🛠️ 技術構成

- Vanilla JS / 単一HTML(外部リクエストなし。MP3エンコーダ [lamejs](https://github.com/zhuker/lamejs)(LGPL-3.0)をインライン同梱)
- `getUserMedia` + `getDisplayMedia` + Web Audio API(ミックス・レベル計測・無音検出・適応型ノイズゲート)
- `MediaRecorder`(webm録音 + Whisper用チャンク録音)/ ScriptProcessor + lamejs(MP3リアルタイムエンコード)
- Web Speech API(リアルタイム認識・自動再接続)
- Fetch + SSE ストリーミング(OpenAI互換 / Anthropic Messages API)
