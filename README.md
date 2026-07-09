# 🎙️ RealTime 文字おこし

マイク入力とデスクトップ音声(会議アプリ・動画などの再生音)を**同時に録音**しながら、**リアルタイムで文字起こし**し、**ワンクリックでAIが議事録をまとめる**ブラウザアプリです。

**ビルド不要・サーバー不要・単一HTMLファイル** — `index.html` をブラウザで開くだけで動きます。

## ✨ 機能

- 🎤 **マイク + 🖥️ デスクトップ音声の同時キャプチャ**(Web Audio APIでミックスして録音・保存)
- 📝 **リアルタイム文字起こし**(3エンジン切り替え)
  - **ブラウザ内蔵 (Web Speech API)** — 無料・設定不要。マイク音声のみ(Chrome / Edge / Android Chrome)
  - **Whisper互換API** — マイクとデスクトップ音声を*別々に*文字起こしし、`[マイク]` / `[デスクトップ]` の話者ラベル付きで表示(OpenAI / Groq / ローカルWhisperサーバー対応)
  - **ハイブリッド** — マイクは内蔵エンジン(低遅延・無料)、デスクトップ音声はWhisper API
- 📋 **ワンクリック議事録生成** — 文字起こし全文をAIに渡し、概要・決定事項・TODOを整理(ストリーミング表示、プロンプト編集可)
- 🤖 **AI連携**(プロバイダ切り替え式)
  - **LM Studio**(ローカル) / **Ollama**(ローカル)
  - **OpenAI** / **Groq** / **Anthropic (Claude)** / 任意のOpenAI互換API
- 📱 **タブレット対応** — レスポンシブUI・44px以上のタッチターゲット・録音中の画面スリープ防止(Wake Lock)
- 💾 録音音声(**MP3**・どこでも再生可/webm切替可)・文字起こし(.md)・議事録(.md)のダウンロード、タイムスタンプ付き表示、入力レベルメーター
- 🔒 データはすべてブラウザ内で処理。外部送信されるのは自分で設定したAPIへの音声チャンク/テキストのみ。設定は localStorage に保存

## 🚀 使い方

### 1. 開く

- `index.html` をダブルクリックしてブラウザ(**Chrome / Edge 推奨**)で開く
- または GitHub Pages 等の HTTPS でホスト
- ローカルサーバーでもOK: `python3 -m http.server 8080` → `http://localhost:8080`

> マイク権限のため、HTTPS / localhost / file:// のいずれかで開く必要があります。

### 2. 録音する

1. 「🎤 マイク」「🖥️ デスクトップ音声」の使う方にチェック
2. **● 録音開始** を押す
3. デスクトップ音声を使う場合、画面共有ダイアログで **「タブ」または「画面全体」を選び、「音声も共有」に必ずチェック**
   - Chrome (Windows): 「画面全体」でシステム音声を共有可能
   - Chrome (macOS): 「タブ」の音声のみ共有可能(Meet/Zoomのタブなどを選択)
4. 文字起こしがリアルタイムで流れます。**■ 停止** で終了(録音音声のダウンロードボタンが出ます)

> 録音は既定で **MP3**(モノラル128kbps・リアルタイムエンコード)で保存されます。⚙️設定の「録音の保存形式」で WebM/M4A に切り替え可能です。

### 3. 議事録を作る

1. ⚙️ **設定** タブで議事録AIを設定(下記)
2. 📋 **議事録** タブ → **✨ 議事録を作成** をクリック
3. 生成された議事録をコピー / .md でダウンロード

## ⚙️ AI設定

### LM Studio(ローカル・無料)

1. LM Studio でモデルをロードし、ローカルサーバーを起動(既定: `http://localhost:1234`)
2. **重要**: Developer タブ → Settings → **Enable CORS** をオンにする
3. アプリの設定でプロバイダ「LM Studio」を選択 → 「一覧取得」でモデルを選択

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
- `getUserMedia` + `getDisplayMedia` + Web Audio API(ミックス・レベル計測・無音検出)
- `MediaRecorder`(webm録音 + Whisper用チャンク録音)/ ScriptProcessor + lamejs(MP3リアルタイムエンコード)
- Web Speech API(リアルタイム認識・自動再接続)
- Fetch + SSE ストリーミング(OpenAI互換 / Anthropic Messages API)
