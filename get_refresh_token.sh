#!/bin/bash
#
# Script generates refresh token from Viessmann developer portal. It is used to authorize api requests to Viessmann api gateway.
# Before using - input two variables below.
# You will also have to use a browser during the whole procedure (just follow script guides)
#
# CLINET_ID - ID taken from Viessmann developer portal: https://developer.viessmann.com/
#             Register account and create client profile for Your Viessmann boiler - it will contain required ID. Copy it to CLIENT_ID variable.
# CODE_CHALLENGE - Go to: https://tonyxu-io.github.io/pkce-generator/
#                 Fill code verifier field. The Code Verifier is a random character string that can consist of the characters A-Z, a-z, 0-9 and punctuation marks -_.~ and must have a length of 43 to 128 characters. 
#                 Click "Generate Code Challenge" and copy result string to variable CODE_CHALLENGE.

CLIENT_ID=""
CODE_CHALLENGE=""

if [[ $CLIENT_ID = "" || $CODE_CHALLENGE = "" ]]; then
  echo "CLINET_ID and/or CODE_CHALLENGE variables are empty - please read manual inside script before using it."
  exit 1
fi

echo "Open in browser: https://iam.viessmann.com/idp/v2/authorize?client_id=9837aa5590238f2bac000c386f59a827&redirect_uri=http://localhost/&response_type=code&code_challenge=Ne_Jp3vBzm19cQ3Na9BtxcenbGhRZL0qAUP1jmNxC4g&scope=IoT%20User%20offline_access"
echo "Copy the code string from the response url"
echo -n "Input refresh code taken from the response url: "
read AUTH_REFRESH_CODE
echo "Requesting refresh token with auth refresh code: $AUTH_REFRESH_CODE ..."
curl -X POST "https://iam.viessmann.com/idp/v2/token" -H "Content-Type: application/x-www-form-urlencoded" -d "grant_type=authorization_code&client_id=${CLIENT_ID}&redirect_uri=http://localhost/&code_verifier=${CODE_CHALLENGE}&code=${AUTH_REFRESH_CODE}"
echo
echo "Copy refresh_token to config.cfg and remove token.json if thre is one"
