-- ============================================================
-- HOTEL MANAGEMENT SYSTEM - SQL SERVER DATABASE SCHEMA
-- ============================================================

USE master;
GO

-- Create Database
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'HotelManagement')
BEGIN
    CREATE DATABASE HotelManagement;
END
GO

USE HotelManagement;
GO

-- ============================================================
-- TABLE: Guests
-- ============================================================
IF OBJECT_ID('dbo.Guests', 'U') IS NOT NULL DROP TABLE dbo.Guests;
CREATE TABLE dbo.Guests (
    guest_id        INT IDENTITY(1,1) PRIMARY KEY,
    name            NVARCHAR(100)  NOT NULL,
    email           NVARCHAR(150)  UNIQUE NOT NULL,
    phone           NVARCHAR(20)   NOT NULL,
    address         NVARCHAR(300),
    id_proof_type   NVARCHAR(50),   -- passport, driver_license, national_id
    id_proof_number NVARCHAR(100),
    created_at      DATETIME2 DEFAULT GETDATE(),
    updated_at      DATETIME2 DEFAULT GETDATE()
);
GO

-- ============================================================
-- TABLE: Rooms
-- ============================================================
IF OBJECT_ID('dbo.Rooms', 'U') IS NOT NULL DROP TABLE dbo.Rooms;
CREATE TABLE dbo.Rooms (
    room_id         INT IDENTITY(1,1) PRIMARY KEY,
    room_number     NVARCHAR(10)   UNIQUE NOT NULL,
    room_type       NVARCHAR(50)   NOT NULL,  -- Standard, Deluxe, Suite, Presidential
    price_per_night DECIMAL(10,2)  NOT NULL,
    status          NVARCHAR(20)   NOT NULL DEFAULT 'available', -- available, occupied, maintenance, reserved
    floor           INT            NOT NULL,
    description     NVARCHAR(500),
    max_occupancy   INT DEFAULT 2,
    amenities       NVARCHAR(500),
    created_at      DATETIME2 DEFAULT GETDATE()
);
GO

-- ============================================================
-- TABLE: Reservations
-- ============================================================
IF OBJECT_ID('dbo.Reservations', 'U') IS NOT NULL DROP TABLE dbo.Reservations;
CREATE TABLE dbo.Reservations (
    reservation_id  INT IDENTITY(1,1) PRIMARY KEY,
    guest_id        INT            NOT NULL REFERENCES dbo.Guests(guest_id),
    room_id         INT            NOT NULL REFERENCES dbo.Rooms(room_id),
    check_in_date   DATE           NOT NULL,
    check_out_date  DATE           NOT NULL,
    total_price     DECIMAL(10,2)  NOT NULL,
    status          NVARCHAR(20)   NOT NULL DEFAULT 'confirmed', -- confirmed, checked_in, checked_out, cancelled
    booking_date    DATETIME2      DEFAULT GETDATE(),
    special_requests NVARCHAR(500),
    adults          INT DEFAULT 1,
    children        INT DEFAULT 0,
    updated_at      DATETIME2 DEFAULT GETDATE()
);
GO

-- ============================================================
-- TABLE: Payments
-- ============================================================
IF OBJECT_ID('dbo.Payments', 'U') IS NOT NULL DROP TABLE dbo.Payments;
CREATE TABLE dbo.Payments (
    payment_id      INT IDENTITY(1,1) PRIMARY KEY,
    reservation_id  INT            NOT NULL REFERENCES dbo.Reservations(reservation_id),
    amount          DECIMAL(10,2)  NOT NULL,
    payment_date    DATETIME2      DEFAULT GETDATE(),
    payment_method  NVARCHAR(50)   NOT NULL, -- cash, credit_card, debit_card, bank_transfer, online
    status          NVARCHAR(20)   NOT NULL DEFAULT 'completed', -- pending, completed, refunded, failed
    transaction_id  NVARCHAR(100),
    notes           NVARCHAR(300)
);
GO

