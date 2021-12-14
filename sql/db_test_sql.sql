SELECT *, 1 AS match_score FROM user_table WHERE email LIKE '%drag%';

-- get all friends (pending included)
WITH friends AS (
    SELECT user_id2 AS user_id,
        CASE
            WHEN accepted_at IS NOT NULL THEN 2
            ELSE 1
        END AS accepted_state
    FROM friendship_table WHERE user_id1 = '543449a2-9225-479e-bf0c-c50da6b16b7c'
    UNION
    SELECT user_id1 AS user_id,
        CASE
            WHEN accepted_at IS NOT NULL THEN 2
            ELSE 1
        END AS accepted_state
    FROM friendship_table WHERE user_id2 = '543449a2-9225-479e-bf0c-c50da6b16b7c'
)
SELECT user_id, first_name, last_name, description, profile_image_extension,
    profile_image_uploaded_at, accepted_state
FROM friends NATURAL JOIN user_table
ORDER BY accepted_state DESC NULLS LAST, CONCAT(first_name, ' ', last_name) ASC;

-- get user search result using email
WITH user_friends AS (
    SELECT user_id2 AS user_id,
        CASE
            WHEN accepted_at IS NOT NULL THEN 2
            ELSE 1
        END AS accepted_state
    FROM friendship_table
    WHERE user_id1 = '543449a2-9225-479e-bf0c-c50da6b16b7c'
    UNION
    SELECT user_id1 AS user_id,
        CASE
            WHEN accepted_at IS NOT NULL THEN 2
            ELSE 1
        END AS accepted_state
    FROM friendship_table
    WHERE user_id2 = '543449a2-9225-479e-bf0c-c50da6b16b7c'
), user_id_filtered AS (
    SELECT user_id, MAX(match_score) AS match_score FROM (
        SELECT user_id, 3 AS match_score FROM user_table WHERE email LIKE LOWER('s%')
        UNION
        SELECT user_id, 2 AS match_score FROM user_table WHERE email LIKE LOWER('%s')
        UNION
        SELECT user_id, 1 AS match_score FROM user_table WHERE email LIKE LOWER('%s%')
    ) u WHERE user_id != '543449a2-9225-479e-bf0c-c50da6b16b7c' GROUP BY user_id
), friends AS (
    SELECT user_id1, user_id2 FROM friendship_table WHERE accepted_at IS NOT NULL
), user_friend_accepted AS (
    SELECT user_id FROM user_friends WHERE accepted_state = 2    
), search_result AS (
    SELECT user_id_filtered.user_id, first_name, last_name, description,
        profile_image_extension, COALESCE(accepted_state, 0) AS accepted_state, match_score
    FROM user_table NATURAL JOIN user_id_filtered
        LEFT JOIN user_friends ON user_id_filtered.user_id = user_friends.user_id
), search_result_with_friends AS (
    SELECT user_id, first_name, last_name, description, profile_image_extension,
        accepted_state, match_score, friends.user_id2 AS friend_id
    FROM search_result LEFT JOIN friends ON user_id = user_id1
    UNION
    SELECT user_id, first_name, last_name, description, profile_image_extension,
        accepted_state, match_score, friends.user_id1 AS friend_id
    FROM search_result LEFT JOIN friends ON user_id = user_id2
), search_result_mutual_friends AS ( -- (user_id, mutual_friend_count)
    SELECT search_result_with_friends.user_id AS user_id, COUNT(friend_id) AS mutual_friend_count
    FROM search_result_with_friends
        INNER JOIN user_friend_accepted ON friend_id = user_friend_accepted.user_id
    GROUP BY search_result_with_friends.user_id
)
SELECT search_result.user_id AS user_id, first_name, last_name, description,
    profile_image_extension, accepted_state, match_score, COALESCE(mutual_friend_count, 0) AS mutual_friend_count
FROM search_result LEFT JOIN search_result_mutual_friends
    ON search_result.user_id = search_result_mutual_friends.user_id
ORDER BY accepted_state DESC NULLS LAST, mutual_friend_count DESC, match_score DESC, user_id DESC; -- friend -> mutual friend count -> match_score -> user_id

