
# システム構築手順
## 概要
1. terraformを使って、AWSリソースを構築
   - tfstateファイルはローカルで管理します。
2. Cognitoユーザプールに、新規ユーザを追加
   - 本システムでは、サインアップ機能は用意しておらず、ユーザはaws cliコマンドを使って追加する。
   - 通常運用では、この手順を使ったユーザ作成は想定されないため、スクリプト化していない。
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

## 2. Cognitoユーザプールへのユーザ追加
### 作業環境
各自のPCにて本リポジトリをクローンして後述の手順を実施する。各自PCには以下の環境が整っていること。
- バージョン`0.14.8`以上のterraformがインストールされていること。
- aws-cli コマンドが利用可能であり、`aws configure`にて、AWS Access Key ID、AWS Secret Access Key、Default region nameがセットされていること。
- jqコマンドがインストールされていること。

### 作業手順
1. ユーザプールIDとクライアントIDを取得
   - 実施後、`userPoolId`、`clientId`変数に値がセットされていることを確認する。

    ```sh
    $ (cd infra/todo && export userPoolId=`terraform output -json | jq '.cognito_user_pool.value.user_pool_id' -r`)
    $ (cd infra/todo && export clientId=`terraform output -json | jq '.cognito_user_pool.value.user_pool_client_id' -r`)
    ```

2. ユーザ名、パスワード、メールアドレスを変数にセット
    - ユーザ名は文字列
    - パスワードは、8文字以上、大文字・小文字・数値がそれぞれ1文字以上含むこと

    ```sh
    $ export userName=
    $ export password=
    $ export email=
    ```

3. ユーザを作成

    ```sh
    $ aws cognito-idp admin-create-user \
        --user-pool-id ${userPoolId} \
        --username ${userName} \
        --user-attributes Name=email,Value="${email}" Name=email_verified,Value=true \
        --message-action SUPPRESS
    $ aws cognito-idp admin-set-user-password \
        --user-pool-id ${userPoolId} \
        --username ${userName} \
        --password ${password} \
        --permanent
    ```

## 3. デプロイ
### 作業環境
各自のPCにて本リポジトリをクローンして後述の手順を実施する。各自PCには以下の環境が整っていること。
- aws-cli コマンドが利用可能であり、`aws configure`にて、AWS Access Key ID、AWS Secret Access Key、Default region nameがセットされていること。

### 作業手順
1. Dockerイメージを生成
    - 実施後、ECRリポジトリにイメージがプッシュされていることを確認する。

    ```sh
    $ make build && make push
    ```

### 作業環境
デプロイ先のAWSアカウントのコンソールから実施する。

### 作業手順
1. 以下の箇所を変更し、サービスの更新を実行する。
    -
