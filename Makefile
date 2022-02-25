.PHONY: test
test:
	docker-compose up -d \
		&& docker exec -it todo_app sh -c "poetry install && pytest -v" \
		&& docker-compose down