-- ============================================================
-- TABLE: Staff
-- ============================================================
IF OBJECT_ID('dbo.Staff', 'U') IS NOT NULL DROP TABLE dbo.Staff;
CREATE TABLE dbo.Staff (
    staff_id        INT IDENTITY(1,1) PRIMARY KEY,
    name            NVARCHAR(100)  NOT NULL,
    position        NVARCHAR(100)  NOT NULL, -- Manager, Receptionist, Housekeeping, Chef, etc.
    salary          DECIMAL(10,2)  NOT NULL,
    contact         NVARCHAR(20)   NOT NULL,
    email           NVARCHAR(150)  UNIQUE,
    shift           NVARCHAR(20)   NOT NULL DEFAULT 'morning', -- morning, afternoon, night
    hire_date       DATE           DEFAULT CAST(GETDATE() AS DATE),
    status          NVARCHAR(20)   DEFAULT 'active', -- active, inactive
    username        NVARCHAR(50)   UNIQUE,
    password_hash   NVARCHAR(256),
    role            NVARCHAR(20)   DEFAULT 'staff', -- admin, manager, staff
    created_at      DATETIME2      DEFAULT GETDATE()
);
GO

-- ============================================================
-- TABLE: Services
-- ============================================================
IF OBJECT_ID('dbo.Services', 'U') IS NOT NULL DROP TABLE dbo.Services;
CREATE TABLE dbo.Services (
    service_id      INT IDENTITY(1,1) PRIMARY KEY,
    service_name    NVARCHAR(100)  NOT NULL,
    description     NVARCHAR(500),
    price           DECIMAL(10,2)  NOT NULL,
    category        NVARCHAR(50),  -- food, spa, transport, laundry, other
    available       BIT DEFAULT 1,
    created_at      DATETIME2 DEFAULT GETDATE()
);
GO

-- ============================================================
-- TABLE: Guest_Services
-- ============================================================
IF OBJECT_ID('dbo.Guest_Services', 'U') IS NOT NULL DROP TABLE dbo.Guest_Services;
CREATE TABLE dbo.Guest_Services (
    guest_service_id INT IDENTITY(1,1) PRIMARY KEY,
    guest_id         INT            NOT NULL REFERENCES dbo.Guests(guest_id),
    service_id       INT            NOT NULL REFERENCES dbo.Services(service_id),
    reservation_id   INT            REFERENCES dbo.Reservations(reservation_id),
    date             DATETIME2      DEFAULT GETDATE(),
    quantity         INT            NOT NULL DEFAULT 1,
    total_price      DECIMAL(10,2)  NOT NULL,
    status           NVARCHAR(20)   DEFAULT 'pending', -- pending, delivered, cancelled
    notes            NVARCHAR(300)
);
GO

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX IX_Reservations_GuestId   ON dbo.Reservations(guest_id);
CREATE INDEX IX_Reservations_RoomId    ON dbo.Reservations(room_id);
CREATE INDEX IX_Reservations_Dates     ON dbo.Reservations(check_in_date, check_out_date);
CREATE INDEX IX_Reservations_Status    ON dbo.Reservations(status);
CREATE INDEX IX_Payments_ReservationId ON dbo.Payments(reservation_id);
CREATE INDEX IX_GuestServices_GuestId  ON dbo.Guest_Services(guest_id);
GO

-- ============================================================
-- SEED DATA
-- ============================================================

