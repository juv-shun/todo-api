
# システム構築手順
## 概要
1. terraformを使って、AWSリソースを構築
   - tfstateファイルはローカルで管理します。
2. アプリケーションのDockerイメージをビルド
3. アプリケーションをデプロイ

## 1. AWSリソースの作成
### 作業環境
各自のPCにて本リポジトリをクローンして後述の手順を実施する。各自PCには以下の環境が整っていること。
- バージョン`0.14.8`以上のterraformがインストールされていること。
- aws-cli コマンドが利用可能であり、`aws configure`にて、AWS Access Key ID、AWS Secret Access Key、Default region nameがセットされていること。

### 作業手順
1. VPCネットワークを構築
   - terraform実施後、terraformが正常終了していることを確認する。

    ```sh
    $ (cd infra/network && terraform init && terraform apply)
    ```

2. その他アプリケーションで利用するAWSリソースの構築
   - terraform実施後、terraformが正常終了していることを確認する。

    ```sh
    $ (cd infra/todo && terraform init && terraform apply)
    ```

## 2. Dockerイメージを作成
### 作業環境
各自のPCにて本リポジトリをクローンして後述の手順を実施する。各自PCには以下の環境が整っていること。
- aws-cli コマンドが利用可能であり、`aws configure`にて、AWS Access Key ID、AWS Secret Access Key、Default region nameがセットされていること。

### 作業手順
1. Dockerイメージを生成
    - 実施後、ECRリポジトリにイメージがプッシュされていることを確認する。

    ```sh
    $ make build && make push
    ```

## 3. アプリケーションのデプロイ
### 作業環境
デプロイ先のAWSアカウントのコンソールから実施する。

### 作業手順
1. 以下の設定で、ECSサービスの更新を実行する。
    - 新しいデプロイの強制: チェックマークをつける
    - タスクの数: 必要なタスク数を入力
2. CodeDeployのライフサイクルが`AfterAllowTestTraffic`まで進んだら、「トラフィックの再ルーティング」ボタンをクリックする。
3. CodeDeployのライフサイクルが`AfterAllowTraffic`まで進んだら、「元のタスクセットの終了」ボタンをクリックする。