-- get user search result using name
WITH user_friends AS (
    SELECT user_id2 AS user_id,
        CASE
            WHEN accepted_at IS NOT NULL THEN 2
            ELSE 1
        END AS accepted_state
    FROM friendship_table
    WHERE user_id1 = '543449a2-9225-479e-bf0c-c50da6b16b7c'
    UNION
    SELECT user_id1 AS user_id,
        CASE
            WHEN accepted_at IS NOT NULL THEN 2
            ELSE 1
        END AS accepted_state
    FROM friendship_table
    WHERE user_id2 = '543449a2-9225-479e-bf0c-c50da6b16b7c'
), user_id_filtered AS (
    SELECT user_id, MAX(match_score) AS match_score FROM (
        SELECT user_id, first_name, last_name, 3 AS match_score FROM user_table
        WHERE LOWER(CONCAT(first_name, ' ', last_name)) LIKE LOWER('e%')
        UNION
        SELECT user_id, first_name, last_name, 2 AS match_score FROM user_table
        WHERE LOWER(CONCAT(first_name, ' ', last_name)) LIKE LOWER('%e')
        UNION
        SELECT user_id, first_name, last_name, 1 AS match_score FROM user_table
        WHERE LOWER(CONCAT(first_name, ' ', last_name)) LIKE LOWER('%e%')
    ) u WHERE user_id != '543449a2-9225-479e-bf0c-c50da6b16b7c' GROUP BY user_id
), friends AS (
    SELECT user_id1, user_id2 FROM friendship_table WHERE accepted_at IS NOT NULL
), user_friend_accepted AS (
    SELECT user_id FROM user_friends WHERE accepted_state = 2    
), search_result AS (
    SELECT user_id_filtered.user_id, first_name, last_name, description,
        profile_image_extension, COALESCE(accepted_state, 0) AS accepted_state, match_score
    FROM user_table NATURAL JOIN user_id_filtered
        LEFT JOIN user_friends ON user_id_filtered.user_id = user_friends.user_id
    WHERE user_id_filtered.user_id != '543449a2-9225-479e-bf0c-c50da6b16b7c'
), search_result_with_friends AS (
    SELECT user_id, first_name, last_name, description, profile_image_extension,
        accepted_state, match_score, friends.user_id2 AS friend_id
    FROM search_result LEFT JOIN friends ON user_id = user_id1
    UNION
    SELECT user_id, first_name, last_name, description, profile_image_extension,
        accepted_state, match_score, friends.user_id1 AS friend_id
    FROM search_result LEFT JOIN friends ON user_id = user_id2
), search_result_mutual_friends AS ( -- (user_id, mutual_friend_count)
    SELECT search_result_with_friends.user_id AS user_id, COUNT(friend_id) AS mutual_friend_count
    FROM search_result_with_friends
        INNER JOIN user_friend_accepted ON friend_id = user_friend_accepted.user_id
    GROUP BY search_result_with_friends.user_id
)
SELECT search_result.user_id AS user_id, first_name, last_name, description,
    profile_image_extension, accepted_state, match_score, COALESCE(mutual_friend_count, 0) AS mutual_friend_count
FROM search_result LEFT JOIN search_result_mutual_friends
    ON search_result.user_id = search_result_mutual_friends.user_id
ORDER BY accepted_state DESC NULLS LAST, mutual_friend_count DESC, match_score DESC, user_id DESC;
-- friend -> mutual friend count -> match_score -> user_id

-- get all friendship requests users have received and not accepted yet
WITH friends_received AS (
    SELECT * FROM friendship_table
    WHERE user_id2 = '543449a2-9225-479e-bf0c-c50da6b16b7c'
        AND accepted_at IS NULL
)
SELECT user_id, first_name, last_name, description, profile_image_extension, requested_at
FROM user_table INNER JOIN friends_received
    ON friends_received.user_id1 = user_table.user_id
ORDER BY requested_at DESC;


