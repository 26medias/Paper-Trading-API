#!/bin/bash

# Parse the arguments
while [ $# -gt 0 ]; do
    key="$1"
    case $key in
        -env|--env)
            env="$2"
            shift # past argument
            shift # past value
            ;;
        -app|--app)
            app="$2"
            shift # past argument
            shift # past value
            ;;
        *)    # unknown option
            POSITIONAL+=("$1") # save it in an array for later
            shift # past argument
            ;;
    esac
done

# If arguments are not passed using flags (-env, -app), assume they are positional
if [ -z $env ] && [ -z $app ]; then
    env=${POSITIONAL[0]}
    app=${POSITIONAL[1]}
fi

# Set env vars
export REACT_APP_API_ENDPOINT=$(eval echo \$API_ENDPOINT_$env)
export APP_ENV=$env

# Handle the app argument
case $app in
    # Check the env vars
    'test')
        (
        #cd server/api
        #node test
        echo REACT_APP_API_ENDPOINT $REACT_APP_API_ENDPOINT
        echo APP_ENV $APP_ENV
        )
        ;;
    # Start the React Website
    'react')
        (
        cd client/website
        npm start
        )
        ;;
    # Build the react website
    'react:build')
        (
        cd client/website
        npm run build
        )
        ;;


    
    # Start the Typescript API
    'api:run')
        (
        cd server/api
        npm run test
        )
        ;;
    # Deploy the API on GCF
    'api:deploy:gcf')
        (
        cd server/api
        tsc
        mv dist js
        cp package.json js/package.json
        cp -r prompts js
        cd js
        gcloud functions deploy deepd-api --entry-point main --memory 1024MB --runtime nodejs18 --region us-east1 --project qs-trading --trigger-http --quiet --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY,SUPABASE_SERVICE_ROLE_AUTH=$SUPABASE_SERVICE_ROLE_AUTH,SUPABASE_PID=$SUPABASE_PID,SUPABASE_SERVICE_ROLE=$SUPABASE_SERVICE_ROLE,DB_STRING=$DB_STRING,APP_ENV=$APP_ENV
        cd ..
        #npm run clean
        )
        ;;

    *)
        echo "Invalid app argument, got '$app'"
        exit 1
esac
