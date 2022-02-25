
# デプロイ手順

## インフラ構築手順
### 作業環境
各自のPCにて本リポジトリをクローンして後述の手順を実施する。各自PCには以下の環境が整っていること。
- バージョン`0.14.8`以上のterraformがインストールされていること。
- aws-cli コマンドが利用可能であり、`aws configure`にて、AWS Access Key ID、AWS Secret Access Key、Default region nameがセットされていること。

### 作業手順
1. GitHubと連携
   1. 以下のAWSコンソールからGitHubと接続する。
     - https://ap-northeast-1.console.aws.amazon.com/codesuite/settings/connections?region=ap-northeast-1&connections-meta=eyJmIjp7InRleHQiOiIifSwicyI6e30sIm4iOjIwLCJpIjowfQ
   1. 生成した接続のARNを環境変数`TF_VAR_connection_star_github_arn`にセット。

2. その他のリソースを構築
   - terraform実施後、terraformが正常終了していることを確認する。

    ```sh
    $ cd infra
    $ terraform init
    $ terraform apply
    ```

## アプリケーションデプロイ手順
### 作業手順
1. 本リポジトリの`master`ブランチにプッシュし、CodePipeLineを起動する。
2. CodeDeployのライフサイクルが`AfterAllowTestTraffic`まで進んだら、「トラフィックの再ルーティング」ボタンをクリックする。
3. CodeDeployのライフサイクルが`AfterAllowTraffic`まで進んだら、「元のタスクセットの終了」ボタンをクリックする。
