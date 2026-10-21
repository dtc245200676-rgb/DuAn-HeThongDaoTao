-- Full MySQL 8 schema and test seed for Sprint 1–4
CREATE DATABASE IF NOT EXISTS he_thong_dao_tao_sprint4_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE he_thong_dao_tao_sprint4_test;
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

-- Base schema is revision 20261006_0002; updated to Sprint 3 revision at the end.
CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY);
INSERT INTO alembic_version(version_num) VALUES ('20261006_0002');

-- Seed permissions
INSERT INTO permissions(code,name,description) VALUES ('dashboard.view','Xem trang tổng quan',NULL);
INSERT INTO permissions(code,name,description) VALUES ('users.view','Xem danh sách người dùng',NULL);
INSERT INTO permissions(code,name,description) VALUES ('users.create','Tạo tài khoản người dùng',NULL);
INSERT INTO permissions(code,name,description) VALUES ('users.update','Sửa thông tin người dùng',NULL);
INSERT INTO permissions(code,name,description) VALUES ('users.lock','Khóa/mở khóa tài khoản',NULL);
INSERT INTO permissions(code,name,description) VALUES ('roles.view','Xem vai trò và quyền',NULL);
INSERT INTO permissions(code,name,description) VALUES ('roles.manage','Cấu hình quyền theo vai trò',NULL);
INSERT INTO permissions(code,name,description) VALUES ('roles.assign','Gán/thu hồi vai trò',NULL);
INSERT INTO permissions(code,name,description) VALUES ('training.view','Xem dữ liệu đào tạo',NULL);
INSERT INTO permissions(code,name,description) VALUES ('training.edit','Cập nhật dữ liệu đào tạo',NULL);
INSERT INTO permissions(code,name,description) VALUES ('grades.view','Xem điểm',NULL);
INSERT INTO permissions(code,name,description) VALUES ('grades.edit','Sửa điểm',NULL);
INSERT INTO permissions(code,name,description) VALUES ('tuition.view','Xem học phí',NULL);
INSERT INTO permissions(code,name,description) VALUES ('tuition.edit','Sửa học phí',NULL);
INSERT INTO permissions(code,name,description) VALUES ('profile.edit','Cập nhật hồ sơ cá nhân',NULL);
INSERT INTO permissions(code,name,description) VALUES ('users.import','Nhập danh sách người dùng từ Excel',NULL);
INSERT INTO permissions(code,name,description) VALUES ('leads.view','Xem danh sách lead tuyển sinh',NULL);
INSERT INTO permissions(code,name,description) VALUES ('leads.edit','Tạo và cập nhật lead tuyển sinh',NULL);
INSERT INTO permissions(code,name,description) VALUES ('leads.assign','Phân công lead tuyển sinh',NULL);

-- Seed roles
INSERT INTO roles(slug,name,description) VALUES ('system_admin','Quản trị hệ thống','Quản trị tài khoản, vai trò và toàn bộ cấu hình hệ thống.');
INSERT INTO roles(slug,name,description) VALUES ('training_manager','Quản lý đào tạo','Quản lý hoạt động đào tạo, lớp học và nghiệp vụ học vụ.');
INSERT INTO roles(slug,name,description) VALUES ('teacher','Giảng viên','Giảng dạy, theo dõi lớp và nhập điểm; không sửa học phí.');
INSERT INTO roles(slug,name,description) VALUES ('accountant','Kế toán','Quản lý học phí; không sửa điểm.');
INSERT INTO roles(slug,name,description) VALUES ('academic_affairs','Giáo vụ','Hỗ trợ vận hành đào tạo và hồ sơ học vụ.');
INSERT INTO roles(slug,name,description) VALUES ('admissions','Tuyển sinh','Theo dõi và hỗ trợ hồ sơ đầu vào.');
INSERT INTO roles(slug,name,description) VALUES ('student_services','Công tác sinh viên','Hỗ trợ người học trong quá trình học tập.');
INSERT INTO roles(slug,name,description) VALUES ('student','Học viên','Xem thông tin học tập, điểm và học phí của bản thân.');

