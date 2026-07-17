I want to build a dashboard that handles job application status emails, organizes and displays them so applicants can focus on applying rather than spreadsheet managing.

Here is my sketch plan, which you should critique as necessary for me to learn.
1. We need the Gmail API so we can access an applicant's emails
2. We read all the emails, ignore the non-job application ones. I would like to cache previously read emails so we don't repeat any work. I think we can keep a hash of the emails and maybe schedule work like a cron job (to be run daily?) or epoll on every new email?
3. For the job application ones, we feed the email title and body content to an LLM to cheaply and efficiently infer (1. the company being applied to, and 2. the status of the application). 
4. The LLM's output should be saved to the corresponding user's database table. 
5. A dashboard can then fetch the data from the user's database table.

This is a MVP.

Addendums:
1. users first perform OAuth2 with Google so we can obtain .readonly restricted access, encrypt user refresh tokens
2. filter at the API level for keywords (how do we make sure no application email slips by the filter?) called on new messages from last sync with History API
3. opt for cheap regex heuristics, survivors are cleaned and then fed to LLM
Question: why do we use cheap heuristics? how does this help us reduce email volume? Why do we need structured output for the LLM?
4. The email output is first matched against existing applications, then update the state machine associated with the application.
5. Use user_id for multi-tenant tables 
6. allow for user corrections and use them to improve future accuracy.
Question: why does the dashboard need an auth?
