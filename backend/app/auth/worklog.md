
# error handling

here are what i think are the most probable errors, weighted by their costliness.

1. the user does not consent when prompted by google auth servers during OAuth2 flow
> Handling: do not proceed with obtaining token, report auth error and redirect client back to auth step.

2. the user's refresh token is expired or invalid (learned only when making a GMail API call with it in a background sync job) caused by expiration or user revoking app access
handling: detect and record failure on User row of db, next time user browser opens our dashboard, prompt for reauth
- Don't ON DELETE CASCADE on revoking access (no way to tell)! defer to actual "delete my data" button

# api error handling

as described in 
https://developers.google.com/workspace/gmail/api/guides/handle-errors

1. 400 bad request 
> Handling: invalid/expire `PageToken`, should obtain new page token with new request (message_id prevents re-processing)

2. 401 unauthorized
> Handling: edge case where access token dies before expiry (it gets automatically renewed on expiry), requires manual refresh. If manual refresh also fails (refresh token expired/invalid), reroute to the same handler for reauth prompting.

3. 403 forbidden 
> Handling: cause is either exceeding usage limit or wrong privileges. If the user's workspace blocked third-party app access, report error to user and signal that there's Nothing we can do.
`dailyLimitExceeded`: report error, tell user to retry tomorrow.

4. 404 not found: message no longer exists
> Handling: rest of message batch should still be processed 

5. 429 too many requests
> Handling: exponential backoff (with max retry attempts, skew batch requests with jitter)

6. 500/502/503/504 errors 
> Handling: retry with exponential backoff (max retry attempts, skew batch with jitter)