-- Seed role-permission mappings
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='system_admin' AND p.code='dashboard.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='system_admin' AND p.code='users.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='system_admin' AND p.code='users.create';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='system_admin' AND p.code='users.update';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='system_admin' AND p.code='users.lock';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='system_admin' AND p.code='roles.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='system_admin' AND p.code='roles.manage';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='system_admin' AND p.code='roles.assign';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='system_admin' AND p.code='training.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='system_admin' AND p.code='training.edit';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='system_admin' AND p.code='grades.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='system_admin' AND p.code='grades.edit';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='system_admin' AND p.code='tuition.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='system_admin' AND p.code='tuition.edit';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='system_admin' AND p.code='profile.edit';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='system_admin' AND p.code='users.import';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='system_admin' AND p.code='leads.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='system_admin' AND p.code='leads.edit';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='system_admin' AND p.code='leads.assign';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='training_manager' AND p.code='dashboard.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='training_manager' AND p.code='users.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='training_manager' AND p.code='training.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='training_manager' AND p.code='training.edit';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='training_manager' AND p.code='grades.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='training_manager' AND p.code='grades.edit';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='training_manager' AND p.code='tuition.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='training_manager' AND p.code='profile.edit';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='training_manager' AND p.code='leads.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='training_manager' AND p.code='leads.edit';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='training_manager' AND p.code='leads.assign';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='teacher' AND p.code='dashboard.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='teacher' AND p.code='training.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='teacher' AND p.code='grades.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='teacher' AND p.code='grades.edit';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='teacher' AND p.code='tuition.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='accountant' AND p.code='dashboard.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='accountant' AND p.code='users.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='accountant' AND p.code='tuition.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='accountant' AND p.code='tuition.edit';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='accountant' AND p.code='grades.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='academic_affairs' AND p.code='dashboard.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='academic_affairs' AND p.code='users.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='academic_affairs' AND p.code='training.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='academic_affairs' AND p.code='training.edit';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='academic_affairs' AND p.code='grades.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='admissions' AND p.code='dashboard.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='admissions' AND p.code='users.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='admissions' AND p.code='training.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='admissions' AND p.code='profile.edit';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='admissions' AND p.code='leads.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='admissions' AND p.code='leads.edit';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='student_services' AND p.code='dashboard.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='student_services' AND p.code='users.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='student_services' AND p.code='training.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='student_services' AND p.code='grades.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='student' AND p.code='dashboard.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='student' AND p.code='training.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='student' AND p.code='grades.view';
INSERT INTO role_permissions(role_id,permission_id) SELECT r.id,p.id FROM roles r, permissions p WHERE r.slug='student' AND p.code='tuition.view';

-- Test accounts
INSERT INTO users(full_name,email,phone,date_of_birth,address,avatar_path,avatar_thumbnail_path,password_hash,`role`,status,is_active,must_change_password,needs_handover,failed_login_attempts,locked_until,created_at,updated_at) VALUES ('Quản trị viên','admin@gmail.com',NULL,NULL,NULL,NULL,NULL,'$pbkdf2$rqBJF36lpwXy+d6vh04TBfgzkgi5N0wScjewPPAAzl29igaN6ntA56iHtnbuimFl','system_admin','active',1,0,0,0,NULL,NOW(),NOW());
INSERT INTO user_roles(user_id,role_id) SELECT u.id,r.id FROM users u, roles r WHERE u.email='admin@gmail.com' AND r.slug='system_admin';
INSERT INTO users(full_name,email,phone,date_of_birth,address,avatar_path,avatar_thumbnail_path,password_hash,`role`,status,is_active,must_change_password,needs_handover,failed_login_attempts,locked_until,created_at,updated_at) VALUES ('Quản lý đào tạo','manager@gmail.com',NULL,NULL,NULL,NULL,NULL,'$pbkdf2$Tr4Q2cHnShIa+2CfAVaRRd2ezBJaMrGmO4K8KDUXCY6LmgxGjXUiXczi20h5xQdc','training_manager','active',1,0,0,0,NULL,NOW(),NOW());
INSERT INTO user_roles(user_id,role_id) SELECT u.id,r.id FROM users u, roles r WHERE u.email='manager@gmail.com' AND r.slug='training_manager';
INSERT INTO users(full_name,email,phone,date_of_birth,address,avatar_path,avatar_thumbnail_path,password_hash,`role`,status,is_active,must_change_password,needs_handover,failed_login_attempts,locked_until,created_at,updated_at) VALUES ('Nhân viên tuyển sinh','admissions@gmail.com',NULL,NULL,NULL,NULL,NULL,'$pbkdf2$gZromPrWWazSRBfm+ptWyuUIHBZrKF1YeP2aasEayy/72EPXSCUomXob1xO8Dpt8','admissions','active',1,0,0,0,NULL,NOW(),NOW());
INSERT INTO user_roles(user_id,role_id) SELECT u.id,r.id FROM users u, roles r WHERE u.email='admissions@gmail.com' AND r.slug='admissions';