-- Rooms
INSERT INTO dbo.Rooms (room_number, room_type, price_per_night, status, floor, description, max_occupancy, amenities) VALUES
('101', 'Standard',    99.00,  'available',   1, 'Cozy standard room with city view',        2, 'WiFi, TV, AC, Mini-bar'),
('102', 'Standard',    99.00,  'available',   1, 'Cozy standard room with garden view',      2, 'WiFi, TV, AC'),
('103', 'Standard',    99.00,  'occupied',    1, 'Standard room with pool view',             2, 'WiFi, TV, AC, Mini-bar'),
('201', 'Deluxe',      149.00, 'available',   2, 'Spacious deluxe room with balcony',        2, 'WiFi, TV, AC, Mini-bar, Bathtub'),
('202', 'Deluxe',      149.00, 'maintenance', 2, 'Deluxe room with king-size bed',           2, 'WiFi, TV, AC, Mini-bar'),
('203', 'Deluxe',      149.00, 'available',   2, 'Deluxe room with panoramic view',          3, 'WiFi, TV, AC, Mini-bar, Jacuzzi'),
('301', 'Suite',       249.00, 'available',   3, 'Luxury suite with separate living room',   4, 'WiFi, TV, AC, Mini-bar, Jacuzzi, Kitchen'),
('302', 'Suite',       249.00, 'occupied',    3, 'Executive suite with business facilities', 3, 'WiFi, TV, AC, Mini-bar, Work Desk'),
('401', 'Presidential',499.00, 'available',   4, 'Presidential suite with private terrace',  6, 'WiFi, TV, AC, Full Kitchen, Jacuzzi, Butler Service'),
('402', 'Presidential',499.00, 'available',   4, 'Presidential suite with ocean view',       6, 'WiFi, TV, AC, Full Kitchen, Private Pool');

-- Services
INSERT INTO dbo.Services (service_name, description, price, category) VALUES
('Room Breakfast',        'Continental breakfast delivered to room',   15.00, 'food'),
('Room Dinner',           'Fine dining dinner served in room',         35.00, 'food'),
('Spa Treatment',         '60-minute full body massage',               80.00, 'spa'),
('Airport Transfer',      'Private car to/from airport',               50.00, 'transport'),
('Laundry Service',       'Per item laundry and dry cleaning',          5.00, 'laundry'),
('Mini Bar Restock',      'Full mini bar restock',                     25.00, 'food'),
('Late Checkout',         'Extend checkout up to 4 hours',             30.00, 'other'),
('Extra Bed',             'Additional bed for the room',               20.00, 'other'),
('Business Center',       'Access to business center facilities',      15.00, 'other'),
('Swimming Pool Access',  'Full day pool access with towels',          10.00, 'other');

-- Admin Staff (password: admin123 - bcrypt hashed placeholder)
INSERT INTO dbo.Staff (name, position, salary, contact, email, shift, username, password_hash, role) VALUES
('Admin User',     'System Administrator', 5000.00, '555-0001', 'admin@hotel.com',      'morning',   'admin',    '$2b$12$placeholder_hash_admin',   'admin'),
('John Manager',   'Hotel Manager',        4500.00, '555-0002', 'manager@hotel.com',    'morning',   'manager',  '$2b$12$placeholder_hash_manager', 'manager'),
('Sarah Front',    'Receptionist',         2500.00, '555-0003', 'sarah@hotel.com',      'morning',   'sarah',    '$2b$12$placeholder_hash_sarah',   'staff'),
('Mike Night',     'Night Receptionist',   2700.00, '555-0004', 'mike@hotel.com',       'night',     'mike',     '$2b$12$placeholder_hash_mike',    'staff'),
('Lisa Housekeeper','Head Housekeeper',    2800.00, '555-0005', 'lisa@hotel.com',       'afternoon', 'lisa',     '$2b$12$placeholder_hash_lisa',    'staff');

-- Sample Guests
INSERT INTO dbo.Guests (name, email, phone, address, id_proof_type, id_proof_number) VALUES
('Alice Johnson',   'alice@example.com',   '555-1001', '123 Main St, New York',     'passport',       'P12345678'),
('Bob Williams',    'bob@example.com',     '555-1002', '456 Oak Ave, Los Angeles',  'driver_license', 'DL987654'),
('Carol Davis',     'carol@example.com',   '555-1003', '789 Pine Rd, Chicago',      'national_id',    'NID456789'),
('David Brown',     'david@example.com',   '555-1004', '321 Elm St, Houston',       'passport',       'P87654321'),
('Emma Wilson',     'emma@example.com',    '555-1005', '654 Maple Dr, Phoenix',     'passport',       'P11223344');
GO

PRINT 'Database schema and seed data created successfully!';
GO
USE HotelManagement;

SELECT * FROM Guests;
SELECT * FROM Rooms;
SELECT * FROM Reservations;
SELECT * FROM Staff;
SELECT * FROM Payments;
SELECT * FROM Services;
SELECT * FROM Guest_Services;