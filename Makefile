PHONY: up

up:
	docker-compose up --build -d

up-prod:
	docker-compose -f docker-compose-prod.yaml up --build -d

update-prod:
	docker-compose -f docker-compose-prod.yaml up --build -d celery_worker django_web celery_beat proxy

update:
	docker-compose -f docker-compose.yaml up --build -d celery_worker django_web celery_beat