-- Sample Sprint 2 training data
INSERT INTO training_programs(code,name,description,total_duration_hours,standard_tuition,status,created_at,updated_at) VALUES ('FS01','Fullstack Developer','Dữ liệu mẫu để test Sprint 2',600,30000000,'active',NOW(),NOW());
INSERT INTO subjects(code,name,session_count,weight,description,learning_outcomes,created_at,updated_at) VALUES ('HTML01','HTML & CSS',10,30,'Nền tảng giao diện','Xây dựng giao diện web cơ bản',NOW(),NOW());
INSERT INTO subjects(code,name,session_count,weight,description,learning_outcomes,created_at,updated_at) VALUES ('JS01','JavaScript',12,40,'JavaScript căn bản','Lập trình JavaScript',NOW(),NOW());
INSERT INTO subjects(code,name,session_count,weight,description,learning_outcomes,created_at,updated_at) VALUES ('REACT01','React',10,30,'React căn bản','Xây dựng SPA bằng React',NOW(),NOW());
INSERT INTO program_subjects(program_id,subject_id,order_index,prerequisite_subject_id) SELECT p.id,s.id,1,NULL FROM training_programs p,subjects s WHERE p.code='FS01' AND s.code='HTML01';
INSERT INTO program_subjects(program_id,subject_id,order_index,prerequisite_subject_id) SELECT p.id,s.id,2,pre.id FROM training_programs p,subjects s,subjects pre WHERE p.code='FS01' AND s.code='JS01' AND pre.code='HTML01';
INSERT INTO program_subjects(program_id,subject_id,order_index,prerequisite_subject_id) SELECT p.id,s.id,3,pre.id FROM training_programs p,subjects s,subjects pre WHERE p.code='FS01' AND s.code='REACT01' AND pre.code='JS01';
INSERT INTO subject_sessions(subject_id,sequence,topic,objective) SELECT id,1,'HTML cơ bản','Hiểu cấu trúc HTML' FROM subjects WHERE code='HTML01';
INSERT INTO subject_sessions(subject_id,sequence,topic,objective) SELECT id,2,'CSS cơ bản','Biết cách định dạng giao diện' FROM subjects WHERE code='HTML01';
INSERT INTO training_classes(program_id,name,status) SELECT id,'FS01 Demo','planned' FROM training_programs WHERE code='FS01';

-- Sample leads
INSERT INTO leads(full_name,phone,email,source,interested_program_id,status,assignee_user_id,note,created_at,updated_at) SELECT 'Nguyễn Văn Lead','0901234567','lead1@example.com','website',p.id,'new',u.id,'Lead mẫu Sprint 2',NOW(),NOW() FROM training_programs p,users u WHERE p.code='FS01' AND u.email='admissions@gmail.com';
INSERT INTO leads(full_name,phone,email,source,interested_program_id,status,assignee_user_id,note,created_at,updated_at) SELECT 'Trần Thị Lead','0912345678','lead2@example.com','facebook',p.id,'contacted',u.id,'Lead mẫu thứ hai',NOW(),NOW() FROM training_programs p,users u WHERE p.code='FS01' AND u.email='admissions@gmail.com';
INSERT INTO lead_assignment_history(lead_id,from_user_id,to_user_id,actor_user_id,created_at) SELECT l.id,NULL,a.id,m.id,NOW() FROM leads l,users a,users m WHERE l.phone='0901234567' AND a.email='admissions@gmail.com' AND m.email='manager@gmail.com';

-- End of Sprint 2 test database


-- ==============================
-- Sprint 3 schema (migration 20261013_0003)
-- This file targets a new, isolated test database. It does not drop any database.
-- ==============================

