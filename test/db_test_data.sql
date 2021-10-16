-- Add user info
INSERT INTO user_table (user_id, email, first_name, last_name, gender, dob)
VALUES
    ('543449a2-9225-479e-bf0c-c50da6b16b7c', 'ykhl1itj@naver.com', 'Yongkyun', 'Lee', 'male', '1996-03-02'), -- user1
    ('f39fbebb-d4c0-4520-9eb3-2cf5fdb734e2', 'yongkyun.daniel.lee@gmail.com', 'Drew', 'Choi', 'male', '1996-09-11'), -- user2
    ('google_117429865182265482928', '2dragonvirus@gmail.com', 'Jisoo', 'Lee', 'female', '1996-08-08'), -- user3
    ('cc06ed68-5909-4802-bd0c-7cf0b0a1c313', 'support@pagenow.io', 'Changhun', 'Lee', 'male', '1996-03-15'), -- user4
    ('9afb334e-a75a-444c-8250-9730f50fe031', 'abcdef@gmail.com', 'Brandon', 'Quach', 'male', '1996-04-01'), -- user5
    ('8010af9d-5ae5-46b2-b35c-7c995b8ea243', 'wxyz@gmail.com', 'Alex', 'Pan', 'male', '2000-03-17'), -- user6
    ('c7d9c2e3-e72a-4912-b607-dc85dd513be6', 'example1234@gmail.com', 'Collin', 'Kwon', 'male', '1996-11-07'), -- user7
    ('google_214425862782267482928', 'sample9876@gmail.com', 'Evan', 'Yeh', 'male', '1998-05-24'), -- user8
    ('7f7950f5-beee-4326-950b-7b3311bca55a', 'mno@gmail.com', 'Patrick', 'Yang', 'male', '1996-08-05'), -- user9
    ('867a93c6-5d8b-4f61-9f36-70dd9c0947db', 'test111@gmail.com', 'Jeff', 'Yang', 'male', '1996-08-05'); -- user10

-- Add friendship info
-- user1 friends: user2, user5, user6, user8, user9
-- user1 <-> user2, user1 -> user3, user2 <-> user4, user4 -> user3, user5 <-> user1
-- user6 <-> user1, user7 -> user1, user8 <-> user1, user9 <-> user1, user1 -> user10
-- user5 <-> user2, user2 -> user8, user2 <-> user9, user3 <-> user9, user10 <-> user8,
-- user9 <-> user10, user4 <-> user6, user2 <-> user6
INSERT INTO friendship_table(user_id1, user_id2, accepted_at)
VALUES
    ('543449a2-9225-479e-bf0c-c50da6b16b7c', 'f39fbebb-d4c0-4520-9eb3-2cf5fdb734e2', TIMESTAMP '2021-10-13 21:36:38'), -- user1 <-> user2
    ('543449a2-9225-479e-bf0c-c50da6b16b7c', 'google_117429865182265482928', NULL), -- user1 -> user3
    ('f39fbebb-d4c0-4520-9eb3-2cf5fdb734e2', 'cc06ed68-5909-4802-bd0c-7cf0b0a1c313', TIMESTAMP '2021-10-12 20:31:28'), -- user2 <-> user4
    ('cc06ed68-5909-4802-bd0c-7cf0b0a1c313', 'google_117429865182265482928', NULL), -- user4 -> user3
    ('9afb334e-a75a-444c-8250-9730f50fe031', '543449a2-9225-479e-bf0c-c50da6b16b7c', TIMESTAMP '2021-10-11 19:21:24'), -- user5 <-> user1
    ('8010af9d-5ae5-46b2-b35c-7c995b8ea243', '543449a2-9225-479e-bf0c-c50da6b16b7c', TIMESTAMP '2021-10-11 05:18:50'), -- user6 <-> user1
    ('c7d9c2e3-e72a-4912-b607-dc85dd513be6', '543449a2-9225-479e-bf0c-c50da6b16b7c', NULL), -- user7 -> user1
    ('google_214425862782267482928', '543449a2-9225-479e-bf0c-c50da6b16b7c', TIMESTAMP '2021-09-17 11:11:11'), -- user8 <-> user1
    ('7f7950f5-beee-4326-950b-7b3311bca55a', '543449a2-9225-479e-bf0c-c50da6b16b7c', TIMESTAMP '2021-10-13 10:10:10'), -- user9 <-> user1
    ('543449a2-9225-479e-bf0c-c50da6b16b7c', '867a93c6-5d8b-4f61-9f36-70dd9c0947db', NULL), -- user1 -> user10
    ('9afb334e-a75a-444c-8250-9730f50fe031', 'f39fbebb-d4c0-4520-9eb3-2cf5fdb734e2', TIMESTAMP '2021-10-01 18:51:01'), -- user5 <-> user2
    ('f39fbebb-d4c0-4520-9eb3-2cf5fdb734e2', 'google_214425862782267482928', NULL), -- user2 -> user8
    ('7f7950f5-beee-4326-950b-7b3311bca55a', 'f39fbebb-d4c0-4520-9eb3-2cf5fdb734e2', TIMESTAMP '2021-09-30 17:00:02'), -- user9 <-> user2
    ('google_117429865182265482928', '7f7950f5-beee-4326-950b-7b3311bca55a', TIMESTAMP '2021-08-08 06:01:10'), -- user3 <-> user9
    ('867a93c6-5d8b-4f61-9f36-70dd9c0947db', 'google_214425862782267482928', TIMESTAMP '2021-09-13 09:18:45'), -- user10 <-> user8
    ('7f7950f5-beee-4326-950b-7b3311bca55a', '867a93c6-5d8b-4f61-9f36-70dd9c0947db', TIMESTAMP '2021-10-16 11:11:11'), -- user9 <-> user10
    ('cc06ed68-5909-4802-bd0c-7cf0b0a1c313', '8010af9d-5ae5-46b2-b35c-7c995b8ea243', TIMESTAMP '2021-10-10 23:01:05'),
    ('f39fbebb-d4c0-4520-9eb3-2cf5fdb734e2', '8010af9d-5ae5-46b2-b35c-7c995b8ea243', TIMESTAMP '2021-10-01 11:11:11'); -- user4 <-> user6