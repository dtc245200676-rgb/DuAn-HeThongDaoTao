-- Sprint 2 full test database. WARNING: this DROPS he_thong_dao_tao.
DROP DATABASE IF EXISTS he_thong_dao_tao;
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

-- Mark schema as already at latest Alembic revision.
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