CREATE TABLE lead_status_history (
  id INT NOT NULL AUTO_INCREMENT,
  lead_id INT NOT NULL,
  from_status VARCHAR(30) NULL,
  to_status VARCHAR(30) NOT NULL,
  reason VARCHAR(255) NULL,
  actor_user_id INT NULL,
  changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_lead_status_history_lead_id FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE,
  CONSTRAINT fk_lead_status_history_actor_user_id FOREIGN KEY (actor_user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;
CREATE INDEX ix_lead_status_history_lead_id ON lead_status_history (lead_id);
CREATE INDEX ix_lead_status_history_to_status ON lead_status_history (to_status);
CREATE INDEX ix_lead_status_history_changed_at ON lead_status_history (changed_at);

CREATE TABLE lead_interactions (
  id INT NOT NULL AUTO_INCREMENT,
  lead_id INT NOT NULL,
  interaction_type VARCHAR(20) NOT NULL,
  content TEXT NOT NULL,
  occurred_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  reminder_at DATETIME NULL,
  reminder_completed_at DATETIME NULL,
  created_by_user_id INT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_lead_interactions_lead_id FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE,
  CONSTRAINT fk_lead_interactions_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;
CREATE INDEX ix_lead_interactions_lead_id ON lead_interactions (lead_id);
CREATE INDEX ix_lead_interactions_occurred_at ON lead_interactions (occurred_at);
CREATE INDEX ix_lead_interactions_reminder_at ON lead_interactions (reminder_at);

CREATE TABLE student_profiles (
  id INT NOT NULL AUTO_INCREMENT,
  student_code VARCHAR(30) NOT NULL,
  user_id INT NOT NULL,
  source_lead_id INT NULL,
  entry_level VARCHAR(255) NULL,
  notes TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT uq_student_profiles_student_code UNIQUE (student_code),
  CONSTRAINT uq_student_profiles_user_id UNIQUE (user_id),
  CONSTRAINT uq_student_profiles_source_lead_id UNIQUE (source_lead_id),
  CONSTRAINT fk_student_profiles_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
  CONSTRAINT fk_student_profiles_source_lead_id FOREIGN KEY (source_lead_id) REFERENCES leads(id) ON DELETE SET NULL
) ENGINE=InnoDB;
CREATE UNIQUE INDEX ix_student_profiles_student_code ON student_profiles (student_code);
CREATE UNIQUE INDEX ix_student_profiles_user_id ON student_profiles (user_id);

CREATE TABLE training_rooms (
  id INT NOT NULL AUTO_INCREMENT,
  code VARCHAR(50) NOT NULL,
  name VARCHAR(150) NOT NULL,
  room_type VARCHAR(20) NOT NULL DEFAULT 'physical',
  capacity INT NULL,
  online_url VARCHAR(500) NULL,
  is_active BOOL NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT uq_training_rooms_code UNIQUE (code)
) ENGINE=InnoDB;
CREATE UNIQUE INDEX ix_training_rooms_code ON training_rooms (code);
CREATE INDEX ix_training_rooms_room_type ON training_rooms (room_type);
CREATE INDEX ix_training_rooms_is_active ON training_rooms (is_active);

ALTER TABLE training_classes
  ADD COLUMN code VARCHAR(50) NULL,
  ADD COLUMN expected_start_date DATE NULL,
  ADD COLUMN max_students INT NOT NULL DEFAULT 30,
  ADD COLUMN delivery_mode VARCHAR(20) NOT NULL DEFAULT 'offline',
  ADD COLUMN room_id INT NULL,
  ADD COLUMN completed_sessions INT NOT NULL DEFAULT 0,
  ADD COLUMN created_by_user_id INT NULL,
  ADD COLUMN created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ADD COLUMN updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;
UPDATE training_classes SET code = CONCAT('LEGACY-', id) WHERE code IS NULL OR code = '';
CREATE UNIQUE INDEX ix_training_classes_code ON training_classes (code);
CREATE INDEX ix_training_classes_expected_start_date ON training_classes (expected_start_date);
CREATE INDEX ix_training_classes_room_id ON training_classes (room_id);
ALTER TABLE training_classes
  ADD CONSTRAINT fk_training_classes_room_id FOREIGN KEY (room_id) REFERENCES training_rooms(id) ON DELETE SET NULL,
  ADD CONSTRAINT fk_training_classes_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE SET NULL;

CREATE TABLE class_subjects (
  id INT NOT NULL AUTO_INCREMENT,
  class_id INT NOT NULL,
  subject_id INT NOT NULL,
  order_index INT NOT NULL,
  prerequisite_subject_id INT NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_class_subject UNIQUE (class_id, subject_id),
  CONSTRAINT uq_class_subject_order UNIQUE (class_id, order_index),
  CONSTRAINT fk_class_subjects_class_id FOREIGN KEY (class_id) REFERENCES training_classes(id) ON DELETE CASCADE,
  CONSTRAINT fk_class_subjects_subject_id FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE RESTRICT,
  CONSTRAINT fk_class_subjects_prerequisite_subject_id FOREIGN KEY (prerequisite_subject_id) REFERENCES subjects(id) ON DELETE SET NULL
) ENGINE=InnoDB;
CREATE INDEX ix_class_subjects_class_id ON class_subjects (class_id);
CREATE INDEX ix_class_subjects_subject_id ON class_subjects (subject_id);

CREATE TABLE class_enrollments (
  id INT NOT NULL AUTO_INCREMENT,
  class_id INT NOT NULL,
  student_id INT NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'active',
  enrolled_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  enrolled_by_user_id INT NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_class_enrollment UNIQUE (class_id, student_id),
  CONSTRAINT fk_class_enrollments_class_id FOREIGN KEY (class_id) REFERENCES training_classes(id) ON DELETE CASCADE,
  CONSTRAINT fk_class_enrollments_student_id FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
  CONSTRAINT fk_class_enrollments_enrolled_by_user_id FOREIGN KEY (enrolled_by_user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;
CREATE INDEX ix_class_enrollments_class_id ON class_enrollments (class_id);
CREATE INDEX ix_class_enrollments_student_id ON class_enrollments (student_id);
CREATE INDEX ix_class_enrollments_status ON class_enrollments (status);

CREATE TABLE class_subject_staff (
  id INT NOT NULL AUTO_INCREMENT,
  class_subject_id INT NOT NULL,
  user_id INT NOT NULL,
  staff_role VARCHAR(20) NOT NULL,
  assigned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  assigned_by_user_id INT NULL,
  PRIMARY KEY (id),
  CONSTRAINT uq_class_subject_staff UNIQUE (class_subject_id, user_id, staff_role),
  CONSTRAINT fk_class_subject_staff_class_subject_id FOREIGN KEY (class_subject_id) REFERENCES class_subjects(id) ON DELETE CASCADE,
  CONSTRAINT fk_class_subject_staff_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_class_subject_staff_assigned_by_user_id FOREIGN KEY (assigned_by_user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;
CREATE INDEX ix_class_subject_staff_class_subject_id ON class_subject_staff (class_subject_id);
CREATE INDEX ix_class_subject_staff_user_id ON class_subject_staff (user_id);
CREATE INDEX ix_class_subject_staff_staff_role ON class_subject_staff (staff_role);

-- Extra test accounts. Passwords are for local testing only.
INSERT INTO users(full_name,email,phone,date_of_birth,address,avatar_path,avatar_thumbnail_path,password_hash,`role`,status,is_active,must_change_password,needs_handover,failed_login_attempts,locked_until,created_at,updated_at)
VALUES ('Giảng viên mẫu','teacher@gmail.com',NULL,NULL,NULL,NULL,NULL,'$pbkdf2$UzNUZXN0U2FsdDIwMjYhIZVaP2TNmt3Hy5W7u89ib5AvW4lQ2O20iai8tqLrKr9t','teacher','active',1,0,0,0,NULL,NOW(),NOW());
INSERT INTO user_roles(user_id,role_id) SELECT u.id,r.id FROM users u JOIN roles r ON r.slug='teacher' WHERE u.email='teacher@gmail.com';

INSERT INTO users(full_name,email,phone,date_of_birth,address,avatar_path,avatar_thumbnail_path,password_hash,`role`,status,is_active,must_change_password,needs_handover,failed_login_attempts,locked_until,created_at,updated_at)
VALUES ('Học viên mẫu','student@gmail.com',NULL,NULL,NULL,NULL,NULL,'$pbkdf2$UzNUZXN0U2FsdDIwMjYhITItEoSm7hZNb+0HGzpJ+fLMR3Z49iOQDdMoj8E4jCeC','student','active',1,0,0,0,NULL,NOW(),NOW());
INSERT INTO user_roles(user_id,role_id) SELECT u.id,r.id FROM users u JOIN roles r ON r.slug='student' WHERE u.email='student@gmail.com';

INSERT INTO training_rooms(code,name,room_type,capacity,online_url,is_active,created_at,updated_at)
VALUES ('R101','Phòng học 101','physical',30,NULL,1,NOW(),NOW()),
       ('ONLINE-01','Phòng học trực tuyến','online',100,'https://meet.example.com/sprint3-demo',1,NOW(),NOW());

UPDATE training_classes SET code='FS01-2026-01', expected_start_date=CURDATE(), max_students=30,
  delivery_mode='offline', status='preparing', completed_sessions=1,
  room_id=(SELECT id FROM training_rooms WHERE code='R101' LIMIT 1)
WHERE name='FS01 Demo';

INSERT INTO student_profiles(student_code,user_id,source_lead_id,entry_level,notes,created_at,updated_at)
SELECT 'STU-2026-001',u.id,l.id,'Cơ bản','Hồ sơ học viên mẫu Sprint 3',NOW(),NOW()
FROM users u LEFT JOIN leads l ON l.phone='0901234567'
WHERE u.email='student@gmail.com';

UPDATE leads SET status='closed', updated_at=NOW() WHERE phone='0901234567';
INSERT INTO lead_status_history(lead_id,from_status,to_status,reason,actor_user_id,changed_at)
SELECT l.id,'new','closed','Đã chuyển thành hồ sơ học viên mẫu',a.id,NOW()
FROM leads l JOIN users a ON a.email='admin@gmail.com' WHERE l.phone='0901234567';
INSERT INTO lead_status_history(lead_id,from_status,to_status,reason,actor_user_id,changed_at)
SELECT l.id,'new','contacted','Đã liên hệ lần đầu',a.id,NOW()
FROM leads l JOIN users a ON a.email='admissions@gmail.com' WHERE l.phone='0912345678';
INSERT INTO lead_interactions(lead_id,interaction_type,content,occurred_at,reminder_at,reminder_completed_at,created_by_user_id,created_at)
SELECT l.id,'call','Đã gọi tư vấn chương trình FS01; cần gọi lại xác nhận lịch học.',NOW(),DATE_ADD(NOW(), INTERVAL 1 DAY),NULL,a.id,NOW()
FROM leads l JOIN users a ON a.email='admissions@gmail.com' WHERE l.phone='0912345678';

INSERT INTO class_subjects(class_id,subject_id,order_index,prerequisite_subject_id)
SELECT tc.id,ps.subject_id,ps.order_index,ps.prerequisite_subject_id
FROM training_classes tc JOIN training_programs p ON p.id=tc.program_id
JOIN program_subjects ps ON ps.program_id=p.id
WHERE tc.name='FS01 Demo' AND p.code='FS01';

INSERT INTO class_enrollments(class_id,student_id,status,enrolled_at,enrolled_by_user_id)
SELECT tc.id,sp.id,'active',NOW(),a.id
FROM training_classes tc JOIN student_profiles sp ON sp.student_code='STU-2026-001'
JOIN users a ON a.email='admin@gmail.com'
WHERE tc.name='FS01 Demo';

INSERT INTO class_subject_staff(class_subject_id,user_id,staff_role,assigned_at,assigned_by_user_id)
SELECT cs.id,t.id,'teacher',NOW(),a.id
FROM class_subjects cs JOIN training_classes tc ON tc.id=cs.class_id
JOIN users t ON t.email='teacher@gmail.com'
JOIN users a ON a.email='admin@gmail.com'
WHERE tc.name='FS01 Demo';

-- Sprint 4 tables: timetable, holidays, schedule changes, status history, attendance and absence requests.
CREATE TABLE academic_holidays (
  id INT NOT NULL AUTO_INCREMENT,
  holiday_date DATE NOT NULL,
  name VARCHAR(200) NOT NULL,
  created_by_user_id INT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_academic_holidays_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;
CREATE UNIQUE INDEX ix_academic_holidays_holiday_date ON academic_holidays (holiday_date);

CREATE TABLE class_schedule_sessions (
  id INT NOT NULL AUTO_INCREMENT,
  class_id INT NOT NULL,
  class_subject_id INT NOT NULL,
  subject_session_id INT NOT NULL,
  start_at DATETIME NOT NULL,
  end_at DATETIME NOT NULL,
  room_id INT NULL,
  teacher_user_id INT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'scheduled',
  cancellation_reason VARCHAR(500) NULL,
  conflict_override BOOLEAN NOT NULL DEFAULT FALSE,
  created_by_user_id INT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT uq_class_schedule_lesson UNIQUE (class_id, subject_session_id),
  CONSTRAINT fk_class_schedule_sessions_class_id FOREIGN KEY (class_id) REFERENCES training_classes(id) ON DELETE CASCADE,
  CONSTRAINT fk_class_schedule_sessions_class_subject_id FOREIGN KEY (class_subject_id) REFERENCES class_subjects(id) ON DELETE CASCADE,
  CONSTRAINT fk_class_schedule_sessions_subject_session_id FOREIGN KEY (subject_session_id) REFERENCES subject_sessions(id) ON DELETE RESTRICT,
  CONSTRAINT fk_class_schedule_sessions_room_id FOREIGN KEY (room_id) REFERENCES training_rooms(id) ON DELETE SET NULL,
  CONSTRAINT fk_class_schedule_sessions_teacher_user_id FOREIGN KEY (teacher_user_id) REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT fk_class_schedule_sessions_created_by_user_id FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;
CREATE INDEX ix_class_schedule_sessions_class_id ON class_schedule_sessions (class_id);
CREATE INDEX ix_class_schedule_sessions_class_subject_id ON class_schedule_sessions (class_subject_id);
CREATE INDEX ix_class_schedule_sessions_subject_session_id ON class_schedule_sessions (subject_session_id);
CREATE INDEX ix_class_schedule_sessions_start_at ON class_schedule_sessions (start_at);
CREATE INDEX ix_class_schedule_sessions_end_at ON class_schedule_sessions (end_at);
CREATE INDEX ix_class_schedule_sessions_room_id ON class_schedule_sessions (room_id);
CREATE INDEX ix_class_schedule_sessions_teacher_user_id ON class_schedule_sessions (teacher_user_id);
CREATE INDEX ix_class_schedule_sessions_status ON class_schedule_sessions (status);

CREATE TABLE schedule_change_history (
  id INT NOT NULL AUTO_INCREMENT,
  schedule_session_id INT NOT NULL,
  action VARCHAR(30) NOT NULL,
  old_start_at DATETIME NULL,
  old_end_at DATETIME NULL,
  old_room_id INT NULL,
  old_teacher_user_id INT NULL,
  reason VARCHAR(500) NULL,
  actor_user_id INT NULL,
  changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_schedule_change_history_schedule_session_id FOREIGN KEY (schedule_session_id) REFERENCES class_schedule_sessions(id) ON DELETE CASCADE,
  CONSTRAINT fk_schedule_change_history_actor_user_id FOREIGN KEY (actor_user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;
CREATE INDEX ix_schedule_change_history_schedule_session_id ON schedule_change_history (schedule_session_id);
CREATE INDEX ix_schedule_change_history_changed_at ON schedule_change_history (changed_at);

CREATE TABLE user_notifications (
  id INT NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  title VARCHAR(200) NOT NULL,
  message TEXT NOT NULL,
  link VARCHAR(500) NULL,
  read_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_user_notifications_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;
CREATE INDEX ix_user_notifications_user_id ON user_notifications (user_id);
CREATE INDEX ix_user_notifications_created_at ON user_notifications (created_at);

CREATE TABLE student_status_history (
  id INT NOT NULL AUTO_INCREMENT,
  student_id INT NOT NULL,
  action VARCHAR(30) NOT NULL,
  from_class_id INT NULL,
  to_class_id INT NULL,
  effective_date DATE NOT NULL,
  reason VARCHAR(500) NOT NULL,
  actor_user_id INT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_student_status_history_student_id FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
  CONSTRAINT fk_student_status_history_from_class_id FOREIGN KEY (from_class_id) REFERENCES training_classes(id) ON DELETE SET NULL,
  CONSTRAINT fk_student_status_history_to_class_id FOREIGN KEY (to_class_id) REFERENCES training_classes(id) ON DELETE SET NULL,
  CONSTRAINT fk_student_status_history_actor_user_id FOREIGN KEY (actor_user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;
CREATE INDEX ix_student_status_history_student_id ON student_status_history (student_id);
CREATE INDEX ix_student_status_history_action ON student_status_history (action);
CREATE INDEX ix_student_status_history_effective_date ON student_status_history (effective_date);

CREATE TABLE attendance_records (
  id INT NOT NULL AUTO_INCREMENT,
  schedule_session_id INT NOT NULL,
  student_id INT NOT NULL,
  status VARCHAR(30) NOT NULL,
  note VARCHAR(500) NULL,
  marked_by_user_id INT NULL,
  marked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_by_user_id INT NULL,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT uq_attendance_session_student UNIQUE (schedule_session_id, student_id),
  CONSTRAINT fk_attendance_records_schedule_session_id FOREIGN KEY (schedule_session_id) REFERENCES class_schedule_sessions(id) ON DELETE CASCADE,
  CONSTRAINT fk_attendance_records_student_id FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
  CONSTRAINT fk_attendance_records_marked_by_user_id FOREIGN KEY (marked_by_user_id) REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT fk_attendance_records_updated_by_user_id FOREIGN KEY (updated_by_user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;
CREATE INDEX ix_attendance_records_schedule_session_id ON attendance_records (schedule_session_id);
CREATE INDEX ix_attendance_records_student_id ON attendance_records (student_id);
CREATE INDEX ix_attendance_records_status ON attendance_records (status);

CREATE TABLE attendance_audit_logs (
  id INT NOT NULL AUTO_INCREMENT,
  attendance_id INT NOT NULL,
  from_status VARCHAR(30) NULL,
  to_status VARCHAR(30) NOT NULL,
  reason VARCHAR(500) NULL,
  actor_user_id INT NULL,
  changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_attendance_audit_logs_attendance_id FOREIGN KEY (attendance_id) REFERENCES attendance_records(id) ON DELETE CASCADE,
  CONSTRAINT fk_attendance_audit_logs_actor_user_id FOREIGN KEY (actor_user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;
CREATE INDEX ix_attendance_audit_logs_attendance_id ON attendance_audit_logs (attendance_id);
CREATE INDEX ix_attendance_audit_logs_changed_at ON attendance_audit_logs (changed_at);

CREATE TABLE absence_requests (
  id INT NOT NULL AUTO_INCREMENT,
  schedule_session_id INT NOT NULL,
  student_id INT NOT NULL,
  reason TEXT NOT NULL,
  evidence_path VARCHAR(500) NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  reviewer_user_id INT NULL,
  review_reason VARCHAR(500) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  reviewed_at DATETIME NULL,
  PRIMARY KEY (id),
  CONSTRAINT fk_absence_requests_schedule_session_id FOREIGN KEY (schedule_session_id) REFERENCES class_schedule_sessions(id) ON DELETE CASCADE,
  CONSTRAINT fk_absence_requests_student_id FOREIGN KEY (student_id) REFERENCES student_profiles(id) ON DELETE CASCADE,
  CONSTRAINT fk_absence_requests_reviewer_user_id FOREIGN KEY (reviewer_user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;
CREATE INDEX ix_absence_requests_schedule_session_id ON absence_requests (schedule_session_id);
CREATE INDEX ix_absence_requests_student_id ON absence_requests (student_id);
CREATE INDEX ix_absence_requests_status ON absence_requests (status);

-- Sample Sprint 4 data for the FS01 demo class. The next Monday is used to keep sample sessions in the future.
INSERT INTO academic_holidays (holiday_date, name, created_by_user_id, created_at)
SELECT '2026-12-25', 'Nghỉ Giáng sinh (dữ liệu demo)', id, NOW()
FROM users WHERE email='admin@gmail.com';

SET @s4_monday = DATE_ADD(CURDATE(), INTERVAL (7 - WEEKDAY(CURDATE())) DAY);

INSERT INTO class_schedule_sessions
(class_id,class_subject_id,subject_session_id,start_at,end_at,room_id,teacher_user_id,status,cancellation_reason,conflict_override,created_by_user_id,created_at,updated_at)
SELECT tc.id,cs.id,ss.id,TIMESTAMP(@s4_monday,'09:00:00'),TIMESTAMP(@s4_monday,'12:00:00'),tr.id,t.id,'scheduled',NULL,FALSE,a.id,NOW(),NOW()
FROM training_classes tc
JOIN class_subjects cs ON cs.class_id=tc.id
JOIN subjects sub ON sub.id=cs.subject_id AND sub.code='HTML01'
JOIN subject_sessions ss ON ss.subject_id=sub.id AND ss.sequence=1
JOIN training_rooms tr ON tr.code='R101'
JOIN users t ON t.email='teacher@gmail.com'
JOIN users a ON a.email='admin@gmail.com'
WHERE tc.name='FS01 Demo';

INSERT INTO class_schedule_sessions
(class_id,class_subject_id,subject_session_id,start_at,end_at,room_id,teacher_user_id,status,cancellation_reason,conflict_override,created_by_user_id,created_at,updated_at)
SELECT tc.id,cs.id,ss.id,TIMESTAMP(DATE_ADD(@s4_monday, INTERVAL 1 DAY),'09:00:00'),TIMESTAMP(DATE_ADD(@s4_monday, INTERVAL 1 DAY),'12:00:00'),tr.id,t.id,'scheduled',NULL,FALSE,a.id,NOW(),NOW()
FROM training_classes tc
JOIN class_subjects cs ON cs.class_id=tc.id
JOIN subjects sub ON sub.id=cs.subject_id AND sub.code='HTML01'
JOIN subject_sessions ss ON ss.subject_id=sub.id AND ss.sequence=2
JOIN training_rooms tr ON tr.code='R101'
JOIN users t ON t.email='teacher@gmail.com'
JOIN users a ON a.email='admin@gmail.com'
WHERE tc.name='FS01 Demo';

INSERT INTO schedule_change_history(schedule_session_id,action,reason,actor_user_id,changed_at)
SELECT id,'created','Tạo lịch học mẫu Sprint 4', (SELECT id FROM users WHERE email='admin@gmail.com' LIMIT 1),NOW()
FROM class_schedule_sessions
WHERE class_id=(SELECT id FROM training_classes WHERE name='FS01 Demo' LIMIT 1);

INSERT INTO student_status_history(student_id,action,from_class_id,to_class_id,effective_date,reason,actor_user_id,created_at)
SELECT sp.id,'reactivate',NULL,tc.id,CURDATE(),'Ghi nhận trạng thái học viên hoạt động cho dữ liệu demo',a.id,NOW()
FROM student_profiles sp
JOIN class_enrollments ce ON ce.student_id=sp.id AND ce.status='active'
JOIN training_classes tc ON tc.id=ce.class_id AND tc.name='FS01 Demo'
JOIN users a ON a.email='admin@gmail.com'
WHERE sp.student_code='STU-2026-001';

INSERT INTO attendance_records(schedule_session_id,student_id,status,note,marked_by_user_id,marked_at,updated_by_user_id,updated_at)
SELECT css.id,sp.id,'present','Điểm danh mẫu Sprint 4',a.id,NOW(),a.id,NOW()
FROM class_schedule_sessions css
JOIN subject_sessions ss ON ss.id=css.subject_session_id AND ss.sequence=1
JOIN training_classes tc ON tc.id=css.class_id AND tc.name='FS01 Demo'
JOIN student_profiles sp ON sp.student_code='STU-2026-001'
JOIN users a ON a.email='admin@gmail.com';

INSERT INTO attendance_audit_logs(attendance_id,from_status,to_status,reason,actor_user_id,changed_at)
SELECT ar.id,NULL,'present','Tạo điểm danh mẫu',a.id,NOW()
FROM attendance_records ar JOIN users a ON a.email='admin@gmail.com'
JOIN class_schedule_sessions css ON css.id=ar.schedule_session_id
JOIN subject_sessions ss ON ss.id=css.subject_session_id AND ss.sequence=1;

INSERT INTO absence_requests(schedule_session_id,student_id,reason,evidence_path,status,reviewer_user_id,review_reason,created_at,reviewed_at)
SELECT css.id,sp.id,'Đơn xin phép mẫu để kiểm thử luồng duyệt.',NULL,'pending',NULL,NULL,NOW(),NULL
FROM class_schedule_sessions css
JOIN subject_sessions ss ON ss.id=css.subject_session_id AND ss.sequence=2
JOIN training_classes tc ON tc.id=css.class_id AND tc.name='FS01 Demo'
JOIN student_profiles sp ON sp.student_code='STU-2026-001';

INSERT INTO user_notifications(user_id,title,message,link,read_at,created_at)
SELECT u.id,'Lịch học mới','Bạn có lịch học HTML & CSS trong thời khóa biểu Sprint 4.','/my-schedule',NULL,NOW()
FROM users u WHERE u.email='student@gmail.com';

-- This SQL file already includes all Sprint 1–4 migration DDL.
UPDATE alembic_version SET version_num='20261013_0004';

-- Local test login accounts (for this test database only):
-- admin@gmail.com / Admin123
-- manager@gmail.com / Manager123
-- admissions@gmail.com / Admissions123
-- teacher@gmail.com / Teacher123
-- student@gmail.com / Student123
