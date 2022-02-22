PHONY: up

up:
	docker-compose up --build -d

up-prod:
	docker-compose -f docker-compose-prod.yaml up --build -d

update-prod:
	docker-compose -f docker-compose-prod.yaml up celery_worker django_web celery_beat proxy --build -d 

update:
	docker-compose -f docker-compose.yaml up celery_worker django_web celery_beat --build -d 