-- get a list of mutual friends between two users
WITH my_friends AS (
    SELECT user_id1 AS friend_id FROM friendship_table
    WHERE user_id2 = '543449a2-9225-479e-bf0c-c50da6b16b7c'
        AND accepted_at IS NOT NULL
    UNION
    SELECT user_id2 AS friend_id FROM friendship_table
    WHERE user_id1 = '543449a2-9225-479e-bf0c-c50da6b16b7c'
        AND accepted_at IS NOT NULL
), user_friends AS (
    SELECT user_id1 AS friend_id FROM friendship_table
    WHERE user_id2 = 'cc06ed68-5909-4802-bd0c-7cf0b0a1c313'
        AND accepted_at IS NOT NULL
    UNION
    SELECT user_id2 AS friend_id FROM friendship_table
    WHERE user_id1 = 'cc06ed68-5909-4802-bd0c-7cf0b0a1c313'
        AND accepted_at IS NOT NULL
), mutual_friends AS (
    SELECT my_friends.friend_id AS user_id FROM my_friends INNER JOIN user_friends
        ON my_friends.friend_id = user_friends.friend_id
)
SELECT user_table.user_id, first_name, last_name, description, profile_image_extension
FROM user_table INNER JOIN mutual_friends
    ON user_table.user_id = mutual_friends.user_id


