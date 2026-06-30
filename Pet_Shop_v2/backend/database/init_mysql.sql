CREATE DATABASE IF NOT EXISTS pet_shop_v2
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'pet_shop'@'localhost' IDENTIFIED BY 'change_me';
CREATE USER IF NOT EXISTS 'pet_shop'@'127.0.0.1' IDENTIFIED BY 'change_me';
GRANT ALL PRIVILEGES ON pet_shop_v2.* TO 'pet_shop'@'localhost';
GRANT ALL PRIVILEGES ON pet_shop_v2.* TO 'pet_shop'@'127.0.0.1';

USE pet_shop_v2;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS operation_logs;
DROP TABLE IF EXISTS review_tasks;
DROP TABLE IF EXISTS pet_coin_logs;
DROP TABLE IF EXISTS pet_coin_rules;
DROP TABLE IF EXISTS pet_coin_accounts;
DROP TABLE IF EXISTS user_memberships;
DROP TABLE IF EXISTS membership_plans;
DROP TABLE IF EXISTS user_coupons;
DROP TABLE IF EXISTS coupons;
DROP TABLE IF EXISTS merchant_promotions;
DROP TABLE IF EXISTS activities;
DROP TABLE IF EXISTS knowledge_articles;
DROP TABLE IF EXISTS knowledge_categories;
DROP TABLE IF EXISTS follows;
DROP TABLE IF EXISTS user_interactions;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS post_topics;
DROP TABLE IF EXISTS topics;
DROP TABLE IF EXISTS post_media;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS service_bookings;
DROP TABLE IF EXISTS service_schedules;
DROP TABLE IF EXISTS service_items;
DROP TABLE IF EXISTS service_providers;
DROP TABLE IF EXISTS adoption_follow_ups;
DROP TABLE IF EXISTS adoption_applications;
DROP TABLE IF EXISTS adoption_pets;
DROP TABLE IF EXISTS live_pets;
DROP TABLE IF EXISTS after_sales;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS cart_items;
DROP TABLE IF EXISTS product_media;
DROP TABLE IF EXISTS product_skus;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS product_categories;
DROP TABLE IF EXISTS pet_reminders;
DROP TABLE IF EXISTS pet_growth_records;
DROP TABLE IF EXISTS pet_profiles;
DROP TABLE IF EXISTS merchant_stores;
DROP TABLE IF EXISTS user_addresses;
DROP TABLE IF EXISTS user_real_name_verifications;
DROP TABLE IF EXISTS auth_accounts;
DROP TABLE IF EXISTS user_roles;
DROP TABLE IF EXISTS role_permissions;
DROP TABLE IF EXISTS permissions;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE users (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  phone VARCHAR(20) NULL,
  password_hash VARCHAR(255) NULL,
  nickname VARCHAR(64) NOT NULL,
  avatar_url VARCHAR(512) NULL,
  gender VARCHAR(16) NOT NULL DEFAULT 'unknown',
  city VARCHAR(64) NULL,
  bio VARCHAR(255) NULL,
  has_pet TINYINT(1) NOT NULL DEFAULT 0,
  pet_count INT UNSIGNED NOT NULL DEFAULT 0,
  interest_tags JSON NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  real_name_status VARCHAR(32) NOT NULL DEFAULT 'unverified',
  last_login_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_users_phone (phone),
  KEY idx_users_city (city),
  KEY idx_users_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE roles (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  code VARCHAR(64) NOT NULL,
  name VARCHAR(64) NOT NULL,
  description VARCHAR(255) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_roles_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE permissions (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  code VARCHAR(96) NOT NULL,
  name VARCHAR(96) NOT NULL,
  module VARCHAR(64) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_permissions_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE role_permissions (
  role_id BIGINT UNSIGNED NOT NULL,
  permission_id BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (role_id, permission_id),
  CONSTRAINT fk_role_permissions_role FOREIGN KEY (role_id) REFERENCES roles(id),
  CONSTRAINT fk_role_permissions_permission FOREIGN KEY (permission_id) REFERENCES permissions(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE user_roles (
  user_id BIGINT UNSIGNED NOT NULL,
  role_id BIGINT UNSIGNED NOT NULL,
  merchant_id BIGINT UNSIGNED NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, role_id),
  KEY idx_user_roles_role (role_id),
  CONSTRAINT fk_user_roles_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_user_roles_role FOREIGN KEY (role_id) REFERENCES roles(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE auth_accounts (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  provider VARCHAR(32) NOT NULL,
  provider_user_id VARCHAR(128) NOT NULL,
  credential_hash VARCHAR(255) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_auth_provider_user (provider, provider_user_id),
  KEY idx_auth_user (user_id),
  CONSTRAINT fk_auth_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE user_real_name_verifications (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  real_name VARCHAR(64) NOT NULL,
  id_card_no_encrypted VARCHAR(512) NOT NULL,
  face_image_url VARCHAR(512) NULL,
  business_license_url VARCHAR(512) NULL,
  qualification_urls JSON NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'pending',
  reject_reason VARCHAR(255) NULL,
  reviewed_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_real_name_user (user_id),
  KEY idx_real_name_status (status),
  CONSTRAINT fk_real_name_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE user_addresses (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  receiver_name VARCHAR(64) NOT NULL,
  receiver_phone VARCHAR(20) NOT NULL,
  province VARCHAR(64) NOT NULL,
  city VARCHAR(64) NOT NULL,
  district VARCHAR(64) NOT NULL,
  detail_address VARCHAR(255) NOT NULL,
  postal_code VARCHAR(16) NULL,
  is_default TINYINT(1) NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_addresses_user (user_id),
  CONSTRAINT fk_addresses_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE merchant_stores (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  owner_user_id BIGINT UNSIGNED NOT NULL,
  store_name VARCHAR(128) NOT NULL,
  store_type VARCHAR(32) NOT NULL,
  logo_url VARCHAR(512) NULL,
  contact_phone VARCHAR(20) NULL,
  province VARCHAR(64) NULL,
  city VARCHAR(64) NULL,
  district VARCHAR(64) NULL,
  address VARCHAR(255) NULL,
  business_license_url VARCHAR(512) NULL,
  qualification_urls JSON NULL,
  deposit_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  rating DECIMAL(3,2) NOT NULL DEFAULT 5.00,
  status VARCHAR(32) NOT NULL DEFAULT 'pending',
  reject_reason VARCHAR(255) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_merchants_owner (owner_user_id),
  KEY idx_merchants_city_status (city, status),
  CONSTRAINT fk_merchants_owner FOREIGN KEY (owner_user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE pet_profiles (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  name VARCHAR(64) NOT NULL,
  pet_type VARCHAR(32) NOT NULL,
  breed VARCHAR(64) NULL,
  gender VARCHAR(16) NOT NULL DEFAULT 'unknown',
  birthday DATE NULL,
  arrival_date DATE NULL,
  weight DECIMAL(6,2) NULL,
  avatar_url VARCHAR(512) NULL,
  sterilized VARCHAR(16) NOT NULL DEFAULT 'unknown',
  vaccine_status VARCHAR(32) NOT NULL DEFAULT 'unknown',
  deworm_status VARCHAR(32) NOT NULL DEFAULT 'unknown',
  health_notes TEXT NULL,
  is_current TINYINT(1) NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_pet_profiles_user (user_id),
  KEY idx_pet_profiles_type (pet_type),
  CONSTRAINT fk_pet_profiles_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE pet_growth_records (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  pet_id BIGINT UNSIGNED NOT NULL,
  user_id BIGINT UNSIGNED NOT NULL,
  record_type VARCHAR(32) NOT NULL,
  title VARCHAR(128) NULL,
  content TEXT NULL,
  media_urls JSON NULL,
  weight DECIMAL(6,2) NULL,
  record_date DATE NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_growth_pet_date (pet_id, record_date),
  KEY idx_growth_user (user_id),
  CONSTRAINT fk_growth_pet FOREIGN KEY (pet_id) REFERENCES pet_profiles(id),
  CONSTRAINT fk_growth_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE pet_reminders (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  pet_id BIGINT UNSIGNED NOT NULL,
  user_id BIGINT UNSIGNED NOT NULL,
  reminder_type VARCHAR(32) NOT NULL,
  title VARCHAR(128) NOT NULL,
  remind_at DATETIME NOT NULL,
  repeat_rule VARCHAR(64) NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_reminders_user_time (user_id, remind_at),
  KEY idx_reminders_pet (pet_id),
  CONSTRAINT fk_reminders_pet FOREIGN KEY (pet_id) REFERENCES pet_profiles(id),
  CONSTRAINT fk_reminders_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE product_categories (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  parent_id BIGINT UNSIGNED NULL,
  name VARCHAR(64) NOT NULL,
  icon_url VARCHAR(512) NULL,
  sort_order INT NOT NULL DEFAULT 0,
  status VARCHAR(32) NOT NULL DEFAULT 'enabled',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_categories_parent (parent_id),
  CONSTRAINT fk_categories_parent FOREIGN KEY (parent_id) REFERENCES product_categories(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE products (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  merchant_id BIGINT UNSIGNED NOT NULL,
  category_id BIGINT UNSIGNED NOT NULL,
  title VARCHAR(160) NOT NULL,
  sub_title VARCHAR(255) NULL,
  brand VARCHAR(64) NULL,
  origin_place VARCHAR(128) NULL,
  main_image_url VARCHAR(512) NULL,
  video_url VARCHAR(512) NULL,
  price DECIMAL(10,2) NOT NULL,
  original_price DECIMAL(10,2) NULL,
  stock INT UNSIGNED NOT NULL DEFAULT 0,
  sales_count INT UNSIGNED NOT NULL DEFAULT 0,
  applicable_pet_types JSON NULL,
  applicable_age VARCHAR(64) NULL,
  shelf_life VARCHAR(64) NULL,
  ingredients TEXT NULL,
  usage_instructions TEXT NULL,
  cautions TEXT NULL,
  description LONGTEXT NULL,
  after_sale_policy TEXT NULL,
  logistics_note TEXT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'draft',
  audit_status VARCHAR(32) NOT NULL DEFAULT 'pending',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_products_merchant (merchant_id),
  KEY idx_products_category_status (category_id, status),
  KEY idx_products_price (price),
  FULLTEXT KEY ft_products_title (title, sub_title),
  CONSTRAINT fk_products_merchant FOREIGN KEY (merchant_id) REFERENCES merchant_stores(id),
  CONSTRAINT fk_products_category FOREIGN KEY (category_id) REFERENCES product_categories(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE product_skus (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  product_id BIGINT UNSIGNED NOT NULL,
  sku_name VARCHAR(128) NOT NULL,
  spec_values JSON NULL,
  price DECIMAL(10,2) NOT NULL,
  original_price DECIMAL(10,2) NULL,
  stock INT UNSIGNED NOT NULL DEFAULT 0,
  sku_code VARCHAR(64) NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'enabled',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_skus_product (product_id),
  UNIQUE KEY uk_skus_code (sku_code),
  CONSTRAINT fk_skus_product FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE product_media (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  product_id BIGINT UNSIGNED NOT NULL,
  media_type VARCHAR(16) NOT NULL,
  media_url VARCHAR(512) NOT NULL,
  sort_order INT NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_product_media_product (product_id),
  CONSTRAINT fk_product_media_product FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE cart_items (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  product_id BIGINT UNSIGNED NOT NULL,
  sku_id BIGINT UNSIGNED NULL,
  quantity INT UNSIGNED NOT NULL DEFAULT 1,
  selected TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_cart_user_sku (user_id, product_id, sku_id),
  KEY idx_cart_user (user_id),
  CONSTRAINT fk_cart_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_cart_product FOREIGN KEY (product_id) REFERENCES products(id),
  CONSTRAINT fk_cart_sku FOREIGN KEY (sku_id) REFERENCES product_skus(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE orders (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  order_no VARCHAR(64) NOT NULL,
  user_id BIGINT UNSIGNED NOT NULL,
  merchant_id BIGINT UNSIGNED NOT NULL,
  address_id BIGINT UNSIGNED NULL,
  total_amount DECIMAL(10,2) NOT NULL,
  discount_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  pet_coin_deduct_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  freight_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  pay_amount DECIMAL(10,2) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'pending_payment',
  remark VARCHAR(255) NULL,
  paid_at DATETIME NULL,
  shipped_at DATETIME NULL,
  received_at DATETIME NULL,
  completed_at DATETIME NULL,
  canceled_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_orders_no (order_no),
  KEY idx_orders_user_status (user_id, status),
  KEY idx_orders_merchant_status (merchant_id, status),
  CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_orders_merchant FOREIGN KEY (merchant_id) REFERENCES merchant_stores(id),
  CONSTRAINT fk_orders_address FOREIGN KEY (address_id) REFERENCES user_addresses(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE order_items (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  order_id BIGINT UNSIGNED NOT NULL,
  product_id BIGINT UNSIGNED NOT NULL,
  sku_id BIGINT UNSIGNED NULL,
  product_title VARCHAR(160) NOT NULL,
  sku_name VARCHAR(128) NULL,
  product_image_url VARCHAR(512) NULL,
  price DECIMAL(10,2) NOT NULL,
  quantity INT UNSIGNED NOT NULL,
  total_amount DECIMAL(10,2) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_order_items_order (order_id),
  KEY idx_order_items_product (product_id),
  CONSTRAINT fk_order_items_order FOREIGN KEY (order_id) REFERENCES orders(id),
  CONSTRAINT fk_order_items_product FOREIGN KEY (product_id) REFERENCES products(id),
  CONSTRAINT fk_order_items_sku FOREIGN KEY (sku_id) REFERENCES product_skus(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE payments (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  order_id BIGINT UNSIGNED NOT NULL,
  payment_no VARCHAR(64) NOT NULL,
  payment_method VARCHAR(32) NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'pending',
  third_party_trade_no VARCHAR(128) NULL,
  paid_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_payments_no (payment_no),
  KEY idx_payments_order (order_id),
  CONSTRAINT fk_payments_order FOREIGN KEY (order_id) REFERENCES orders(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE after_sales (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  order_id BIGINT UNSIGNED NOT NULL,
  order_item_id BIGINT UNSIGNED NULL,
  user_id BIGINT UNSIGNED NOT NULL,
  merchant_id BIGINT UNSIGNED NOT NULL,
  after_sale_type VARCHAR(32) NOT NULL,
  reason VARCHAR(255) NOT NULL,
  description TEXT NULL,
  media_urls JSON NULL,
  refund_amount DECIMAL(10,2) NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'pending',
  reviewed_at DATETIME NULL,
  completed_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_after_sales_order (order_id),
  KEY idx_after_sales_user (user_id),
  KEY idx_after_sales_merchant_status (merchant_id, status),
  CONSTRAINT fk_after_sales_order FOREIGN KEY (order_id) REFERENCES orders(id),
  CONSTRAINT fk_after_sales_item FOREIGN KEY (order_item_id) REFERENCES order_items(id),
  CONSTRAINT fk_after_sales_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_after_sales_merchant FOREIGN KEY (merchant_id) REFERENCES merchant_stores(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE live_pets (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  merchant_id BIGINT UNSIGNED NOT NULL,
  pet_name VARCHAR(64) NULL,
  pet_type VARCHAR(32) NOT NULL,
  breed VARCHAR(64) NULL,
  gender VARCHAR(16) NOT NULL DEFAULT 'unknown',
  birthday DATE NULL,
  color VARCHAR(64) NULL,
  weight DECIMAL(6,2) NULL,
  city VARCHAR(64) NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  deposit_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  negotiable TINYINT(1) NOT NULL DEFAULT 0,
  support_video_view TINYINT(1) NOT NULL DEFAULT 0,
  support_offline_view TINYINT(1) NOT NULL DEFAULT 0,
  support_delivery TINYINT(1) NOT NULL DEFAULT 0,
  vaccine_info TEXT NULL,
  deworm_info TEXT NULL,
  health_certificate_url VARCHAR(512) NULL,
  quarantine_certificate_url VARCHAR(512) NULL,
  chip_no VARCHAR(64) NULL,
  pedigree_certificate_url VARCHAR(512) NULL,
  personality TEXT NULL,
  diet_habit TEXT NULL,
  inherited_disease_note TEXT NULL,
  after_sale_commitment TEXT NULL,
  media_urls JSON NULL,
  description TEXT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'pending',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_live_pets_merchant (merchant_id),
  KEY idx_live_pets_filter (pet_type, city, status),
  KEY idx_live_pets_price (price),
  CONSTRAINT fk_live_pets_merchant FOREIGN KEY (merchant_id) REFERENCES merchant_stores(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE adoption_pets (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  publisher_id BIGINT UNSIGNED NOT NULL,
  organization_id BIGINT UNSIGNED NULL,
  pet_name VARCHAR(64) NOT NULL,
  pet_type VARCHAR(32) NOT NULL,
  breed VARCHAR(64) NULL,
  gender VARCHAR(16) NOT NULL DEFAULT 'unknown',
  age_desc VARCHAR(64) NULL,
  body_size VARCHAR(32) NULL,
  city VARCHAR(64) NOT NULL,
  sterilized VARCHAR(16) NOT NULL DEFAULT 'unknown',
  vaccine_status VARCHAR(32) NOT NULL DEFAULT 'unknown',
  deworm_status VARCHAR(32) NOT NULL DEFAULT 'unknown',
  health_status TEXT NULL,
  personality TEXT NULL,
  rescue_story TEXT NULL,
  adoption_condition TEXT NULL,
  adoption_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  media_urls JSON NULL,
  follow_up_required TINYINT(1) NOT NULL DEFAULT 1,
  status VARCHAR(32) NOT NULL DEFAULT 'pending',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_adoption_publisher (publisher_id),
  KEY idx_adoption_org (organization_id),
  KEY idx_adoption_filter (pet_type, city, status),
  CONSTRAINT fk_adoption_publisher FOREIGN KEY (publisher_id) REFERENCES users(id),
  CONSTRAINT fk_adoption_org FOREIGN KEY (organization_id) REFERENCES merchant_stores(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE adoption_applications (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  adoption_pet_id BIGINT UNSIGNED NOT NULL,
  applicant_user_id BIGINT UNSIGNED NOT NULL,
  applicant_name VARCHAR(64) NOT NULL,
  applicant_phone VARCHAR(20) NOT NULL,
  city VARCHAR(64) NOT NULL,
  living_condition VARCHAR(255) NULL,
  own_house TINYINT(1) NULL,
  family_agreed TINYINT(1) NULL,
  has_pet_experience TINYINT(1) NULL,
  current_has_pet TINYINT(1) NULL,
  job_info VARCHAR(128) NULL,
  monthly_pet_budget DECIMAL(10,2) NULL,
  reason TEXT NULL,
  accept_follow_up TINYINT(1) NOT NULL DEFAULT 1,
  accept_sterilization TINYINT(1) NOT NULL DEFAULT 1,
  accept_agreement TINYINT(1) NOT NULL DEFAULT 1,
  status VARCHAR(32) NOT NULL DEFAULT 'submitted',
  reviewed_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_applications_pet (adoption_pet_id),
  KEY idx_applications_user (applicant_user_id),
  KEY idx_applications_status (status),
  CONSTRAINT fk_applications_pet FOREIGN KEY (adoption_pet_id) REFERENCES adoption_pets(id),
  CONSTRAINT fk_applications_user FOREIGN KEY (applicant_user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE adoption_follow_ups (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  application_id BIGINT UNSIGNED NOT NULL,
  follow_up_day INT UNSIGNED NOT NULL,
  follow_up_at DATETIME NOT NULL,
  pet_photo_urls JSON NULL,
  health_status TEXT NULL,
  diet_status TEXT NULL,
  living_environment TEXT NULL,
  abnormal_note TEXT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'pending',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_follow_ups_application (application_id),
  KEY idx_follow_ups_time (follow_up_at),
  CONSTRAINT fk_follow_ups_application FOREIGN KEY (application_id) REFERENCES adoption_applications(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE service_providers (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  merchant_id BIGINT UNSIGNED NULL,
  provider_type VARCHAR(32) NOT NULL,
  display_name VARCHAR(64) NOT NULL,
  avatar_url VARCHAR(512) NULL,
  city VARCHAR(64) NULL,
  introduction TEXT NULL,
  qualification_urls JSON NULL,
  rating DECIMAL(3,2) NOT NULL DEFAULT 5.00,
  status VARCHAR(32) NOT NULL DEFAULT 'pending',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_service_provider_user (user_id),
  KEY idx_service_provider_merchant (merchant_id),
  KEY idx_service_provider_city (city, status),
  CONSTRAINT fk_service_provider_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_service_provider_merchant FOREIGN KEY (merchant_id) REFERENCES merchant_stores(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE service_items (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  provider_id BIGINT UNSIGNED NOT NULL,
  service_type VARCHAR(32) NOT NULL,
  title VARCHAR(128) NOT NULL,
  description TEXT NULL,
  price DECIMAL(10,2) NOT NULL,
  duration_minutes INT UNSIGNED NOT NULL DEFAULT 60,
  cover_url VARCHAR(512) NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'enabled',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_service_items_provider (provider_id),
  KEY idx_service_items_type (service_type, status),
  CONSTRAINT fk_service_items_provider FOREIGN KEY (provider_id) REFERENCES service_providers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE service_schedules (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  provider_id BIGINT UNSIGNED NOT NULL,
  service_date DATE NOT NULL,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  capacity INT UNSIGNED NOT NULL DEFAULT 1,
  booked_count INT UNSIGNED NOT NULL DEFAULT 0,
  status VARCHAR(32) NOT NULL DEFAULT 'available',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_schedules_provider_date (provider_id, service_date),
  CONSTRAINT fk_schedules_provider FOREIGN KEY (provider_id) REFERENCES service_providers(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE service_bookings (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  booking_no VARCHAR(64) NOT NULL,
  user_id BIGINT UNSIGNED NOT NULL,
  pet_id BIGINT UNSIGNED NULL,
  service_item_id BIGINT UNSIGNED NOT NULL,
  schedule_id BIGINT UNSIGNED NULL,
  amount DECIMAL(10,2) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'pending_payment',
  service_photo_urls JSON NULL,
  user_remark VARCHAR(255) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_service_bookings_no (booking_no),
  KEY idx_service_bookings_user (user_id, status),
  KEY idx_service_bookings_item (service_item_id),
  CONSTRAINT fk_service_bookings_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_service_bookings_pet FOREIGN KEY (pet_id) REFERENCES pet_profiles(id),
  CONSTRAINT fk_service_bookings_item FOREIGN KEY (service_item_id) REFERENCES service_items(id),
  CONSTRAINT fk_service_bookings_schedule FOREIGN KEY (schedule_id) REFERENCES service_schedules(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE posts (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  pet_id BIGINT UNSIGNED NULL,
  post_type VARCHAR(32) NOT NULL DEFAULT 'daily',
  content TEXT NULL,
  location VARCHAR(128) NULL,
  visibility VARCHAR(32) NOT NULL DEFAULT 'public',
  status VARCHAR(32) NOT NULL DEFAULT 'pending',
  like_count INT UNSIGNED NOT NULL DEFAULT 0,
  comment_count INT UNSIGNED NOT NULL DEFAULT 0,
  favorite_count INT UNSIGNED NOT NULL DEFAULT 0,
  share_count INT UNSIGNED NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_posts_user (user_id),
  KEY idx_posts_pet (pet_id),
  KEY idx_posts_status_created (status, created_at),
  CONSTRAINT fk_posts_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_posts_pet FOREIGN KEY (pet_id) REFERENCES pet_profiles(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE post_media (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  post_id BIGINT UNSIGNED NOT NULL,
  media_type VARCHAR(16) NOT NULL,
  media_url VARCHAR(512) NOT NULL,
  cover_url VARCHAR(512) NULL,
  sort_order INT NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_post_media_post (post_id),
  CONSTRAINT fk_post_media_post FOREIGN KEY (post_id) REFERENCES posts(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE topics (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(64) NOT NULL,
  description VARCHAR(255) NULL,
  post_count INT UNSIGNED NOT NULL DEFAULT 0,
  status VARCHAR(32) NOT NULL DEFAULT 'enabled',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_topics_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE post_topics (
  post_id BIGINT UNSIGNED NOT NULL,
  topic_id BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (post_id, topic_id),
  KEY idx_post_topics_topic (topic_id),
  CONSTRAINT fk_post_topics_post FOREIGN KEY (post_id) REFERENCES posts(id),
  CONSTRAINT fk_post_topics_topic FOREIGN KEY (topic_id) REFERENCES topics(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE comments (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  target_type VARCHAR(32) NOT NULL,
  target_id BIGINT UNSIGNED NOT NULL,
  parent_id BIGINT UNSIGNED NULL,
  content TEXT NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'visible',
  like_count INT UNSIGNED NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_comments_target (target_type, target_id),
  KEY idx_comments_user (user_id),
  KEY idx_comments_parent (parent_id),
  CONSTRAINT fk_comments_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_comments_parent FOREIGN KEY (parent_id) REFERENCES comments(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE user_interactions (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  interaction_type VARCHAR(32) NOT NULL,
  target_type VARCHAR(32) NOT NULL,
  target_id BIGINT UNSIGNED NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_interactions_user_target (user_id, interaction_type, target_type, target_id),
  KEY idx_interactions_target (interaction_type, target_type, target_id),
  CONSTRAINT fk_interactions_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE follows (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  follower_user_id BIGINT UNSIGNED NOT NULL,
  followed_user_id BIGINT UNSIGNED NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_follows_pair (follower_user_id, followed_user_id),
  KEY idx_follows_followed (followed_user_id),
  CONSTRAINT fk_follows_follower FOREIGN KEY (follower_user_id) REFERENCES users(id),
  CONSTRAINT fk_follows_followed FOREIGN KEY (followed_user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE knowledge_categories (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  parent_id BIGINT UNSIGNED NULL,
  name VARCHAR(64) NOT NULL,
  sort_order INT NOT NULL DEFAULT 0,
  status VARCHAR(32) NOT NULL DEFAULT 'enabled',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_knowledge_categories_parent (parent_id),
  CONSTRAINT fk_knowledge_categories_parent FOREIGN KEY (parent_id) REFERENCES knowledge_categories(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE knowledge_articles (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  category_id BIGINT UNSIGNED NOT NULL,
  author_user_id BIGINT UNSIGNED NULL,
  title VARCHAR(160) NOT NULL,
  summary VARCHAR(255) NULL,
  cover_url VARCHAR(512) NULL,
  content LONGTEXT NOT NULL,
  view_count INT UNSIGNED NOT NULL DEFAULT 0,
  status VARCHAR(32) NOT NULL DEFAULT 'draft',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_articles_category (category_id, status),
  KEY idx_articles_author (author_user_id),
  FULLTEXT KEY ft_articles_title (title, summary),
  CONSTRAINT fk_articles_category FOREIGN KEY (category_id) REFERENCES knowledge_categories(id),
  CONSTRAINT fk_articles_author FOREIGN KEY (author_user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE coupons (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(128) NOT NULL,
  coupon_type VARCHAR(32) NOT NULL,
  threshold_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  discount_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  discount_rate DECIMAL(5,2) NULL,
  total_quantity INT UNSIGNED NOT NULL DEFAULT 0,
  received_quantity INT UNSIGNED NOT NULL DEFAULT 0,
  valid_from DATETIME NOT NULL,
  valid_to DATETIME NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'draft',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_coupons_status_time (status, valid_from, valid_to)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE activities (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  title VARCHAR(128) NOT NULL,
  activity_type VARCHAR(32) NOT NULL,
  cover_url VARCHAR(512) NULL,
  description TEXT NULL,
  start_at DATETIME NOT NULL,
  end_at DATETIME NOT NULL,
  sort_order INT NOT NULL DEFAULT 0,
  status VARCHAR(32) NOT NULL DEFAULT 'draft',
  created_by BIGINT UNSIGNED NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_activities_status_time (status, start_at, end_at),
  KEY idx_activities_creator (created_by),
  CONSTRAINT fk_activities_creator FOREIGN KEY (created_by) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE merchant_promotions (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  merchant_id BIGINT UNSIGNED NOT NULL,
  title VARCHAR(128) NOT NULL,
  promotion_type VARCHAR(32) NOT NULL,
  rule JSON NULL,
  start_at DATETIME NOT NULL,
  end_at DATETIME NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'draft',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_promotions_merchant_status (merchant_id, status),
  KEY idx_promotions_time (start_at, end_at),
  CONSTRAINT fk_promotions_merchant FOREIGN KEY (merchant_id) REFERENCES merchant_stores(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE user_coupons (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  coupon_id BIGINT UNSIGNED NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'unused',
  used_order_id BIGINT UNSIGNED NULL,
  received_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  used_at DATETIME NULL,
  PRIMARY KEY (id),
  KEY idx_user_coupons_user_status (user_id, status),
  KEY idx_user_coupons_coupon (coupon_id),
  CONSTRAINT fk_user_coupons_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_user_coupons_coupon FOREIGN KEY (coupon_id) REFERENCES coupons(id),
  CONSTRAINT fk_user_coupons_order FOREIGN KEY (used_order_id) REFERENCES orders(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE membership_plans (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(64) NOT NULL,
  level_code VARCHAR(32) NOT NULL,
  duration_days INT UNSIGNED NOT NULL,
  price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  benefits JSON NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'enabled',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_membership_level (level_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE user_memberships (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  plan_id BIGINT UNSIGNED NOT NULL,
  start_at DATETIME NOT NULL,
  end_at DATETIME NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'active',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_user_memberships_user (user_id, status),
  KEY idx_user_memberships_plan (plan_id),
  CONSTRAINT fk_user_memberships_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_user_memberships_plan FOREIGN KEY (plan_id) REFERENCES membership_plans(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE pet_coin_accounts (
  user_id BIGINT UNSIGNED NOT NULL,
  balance INT NOT NULL DEFAULT 0,
  total_earned INT NOT NULL DEFAULT 0,
  total_used INT NOT NULL DEFAULT 0,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id),
  CONSTRAINT fk_coin_accounts_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE pet_coin_rules (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  rule_code VARCHAR(64) NOT NULL,
  rule_name VARCHAR(96) NOT NULL,
  change_amount INT NOT NULL,
  daily_limit INT UNSIGNED NULL,
  monthly_limit INT UNSIGNED NULL,
  expire_days INT UNSIGNED NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'enabled',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_coin_rules_code (rule_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE pet_coin_logs (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  change_amount INT NOT NULL,
  balance_before INT NOT NULL,
  balance_after INT NOT NULL,
  change_type VARCHAR(32) NOT NULL,
  source VARCHAR(64) NOT NULL,
  related_type VARCHAR(32) NULL,
  related_id BIGINT UNSIGNED NULL,
  expire_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_coin_logs_user_time (user_id, created_at),
  KEY idx_coin_logs_source (source),
  CONSTRAINT fk_coin_logs_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE review_tasks (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  target_type VARCHAR(32) NOT NULL,
  target_id BIGINT UNSIGNED NOT NULL,
  submitter_user_id BIGINT UNSIGNED NULL,
  reviewer_user_id BIGINT UNSIGNED NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'pending',
  reason VARCHAR(255) NULL,
  reviewed_at DATETIME NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_review_target (target_type, target_id),
  KEY idx_review_status (status),
  KEY idx_review_submitter (submitter_user_id),
  KEY idx_review_reviewer (reviewer_user_id),
  CONSTRAINT fk_review_submitter FOREIGN KEY (submitter_user_id) REFERENCES users(id),
  CONSTRAINT fk_review_reviewer FOREIGN KEY (reviewer_user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE operation_logs (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  actor_user_id BIGINT UNSIGNED NULL,
  action VARCHAR(64) NOT NULL,
  target_type VARCHAR(32) NULL,
  target_id BIGINT UNSIGNED NULL,
  ip_address VARCHAR(64) NULL,
  user_agent VARCHAR(255) NULL,
  detail JSON NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_operation_actor (actor_user_id),
  KEY idx_operation_target (target_type, target_id),
  KEY idx_operation_created (created_at),
  CONSTRAINT fk_operation_actor FOREIGN KEY (actor_user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO roles (code, name, description) VALUES
  ('user', 'Normal User', 'Pet owner or future pet owner'),
  ('merchant', 'Merchant', 'Pet store, breeder, product seller, or service store'),
  ('rescuer', 'Rescue Or Sender', 'Rescue organization or adoption publisher'),
  ('service_provider', 'Service Provider', 'Groomer, trainer, boarding worker, feeder, or walker'),
  ('operator', 'Platform Operator', 'Platform staff for audit and operations'),
  ('admin', 'Administrator', 'System administrator');

INSERT INTO permissions (code, name, module) VALUES
  ('product:view', 'View Products', 'mall'),
  ('order:create', 'Create Orders', 'mall'),
  ('post:create', 'Create Posts', 'community'),
  ('pet_profile:manage', 'Manage Pet Profiles', 'pet_profile'),
  ('adoption:apply', 'Apply Adoption', 'adoption'),
  ('service:book', 'Book Services', 'service'),
  ('merchant:manage_products', 'Manage Merchant Products', 'merchant'),
  ('merchant:manage_orders', 'Manage Merchant Orders', 'merchant'),
  ('merchant:publish_live_pet', 'Publish Live Pets', 'live_pet'),
  ('merchant:publish_promotion', 'Publish Merchant Promotions', 'merchant'),
  ('adoption:publish', 'Publish Adoption Pets', 'adoption'),
  ('adoption:review_application', 'Review Adoption Applications', 'adoption'),
  ('service:publish', 'Publish Services', 'service'),
  ('service:accept_booking', 'Accept Service Bookings', 'service'),
  ('audit:merchant', 'Audit Merchants', 'audit'),
  ('audit:live_pet', 'Audit Live Pets', 'audit'),
  ('audit:content', 'Audit Content', 'audit'),
  ('coin_rule:manage', 'Manage Pet Coin Rules', 'operation'),
  ('activity:manage', 'Manage Activities', 'operation'),
  ('membership:manage', 'Manage Membership Benefits', 'operation'),
  ('config:operate', 'Manage Platform Config', 'operation'),
  ('report:view', 'View Reports', 'report');

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r JOIN permissions p
WHERE r.code = 'user'
  AND p.code IN ('product:view', 'order:create', 'post:create', 'pet_profile:manage', 'adoption:apply', 'service:book');

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r JOIN permissions p
WHERE r.code = 'merchant'
  AND p.code IN ('merchant:manage_products', 'merchant:manage_orders', 'merchant:publish_live_pet', 'merchant:publish_promotion');

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r JOIN permissions p
WHERE r.code = 'rescuer'
  AND p.code IN ('adoption:publish', 'adoption:review_application');

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r JOIN permissions p
WHERE r.code = 'service_provider'
  AND p.code IN ('service:publish', 'service:accept_booking');

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r JOIN permissions p
WHERE r.code = 'operator'
  AND p.code IN ('audit:merchant', 'audit:live_pet', 'audit:content', 'coin_rule:manage', 'activity:manage', 'membership:manage', 'config:operate', 'report:view');

INSERT INTO pet_coin_rules (rule_code, rule_name, change_amount, daily_limit, monthly_limit, expire_days, status) VALUES
  ('daily_check_in', 'Daily Check In', 5, 1, NULL, 365, 'enabled'),
  ('complete_pet_profile', 'Complete Pet Profile', 50, NULL, 1, 365, 'enabled'),
  ('first_order', 'First Order', 100, NULL, 1, 365, 'enabled'),
  ('order_review', 'Order Review', 20, 5, NULL, 365, 'enabled'),
  ('quality_post', 'Quality Community Post', 30, 3, NULL, 365, 'enabled'),
  ('adoption_follow_up', 'Adoption Follow Up Upload', 50, NULL, NULL, 365, 'enabled');

INSERT INTO membership_plans (name, level_code, duration_days, price, benefits, status) VALUES
  ('Normal Member', 'normal', 0, 0.00, JSON_ARRAY('basic_profile', 'basic_community'), 'enabled'),
  ('Monthly Member', 'monthly', 30, 19.90, JSON_ARRAY('coupon_pack', 'member_discount', 'priority_service'), 'enabled'),
  ('Yearly Member', 'yearly', 365, 168.00, JSON_ARRAY('coupon_pack', 'member_discount', 'exclusive_support'), 'enabled');

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r JOIN permissions p
WHERE r.code = 'admin';
