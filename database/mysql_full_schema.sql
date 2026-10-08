-- Full MySQL 8 schema reference for Sprint 1 + Sprint 2
CREATE DATABASE IF NOT EXISTS he_thong_dao_tao CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE he_thong_dao_tao;
SET default_storage_engine=InnoDB;

-- Khuyến nghị triển khai thực tế: dùng Alembic `alembic upgrade head`.

CREATE TABLE permissions (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	code VARCHAR(100) NOT NULL, 
	name VARCHAR(150) NOT NULL, 
	description VARCHAR(255), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_permissions_code UNIQUE (code)
);
CREATE INDEX ix_permissions_code ON permissions (code);

CREATE TABLE roles (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	slug VARCHAR(50) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description VARCHAR(255), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_roles_slug UNIQUE (slug)
);
CREATE INDEX ix_roles_slug ON roles (slug);

CREATE TABLE subjects (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	code VARCHAR(50) NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	session_count INTEGER NOT NULL, 
	weight INTEGER NOT NULL, 
	description TEXT, 
	learning_outcomes TEXT, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_subjects_code ON subjects (code);

CREATE TABLE training_programs (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	code VARCHAR(50) NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	description TEXT, 
	total_duration_hours INTEGER NOT NULL, 
	standard_tuition NUMERIC(14, 2) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_training_programs_code ON training_programs (code);
CREATE INDEX ix_training_programs_status ON training_programs (status);

CREATE TABLE users (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	full_name VARCHAR(150) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	phone VARCHAR(30), 
	date_of_birth DATE, 
	address VARCHAR(500), 
	avatar_path VARCHAR(500), 
	avatar_thumbnail_path VARCHAR(500), 
	password_hash VARCHAR(255) NOT NULL, 
	`role` VARCHAR(50) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	is_active BOOL NOT NULL, 
	must_change_password BOOL NOT NULL, 
	needs_handover BOOL NOT NULL, 
	failed_login_attempts INTEGER NOT NULL, 
	locked_until DATETIME, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE INDEX ix_users_id ON users (id);
CREATE INDEX ix_users_phone ON users (phone);
CREATE INDEX ix_users_status ON users (status);

CREATE TABLE account_lock_audits (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER NOT NULL, 
	actor_user_id INTEGER, 
	action VARCHAR(20) NOT NULL, 
	reason TEXT NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(actor_user_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX ix_account_lock_audits_user_id ON account_lock_audits (user_id);

CREATE TABLE activation_tokens (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER NOT NULL, 
	token_hash VARCHAR(64) NOT NULL, 
	expires_at DATETIME NOT NULL, 
	used_at DATETIME, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX ix_activation_tokens_expires_at ON activation_tokens (expires_at);
CREATE UNIQUE INDEX ix_activation_tokens_token_hash ON activation_tokens (token_hash);
CREATE INDEX ix_activation_tokens_user_id ON activation_tokens (user_id);

CREATE TABLE auth_sessions (
	id VARCHAR(36) NOT NULL, 
	user_id INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	last_activity_at DATETIME NOT NULL, 
	expires_at DATETIME NOT NULL, 
	revoked_at DATETIME, 
	user_agent VARCHAR(255), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX ix_auth_sessions_expires_at ON auth_sessions (expires_at);
CREATE INDEX ix_auth_sessions_revoked_at ON auth_sessions (revoked_at);
CREATE INDEX ix_auth_sessions_user_id ON auth_sessions (user_id);

CREATE TABLE leads (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	full_name VARCHAR(150) NOT NULL, 
	phone VARCHAR(30) NOT NULL, 
	email VARCHAR(255), 
	source VARCHAR(100), 
	interested_program_id INTEGER, 
	status VARCHAR(30) NOT NULL, 
	assignee_user_id INTEGER, 
	note TEXT, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(interested_program_id) REFERENCES training_programs (id) ON DELETE SET NULL, 
	FOREIGN KEY(assignee_user_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX ix_leads_assignee_user_id ON leads (assignee_user_id);
CREATE INDEX ix_leads_created_at ON leads (created_at);
CREATE INDEX ix_leads_full_name ON leads (full_name);
CREATE INDEX ix_leads_phone ON leads (phone);
CREATE INDEX ix_leads_source ON leads (source);
CREATE INDEX ix_leads_status ON leads (status);

CREATE TABLE password_reset_tokens (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER NOT NULL, 
	token_hash VARCHAR(64) NOT NULL, 
	expires_at DATETIME NOT NULL, 
	used_at DATETIME, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX ix_password_reset_tokens_expires_at ON password_reset_tokens (expires_at);
CREATE UNIQUE INDEX ix_password_reset_tokens_token_hash ON password_reset_tokens (token_hash);
CREATE INDEX ix_password_reset_tokens_user_id ON password_reset_tokens (user_id);

CREATE TABLE program_subjects (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	program_id INTEGER NOT NULL, 
	subject_id INTEGER NOT NULL, 
	order_index INTEGER NOT NULL, 
	prerequisite_subject_id INTEGER, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_program_subject UNIQUE (program_id, subject_id), 
	CONSTRAINT uq_program_subject_order UNIQUE (program_id, order_index), 
	FOREIGN KEY(program_id) REFERENCES training_programs (id) ON DELETE CASCADE, 
	FOREIGN KEY(subject_id) REFERENCES subjects (id) ON DELETE RESTRICT, 
	FOREIGN KEY(prerequisite_subject_id) REFERENCES subjects (id) ON DELETE SET NULL
);
CREATE INDEX ix_program_subjects_program_id ON program_subjects (program_id);
CREATE INDEX ix_program_subjects_subject_id ON program_subjects (subject_id);

CREATE TABLE role_permissions (
	role_id INTEGER NOT NULL, 
	permission_id INTEGER NOT NULL, 
	PRIMARY KEY (role_id, permission_id), 
	FOREIGN KEY(role_id) REFERENCES roles (id) ON DELETE CASCADE, 
	FOREIGN KEY(permission_id) REFERENCES permissions (id) ON DELETE CASCADE
);

CREATE TABLE subject_sessions (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	subject_id INTEGER NOT NULL, 
	sequence INTEGER NOT NULL, 
	topic VARCHAR(255) NOT NULL, 
	objective TEXT, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_subject_session_sequence UNIQUE (subject_id, sequence), 
	FOREIGN KEY(subject_id) REFERENCES subjects (id) ON DELETE CASCADE
);
CREATE INDEX ix_subject_sessions_subject_id ON subject_sessions (subject_id);

CREATE TABLE training_classes (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	program_id INTEGER NOT NULL, 
	name VARCHAR(150) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(program_id) REFERENCES training_programs (id) ON DELETE RESTRICT
);
CREATE INDEX ix_training_classes_program_id ON training_classes (program_id);
CREATE INDEX ix_training_classes_status ON training_classes (status);

CREATE TABLE user_roles (
	user_id INTEGER NOT NULL, 
	role_id INTEGER NOT NULL, 
	PRIMARY KEY (user_id, role_id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(role_id) REFERENCES roles (id) ON DELETE CASCADE
);

CREATE TABLE lead_assignment_history (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	lead_id INTEGER NOT NULL, 
	from_user_id INTEGER, 
	to_user_id INTEGER, 
	actor_user_id INTEGER, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(lead_id) REFERENCES leads (id) ON DELETE CASCADE, 
	FOREIGN KEY(from_user_id) REFERENCES users (id) ON DELETE SET NULL, 
	FOREIGN KEY(to_user_id) REFERENCES users (id) ON DELETE SET NULL, 
	FOREIGN KEY(actor_user_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX ix_lead_assignment_history_lead_id ON lead_assignment_history (lead_id);