-- get all friendship requests users have received and not accepted yet (DEPRECATED - don't need mutual friend count)
WITH friends_received AS (
    SELECT * FROM friendship_table
    WHERE user_id2 = '543449a2-9225-479e-bf0c-c50da6b16b7c'
        AND accepted_at IS NULL
), friends_received_result AS (
    SELECT user_id, first_name, last_name, description, profile_image_extension, requested_at
    FROM user_table INNER JOIN friends_received
        ON friends_received.user_id1 = user_table.user_id
), friends AS (
    SELECT user_id1, user_id2 FROM friendship_table WHERE accepted_at IS NOT NULL
), friends_received_with_friends AS (
    SELECT user_id, first_name, last_name, description, profile_image_extension,
        friends.user_id2 AS friend_id, requested_at
    FROM friends_received_result LEFT JOIN friends ON user_id = user_id1
    UNION
    SELECT user_id, first_name, last_name, description, profile_image_extension,
        friends.user_id1 AS friend_id, requested_at
    FROM friends_received_result LEFT JOIN friends ON user_id = user_id2
), friends_received_mutual_friends AS (
    SELECT friends_received_with_friends.user_id AS user_id,
        COALESCE(COUNT(friend_id), 0) AS mutual_friend_count
    FROM friends_received_with_friends
    GROUP BY friends_received_with_friends.user_id
)
SELECT * FROM friends_received_mutual_friends;

-- get sent share notifictions
WITH user_share_notification AS (
    SELECT * FROM share_notification_table
    WHERE user_id = 'google_117429865182265482928'
    ORDER BY sent_at DESC
    LIMIT 2
), share_notification_not_seen AS (
    SELECT user_share_notification.event_id, COUNT(*) as not_seen_count
        FROM user_share_notification LEFT OUTER JOIN share_notification_seen_table
        ON user_share_notification.event_id = share_notification_seen_table.event_id
        WHERE share_notification_seen_table.seen_at is NULL
        GROUP BY user_share_notification.event_id
)
SELECT user_share_notification.event_id, url, title, sent_at,
    COALESCE(not_seen_count, 0) FROM
user_share_notification LEFT JOIN share_notification_not_seen
    ON share_notification_not_seen.event_id = user_share_notification.event_id;


----------------------------------------------
-- DEPRECATED --
-- get user search result using email (DEPRECATED - not returning mutual friends)
WITH friends AS (
    SELECT user_id2 AS user_id,
        CASE
            WHEN accepted_at IS NOT NULL THEN 2
            ELSE 1
        END AS accepted_state
    FROM friendship_table
    WHERE user_id1 = '543449a2-9225-479e-bf0c-c50da6b16b7c'
    UNION
    SELECT user_id1 AS user_id,
        CASE
            WHEN accepted_at IS NOT NULL THEN 2
            ELSE 1
        END AS accepted_state
    FROM friendship_table
    WHERE user_id2 = '543449a2-9225-479e-bf0c-c50da6b16b7c'
), user_id_filtered AS (
    SELECT user_id, MAX(match_score) AS match_score FROM (
        SELECT user_id, 3 AS match_score FROM user_table WHERE email LIKE 'e%'
        UNION
        SELECT user_id, 2 AS match_score FROM user_table WHERE email LIKE '%e'
        UNION
        SELECT user_id, 1 AS match_score FROM user_table WHERE email LIKE '%e%'
    ) u WHERE user_id != '543449a2-9225-479e-bf0c-c50da6b16b7c' GROUP BY user_id
)
SELECT user_id_filtered.user_id, first_name, last_name, description,
    profile_image_extension, COALESCE(accepted_state, 0) AS accepted_state, match_score
FROM user_table NATURAL JOIN user_id_filtered
    LEFT JOIN friends ON user_id_filtered.user_id = friends.user_id
ORDER BY accepted_state DESC NULLS LAST, match_score DESC, user_id DESC;

-- get search result using name (DEPRECATED)
WITH friends AS (
    SELECT user_id2 AS user_id, COALESCE(accepted_at, to_timestamp(0)) AS accepted_at FROM friendship_table
    WHERE user_id1 = '543449a2-9225-479e-bf0c-c50da6b16b7c'
    UNION
    SELECT user_id1 AS user_id, COALESCE(accepted_at, to_timestamp(0)) AS accepted_at FROM friendship_table
    WHERE user_id2 = '543449a2-9225-479e-bf0c-c50da6b16b7c'
), user_id_filtered AS (
    SELECT user_id, MAX(match_score) AS match_score FROM (
        SELECT user_id, first_name, last_name, 3 AS match_score FROM user_table WHERE LOWER(CONCAT(first_name, ' ', last_name)) LIKE 'y%'
        UNION
        SELECT user_id, first_name, last_name, 2 AS match_score FROM user_table WHERE LOWER(CONCAT(first_name, ' ', last_name)) LIKE '%y'
        UNION
        SELECT user_id, first_name, last_name, 1 AS match_score FROM user_table WHERE LOWER(CONCAT(first_name, ' ', last_name)) LIKE '%y%'
    ) u GROUP BY user_id
)
SELECT user_id_filtered.user_id, first_name, last_name, description, profile_image_extension, accepted_at, match_score
FROM user_table NATURAL JOIN user_id_filtered LEFT JOIN friends ON user_id_filtered.user_id = friends.user_id
ORDER BY accepted_at DESC NULLS LAST, match_score DESC;

-- get user search result using name (DEPRECATED - not returning mutual friends)
WITH friends AS (
    SELECT user_id2 AS user_id, accepted_at,
        CASE
            WHEN accepted_at IS NOT NULL THEN 2
            ELSE 1
        END AS accepted_state
    FROM friendship_table
    WHERE user_id1 = '543449a2-9225-479e-bf0c-c50da6b16b7c'
    UNION
    SELECT user_id1 AS user_id, accepted_at,
        CASE
            WHEN accepted_at IS NOT NULL THEN 2
            ELSE 1
        END AS accepted_state
    FROM friendship_table    
    WHERE user_id2 = '543449a2-9225-479e-bf0c-c50da6b16b7c'
), user_id_filtered AS (
    SELECT user_id, MAX(match_score) AS match_score FROM (
        SELECT user_id, first_name, last_name, 3 AS match_score FROM user_table WHERE LOWER(CONCAT(first_name, ' ', last_name)) LIKE 'a%'
        UNION
        SELECT user_id, first_name, last_name, 2 AS match_score FROM user_table WHERE LOWER(CONCAT(first_name, ' ', last_name)) LIKE '%a'
        UNION
        SELECT user_id, first_name, last_name, 1 AS match_score FROM user_table WHERE LOWER(CONCAT(first_name, ' ', last_name)) LIKE '%a%'
    ) u WHERE user_id != '543449a2-9225-479e-bf0c-c50da6b16b7c' GROUP BY user_id
)
SELECT user_id_filtered.user_id, email, first_name, last_name, description,
    profile_image_extension, COALESCE(accepted_state, 0) AS accepted_state, match_score
FROM user_table NATURAL JOIN user_id_filtered
    LEFT JOIN friends ON user_id_filtered.user_id = friends.user_id
ORDER BY accepted_state DESC NULLS LAST, match_score DESC, user_id DESC;
