
export FLASK_APP=app.py


export LOCAL_GOOGLE_AUTH_URL="$(\
    jq '.GOOGLE_AUTH_URL' ./secrets/secrets_local.json\
)";


export SECRETS="$(\
    jq ".GOOGLE_AUTH_URL=$LOCAL_GOOGLE_AUTH_URL" ./secrets/secrets_global.json | \
    base64  \
);"



