-- Add user info
INSERT INTO user_table (user_id, email, first_name, middle_name, last_name, gender, dob)
VALUES
    ('543449a2-9225-479e-bf0c-c50da6b16b7c', 'ykhl1itj@naver.com', 'Yongkyun', '', 'Lee', 'male', '1996-03-02'),
    ('f39fbebb-d4c0-4520-9eb3-2cf5fdb734e2', 'yongkyun.daniel.lee@gmail.com', 'Drew', '', 'Choi', 'male', '1996-09-11'),
    ('google_117429865182265482928', '2dragonvirus@gmail.com', 'Jisoo', '', 'Lee', 'female', '1996-08-08'),
    ('cc06ed68-5909-4802-bd0c-7cf0b0a1c313', 'support@pagenow.io', 'Changhun', 'Quentin', 'Lee', 'male', '1996-03-15');

-- Add friendship info
-- user1 <-> user2, user1 -> user3, user2 <-> user4, user4 -> user3
INSERT INTO friendship_table(user_id1, user_id2, accepted_at)
VALUES
    ('543449a2-9225-479e-bf0c-c50da6b16b7c', 'f39fbebb-d4c0-4520-9eb3-2cf5fdb734e2', TIMESTAMP '2021-10-13 21:36:38'),
    ('543449a2-9225-479e-bf0c-c50da6b16b7c', 'google_117429865182265482928', NULL),
    ('f39fbebb-d4c0-4520-9eb3-2cf5fdb734e2', 'cc06ed68-5909-4802-bd0c-7cf0b0a1c313', TIMESTAMP '2021-10-12 20:31:28'),
    ('cc06ed68-5909-4802-bd0c-7cf0b0a1c313', 'google_117429865182265482928', NULL);