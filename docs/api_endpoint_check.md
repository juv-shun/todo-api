# API 試用手順
## 概要
`http://{{ドメイン名}}/docs` からAPIの試行が可能である。
しかし、本システムは、ユーザ認証機能は存在するが、ユーザ作成機能は有していない。したがって、以下の手順でユーザを作成する。
### 作業環境
各自のPCにて本リポジトリをクローンして後述の手順を実施する。各自PCには以下の環境が整っていること。
- バージョン`0.14.8`以上のterraformがインストールされていること。
- aws-cli コマンドが利用可能であり、`aws configure`にて、AWS Access Key ID、AWS Secret Access Key、Default region nameがセットされていること。
- jqコマンドがインストールされていること。

### 作業手順
1. ユーザプールIDとクライアントIDを取得
   - 実施後、`userPoolId`、`clientId`変数に値がセットされていることを確認する。

    ```sh
    $ cd infra/todo
    $ userPoolId=`terraform output -json | jq '.cognito_user_pool.value.user_pool_id' -r`
    $ clientId=`terraform output -json | jq '.cognito_user_pool.value.user_pool_client_id' -r`
    ```

2. ユーザ名、パスワード、メールアドレスを変数にセット
    - ユーザ名は文字列
    - パスワードは、8文字以上、大文字・小文字・数値がそれぞれ1文字以上含むこと

    ```sh
    $ userName=
    $ password=
    $ email=
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

4. (補足)以下のコマンドを実行することで、ユーザのIDトークンを取得することができます。

    ```sh
    id_token=`aws cognito-idp admin-initiate-auth \
        --user-pool-id ${userPoolId} \
        --client-id ${clientId} \
        --auth-flow "ADMIN_USER_PASSWORD_AUTH" \
        --auth-parameters USERNAME=${userName},PASSWORD=${password} \
            | jq '.AuthenticationResult.IdToken' -r`
    ```
