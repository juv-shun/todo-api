AWS_ACCOUNT_ID=`aws sts get-caller-identity | jq '.Account' -r`

.PHONY: build
build:
	docker build -t ${AWS_ACCOUNT_ID}.dkr.ecr.ap-northeast-1.amazonaws.com/todo-app:master .

.PHONY: push
push:
	aws ecr get-login-password \
		| docker login \
			--username AWS \
			--password-stdin https://${AWS_ACCOUNT_ID}.dkr.ecr.ap-northeast-1.amazonaws.com \
	&& docker push ${AWS_ACCOUNT_ID}.dkr.ecr.ap-northeast-1.amazonaws.com/todo-app:master
