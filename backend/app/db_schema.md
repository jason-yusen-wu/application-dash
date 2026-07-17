CREATE TABLE users (
  user_id SERIAL PRIMARY KEY,
  google_sub VARCHAR(255) NOT NULL UNIQUE,
  user_refresh_token TEXT NOT NULL,
  last_history_id BIGINT
);

Google sub: unique identifier for google account used in OAuth 2.0
refresh_token: only issued on first grant 
last_history_id: used by GMail API, monotonically increasing
 - is nullable: a user that only performed OAuth will not have a valid last_history_id

CREATE TABLE application_status (
  status varchar(255) PRIMARY KEY,
  CONSTRAINT check_status CHECK (status IN ('submitted', 'OA', 'interview', 'offer', 'rejected'))
);

status: enum (not the SQL ENUM) representing an application's progress in the pipeline 

CREATE TABLE applications (
  app_id SERIAL PRIMARY KEY,
  user_id INT NOT NULL,
  CONSTRAINT fk_apps_users FOREIGN KEY (user_id) REFERENCES users(user_id),
  company_name varchar(255) NOT NULL,
  job_title varchar(255) NOT NULL,
  status VARCHAR(255) NOT NULL,
  CONSTRAINT check_status FOREIGN KEY (status) REFERENCES application_status(status),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL,
  applied_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX ix_applications_user_id ON applications(user_id);

user_id: indexed for faster lookup ("give me all applications of this user")
created_at: time at which **record** was created (for debug and audit)
updated_at: time of most recent status update (i.e. latest application event)
applied_at: time at which application confirmation was received (i.e. earliest application event)


CREATE TABLE application_events (
  event_id SERIAL PRIMARY KEY,
  application_id INT NOT NULL REFERENCES applications(app_id),
  gmail_message_id VARCHAR(255) NOT NULL UNIQUE,
  inferred_status varchar(255) NOT NULL,
  CONSTRAINT status_is_enum FOREIGN KEY (inferred_status) REFERENCES application_status(status),
  received_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

gmail_message_id: technically can serve as primary key but `event_id` is smaller 
inferred_status: LLM's structured decoding generated from email input
received_at: the actual timestamp on the physical email itself
created_at: time at record creation

