I provide here my database schema in the form of raw SQL DDL. These are annotated with my own reasoning

CREATE TABLE users {
  user_id SERIAL PRIMARY KEY,
  user_email varchar(255) NOT NULL UNIQUE,
  user_refresh_token TEXT NOT NULL, 
}

CREATE TABLE applications {
  app_id SERIAL PRIMARY KEY,
  CONSTRAINT fk_apps_users FOREIGN KEY (user_id) REFERENCES users(user_id),
  company_name varchar(255),
  job_title varchar(255),
  date DATE,
  status int
}

CREATE TABLE application_events {
  event_id SERIAL PRIMARY KEY,
  application_id INT NOT NULL REFERENCES applications(app_id),
  gmail_message_id VARCHAR(255) NOT NULL UNIQUE,
  inferred_status status_enum NOT NULL,
  received_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
}

My understanding:
 - `application_events.gmail_message_id` is unique, which achieves dedup
 - the `received_at` and `created_at` record fields are how we perform incremental sync
 - 


