

.PHONY: \
	local-python-init \
	local-python-down \
	local-python-init \
	app-up-local \
	app-up-docker \
	google-build-deploy \
	google-build \
	google-deploy


app-up-local:
	. ./venv/bin/activate; \
	. secrets/set_env.sh; \
	. secrets/set_env_local.sh; \
	flask run


app-up-docker:
	. secrets/set_env.sh; \
	. secrets/set_env_local.sh; \
	docker build -t flashcards:1.0 ./ ;\
	docker run \
		-e PORT=5000 \
		-e GOOGLE_AUTH_URL=$$GOOGLE_AUTH_URL \
		-e GOOGLE_PROJECT_ID=$$GOOGLE_PROJECT_ID \
		-e GOOGLE_SERVICE_ACCOUNT_SECRETS=$$GOOGLE_SERVICE_ACCOUNT_SECRETS \
		-e GOOGLE_SERVICE_ACCOUNT=$$GOOGLE_SERVICE_ACCOUNT \
		-e GOOGLE_REGION=$$GOOGLE_REGION \
		-e GOOGLE_IMAGE=$$GOOGLE_IMAGE \
		-e GOOGLE_EMAIL=$$GOOGLE_EMAIL \
		-p 5000:5000 \
		--rm  \
		flashcards:1.0




google-build-deploy: google-build google-deploy

google-build:
	. secrets/set_env.sh ;\
	gcloud builds submit ./ --tag "$$GOOGLE_IMAGE"

google-deploy:
	. secrets/set_env.sh ;\
	gcloud run deploy flashcards \
		--image "$$GOOGLE_IMAGE" \
		--region="$$GOOGLE_REGION" \
		--platform managed \
		--allow-unauthenticated \
		--service-account="$$GOOGLE_SERVICE_ACCOUNT" \
		--update-env-vars GOOGLE_AUTH_URL=$$GOOGLE_AUTH_URL \
		--update-env-vars GOOGLE_PROJECT_ID=$$GOOGLE_PROJECT_ID \
		--update-env-vars GOOGLE_SERVICE_ACCOUNT_SECRETS=$$GOOGLE_SERVICE_ACCOUNT_SECRETS \
		--update-env-vars GOOGLE_SERVICE_ACCOUNT=$$GOOGLE_SERVICE_ACCOUNT \
		--update-env-vars GOOGLE_REGION=$$GOOGLE_REGION \
		--update-env-vars GOOGLE_IMAGE=$$GOOGLE_IMAGE \
		--update-env-vars GOOGLE_EMAIL=$$GOOGLE_EMAIL 




local-python-up: 
	. venv/bin/activate; \
	. secrets/set_env.sh; \
	. secrets/set_env_local.sh; \
	python

local-python-init:
	virtualenv venv

local-python-down:
	@echo "deactivate"
	