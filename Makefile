

.PHONY: \
	docker-build \
	docker-up-app \
	docker-up-python \
	docker-deploy-content \
	google-build-deploy \
	google-build \
	google-deploy


docker-build:
	. ./scripts/setup_secrets_local.sh ;\
	docker build -t flashcards:1.0 ./ 

docker-up-app:
	. ./scripts/setup_secrets_local.sh ;\
	docker run \
		-e PORT=5000 \
		-e SECRETS="$$SECRETS" \
		-p 5000:5000 \
		--rm  \
		flashcards:1.0 ; 

docker-up-python:
	. ./scripts/setup_secrets_local.sh ;\
	docker run -e SECRETS="$$SECRETS" --rm -it flashcards:1.0 python

docker-deploy-content:
	. ./scripts/setup_secrets_local.sh ;\
	docker run -e SECRETS="$$SECRETS" --rm -it flashcards:1.0 python ./scripts/update_database.py


google-build-deploy: google-build google-deploy

google-build:
	gcloud builds submit ./  --tag "$$(jq -r '.GOOGLE_IMAGE'  ./secrets/secrets_global.json)"

google-deploy:
	gcloud run deploy flashcards \
		--image "$$(jq -r '.GOOGLE_IMAGE' ./secrets/secrets_global.json)"\
		--region="$$(jq -r '.GOOGLE_REGION' ./secrets/secrets_global.json)"\
		--platform managed \
		--allow-unauthenticated \
		--service-account="$$(jq -r '.GOOGLE_SERVICE_ACCOUNT' ./secrets/secrets_global.json)"\
		--update-env-vars SECRETS="$$(base64 ./secrets/secrets_global.json)"

