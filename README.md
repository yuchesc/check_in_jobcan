# ジョブ●ン勤怠ログインLambda関数

ジョブ●ン共通ID対応版

## venv作成〜アップロード

```bash
python3 -m venv ~/.venv/jobcan
source ~/.venv/jobcan/bin/activate

cd check_in_jobcan
pip3 install boto3, requests, lambda-uploader
pip3 install 'beautifulsoup4==4.6.0' -t .

# Build
lambda-uploader -e ~/.venv/jobcan --variables '{"user_email": "***@***.co.jp","user_password": "******","sns_topic_arn": "arn:aws:sns:ap-northeast-1:***:jobcan"}'
```

## 環境変数

* user_email ログインID
* user_password ログインパスワード
* sns_topic_arn (optional) 成功/失敗をメール通知する想定

## 参考

* AWS LambdaでBeautiful Soupを使う場合はインストール手順が特殊になる。 

https://qiita.com/ryo-yamaoka/items/bbd69deeeef2d586c3c5
