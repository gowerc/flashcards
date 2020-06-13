

.PHONY: \
	local-python-init \
	app-up-local \
	app-up-docker \
	google-build-deploy \
	google-build \
	google-deploy


app-up-local:
	. ./venv/bin/activate; \
	export FLASK_APP=app.py \
	export LOCAL_GOOGLE_AUTH_URL=$$(jq '.GOOGLE_AUTH_URL' ./secrets/secrets_local.json); \
	export SECRETS=$$(cat ./secrets/secrets_global.json | jq ".GOOGLE_AUTH_URL=$$LOCAL_GOOGLE_AUTH_URL" | base64); \
	flask run


app-up-docker:
	docker build -t flashcards:1.0 ./ ;\
	docker run \
		-e PORT=5000 \
		-e SECRETS=$$(base64 secrets/secrets_global.json) \
		-p 5000:5000 \
		--rm  \
		flashcards:1.0


google-build-deploy: google-build google-deploy

google-build:
	gcloud builds submit ./ --tag "$$(jq -r '.GOOGLE_IMAGE' < secrets/secrets_global.json)"

google-deploy:
	gcloud run deploy flashcards \
		--image "$$(jq -r '.GOOGLE_IMAGE' < secrets/secrets_global.json)"\
		--region="$$(jq -r '.GOOGLE_REGION' < secrets/secrets_global.json)"\
		--platform managed \
		--allow-unauthenticated \
		--service-account="$$(jq -r '.GOOGLE_SERVICE_ACCOUNT' < secrets/secrets_global.json)"\
		--update-env-vars SECRETS=$$(base64 secrets/secrets_global.json)




local-python-up: 
	. venv/bin/activate; \
	export SECRETS=$$(base64 secrets/secrets_global.json); \
	python
