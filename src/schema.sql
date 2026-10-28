CREATE DATABASE IF NOT EXISTS aicoaching
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE aicoaching;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS meeting_notes;
DROP TABLE IF EXISTS activities;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS candidates;
DROP TABLE IF EXISTS coaches;
DROP TABLE IF EXISTS excel_coach_notes;
DROP TABLE IF EXISTS excel_courses_events;
DROP TABLE IF EXISTS excel_coach_meetings;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE coaches (
  coach_id VARCHAR(64) NOT NULL PRIMARY KEY,
  coach_name VARCHAR(255) NOT NULL,
  region VARCHAR(128) NOT NULL DEFAULT 'Unknown',
  working_hours_per_week DECIMAL(8,2) NOT NULL DEFAULT 37.00,
  working_days VARCHAR(64) NOT NULL,
  timezone VARCHAR(64) NOT NULL DEFAULT 'Europe/London'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE candidates (
  candidate_id VARCHAR(64) NOT NULL PRIMARY KEY,
  candidate_name VARCHAR(255) NOT NULL,
  programme VARCHAR(255) NOT NULL,
  status VARCHAR(64) NOT NULL,
  assigned_coach_id VARCHAR(64) NOT NULL,
  CONSTRAINT fk_candidates_coach FOREIGN KEY (assigned_coach_id) REFERENCES coaches (coach_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE bookings (
  booking_id VARCHAR(64) NOT NULL PRIMARY KEY,
  coach_id VARCHAR(64) NOT NULL,
  candidate_id VARCHAR(64) NOT NULL,
  session_date DATE NOT NULL,
  start_time VARCHAR(8) NOT NULL,
  end_time VARCHAR(8) NOT NULL,
  duration_minutes INT NOT NULL,
  status VARCHAR(32) NOT NULL,
  created_date DATE NULL,
  CONSTRAINT fk_bookings_coach FOREIGN KEY (coach_id) REFERENCES coaches (coach_id),
  CONSTRAINT fk_bookings_candidate FOREIGN KEY (candidate_id) REFERENCES candidates (candidate_id),
  INDEX idx_bookings_coach_date (coach_id, session_date),
  INDEX idx_bookings_date (session_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE activities (
  activity_id VARCHAR(64) NOT NULL PRIMARY KEY,
  candidate_id VARCHAR(64) NOT NULL,
  activity_name VARCHAR(512) NOT NULL,
  activity_type VARCHAR(64) NOT NULL,
  scheduled_date DATE NULL,
  completion_date DATE NULL,
  status VARCHAR(32) NOT NULL,
  duration_minutes INT NULL,
  CONSTRAINT fk_activities_candidate FOREIGN KEY (candidate_id) REFERENCES candidates (candidate_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE meeting_notes (
  meeting_id VARCHAR(64) NOT NULL PRIMARY KEY,
  coach_id VARCHAR(64) NULL,
  candidate_id VARCHAR(64) NOT NULL,
  meeting_date DATE NOT NULL,
  booking_id VARCHAR(64) NULL,
  notes TEXT,
  agreed_actions TEXT,
  CONSTRAINT fk_notes_candidate FOREIGN KEY (candidate_id) REFERENCES candidates (candidate_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
