#!/bin/bash
set -e

echo
echo "Setting up Dev Env..."
if [ -d venv ]; then
    echo '-> Using existing virtualenv'
elif [ `whereis -bq python3.8` ]; then
    virtualenv -p python3.8 venv
elif [ `whereis -bq python3.9` ]; then
    virtualenv -p python3.9 venv
else
    echo 'No Python 3.8 or 3.9 found - aborting'  >> /dev/stderr
    exit 1
fi
source venv/bin/activate

if [ ! -f .env ]; then
    echo
    echo "Setup env variables..."
    echo
    echo "Create a OpenAI token at https://platform.openai.com/account/api-keys"
    read -p "OpenAI token: " OPENAI_API_KEY

    echo
    echo "Create a Pinecode token (https://app.pinecone.io), but make sure the environment is 'us-west1-gcp'"
    read -p "Pinecode API key: " PINECONE_TOKEN


    cat << EOT > .env
OPENAI_API_KEY=$OPENAI_API_KEY
PINECONE_API_KEY=$PINECONE_TOKEN
EOT
    echo "-> Tokens written to ./.env"
fi

echo
echo "Run 'source venv/bin/activate' to use the virtualenv"
