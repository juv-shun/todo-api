AWS_ACCOUNT_ID=`aws sts get-caller-identity | jq '.Account' -r`

.PHONY: build
build:
	docker build -t ${AWS_ACCOUNT_ID}.dkr.ecr.ap-northeast-1.amazonaws.com/todo-app:latest .

.PHONY: push
push:
	aws ecr get-login-password \
		| docker login \
			--username AWS \
			--password-stdin https://${AWS_ACCOUNT_ID}.dkr.ecr.ap-northeast-1.amazonaws.com \
	&& docker push ${AWS_ACCOUNT_ID}.dkr.ecr.ap-northeast-1.amazonaws.com/todo-app:latest

.PHONY: test
test:
	docker-compose up -d \
		&& docker exec -it todo_app sh -c "poetry install && pytest -v" \
		&& docker-compose down
