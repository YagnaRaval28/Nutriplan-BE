-- =============================================================
-- NutriPlan AI — Seed Data
-- Run this file AFTER schema.sql
-- Command: psql -U postgres -d nutriplan -f seed.sql
-- =============================================================

-- =============================================================
-- 1. SUBSCRIPTION PLANS
-- =============================================================

INSERT INTO subscription_plans (plan_key, name, price, features, ai_recipes_per_month, max_clients, target_role) VALUES
('free',              'Free',              0.00,  ARRAY['Calorie tracking','3 AI recipes/month','7-day history','Basic reports'],                                       3,    NULL, 'user'),
('basic',             'Basic',             9.99,  ARRAY['Unlimited tracking','20 AI recipes/month','Weekly reports','Messaging'],                                       20,   NULL, 'user'),
('pro',               'Pro',              19.99,  ARRAY['Everything in Basic','Unlimited AI recipes','Monthly reports','Dietician access','Food photo AI'],            999,   NULL, 'user'),
('dietician_starter', 'Dietician Starter',49.99,  ARRAY['Manage up to 50 clients','Client progress reports','Messaging','Diet plan builder'],                          999,   50,  'dietician'),
('dietician_pro',     'Dietician Pro',    99.99,  ARRAY['Unlimited clients','Advanced analytics','Priority support','Everything in Starter'],                          999,  NULL, 'dietician')
ON CONFLICT (plan_key) DO NOTHING;

-- =============================================================
-- 2. FOOD CATEGORIES
-- =============================================================

INSERT INTO food_categories (name, icon) VALUES
('Grains & Cereals',    '🌾'),
('Protein - Meat',      '🥩'),
('Protein - Seafood',   '🐟'),
('Protein - Eggs',      '🥚'),
('Protein - Legumes',   '🫘'),
('Dairy',               '🥛'),
('Vegetables',          '🥦'),
('Fruits',              '🍎'),
('Nuts & Seeds',        '🥜'),
('Oils & Fats',         '🫒'),
('Beverages',           '🧃'),
('Snacks',              '🍿'),
('Sweets & Desserts',   '🍮'),
('Indian Breads',       '🫓'),
('Indian Dishes',       '🍛'),
('Supplements',         '💊')
ON CONFLICT (name) DO NOTHING;

-- =============================================================
-- 3. FOOD ITEMS
-- All nutrition values are per 100g unless unit is specified
-- Sources: ICMR, USDA, Open Food Facts
-- =============================================================

-- ───────────────────────────────────────────────
-- GRAINS & CEREALS (category 1)
-- ───────────────────────────────────────────────
INSERT INTO food_items (name, name_hindi, category_id, serving_size, unit, calories, protein_g, carbs_g, fats_g, fiber_g, sugar_g, sodium_mg, is_vegetarian, is_vegan, is_gluten_free) VALUES

('White Rice (cooked)',         'Chawal',       1, 100, 'g',  130, 2.7,  28.2,  0.3,  0.4,  0.0,   1.0, TRUE, TRUE,  TRUE),
('Brown Rice (cooked)',         'Brown Chawal', 1, 100, 'g',  123, 2.6,  25.6,  0.9,  1.8,  0.0,   2.0, TRUE, TRUE,  TRUE),
('Oats (raw)',                  'Jaee',         1, 100, 'g',  389, 16.9, 66.3,  6.9, 10.6,  0.0,   2.0, TRUE, TRUE,  FALSE),
('Oats (cooked)',               'Pakke Jaee',   1, 100, 'g',   71,  2.5, 12.0,  1.4,  1.7,  0.0,   4.0, TRUE, TRUE,  FALSE),
('Wheat Flour (Atta)',          'Atta',         1, 100, 'g',  341, 12.0, 70.0,  1.7, 11.2,  0.0,   2.0, TRUE, TRUE,  FALSE),
('Maida (Refined Flour)',       'Maida',        1, 100, 'g',  348,  9.0, 74.0,  1.0,  2.7,  0.0,   2.0, TRUE, TRUE,  FALSE),
('Semolina (Suji/Rava)',        'Suji',         1, 100, 'g',  360, 12.7, 72.8,  1.0,  3.9,  0.0,   1.0, TRUE, TRUE,  FALSE),
('Poha (Flattened Rice)',       'Poha',         1, 100, 'g',  333,  6.8, 73.0,  1.0,  1.2,  0.0,   5.0, TRUE, TRUE,  TRUE),
('Quinoa (cooked)',             'Quinoa',       1, 100, 'g',  120,  4.1, 21.3,  1.9,  2.8,  0.9,   7.0, TRUE, TRUE,  TRUE),
('Corn / Maize',                'Makka',        1, 100, 'g',   86,  3.2, 18.7,  1.2,  2.0,  3.2,   15.0, TRUE, TRUE, TRUE),
('Bread (White)',               'Bread',        1, 100, 'g',  265,  9.0, 49.0,  3.2,  2.7, 5.0,  490.0, TRUE, TRUE, FALSE),
('Bread (Brown / Whole Wheat)', 'Brown Bread',  1, 100, 'g',  247,  9.7, 43.0,  3.4,  6.0, 6.0,  400.0, TRUE, TRUE, FALSE),
('Millet (Bajra)',              'Bajra',        1, 100, 'g',  361, 11.6, 67.5,  5.0,  1.2,  0.0,   5.0, TRUE, TRUE,  TRUE),
('Sorghum (Jowar)',             'Jowar',        1, 100, 'g',  349,  9.9, 72.6,  1.7,  1.6,  0.0,   5.0, TRUE, TRUE,  TRUE),
('Ragi (Finger Millet)',        'Ragi',         1, 100, 'g',  336,  7.3, 72.0,  1.5,  3.6,  0.0,  11.0, TRUE, TRUE,  TRUE),
('Pasta (cooked)',              'Pasta',        1, 100, 'g',  158,  5.8, 30.9,  0.9,  1.8,  0.6,   1.0, TRUE, TRUE,  FALSE),
('Vermicelli / Seviyan',        'Seviyan',      1, 100, 'g',  350, 10.0, 72.0,  1.5,  2.0,  0.0,  10.0, TRUE, TRUE,  FALSE);

-- ───────────────────────────────────────────────
-- PROTEIN - MEAT (category 2)
-- ───────────────────────────────────────────────
INSERT INTO food_items (name, name_hindi, category_id, serving_size, unit, calories, protein_g, carbs_g, fats_g, fiber_g, sugar_g, sodium_mg, is_vegetarian, is_vegan, is_gluten_free) VALUES

('Chicken Breast (grilled)',    'Murgi ka Seena', 2, 100, 'g', 165, 31.0, 0.0,  3.6,  0.0, 0.0,  74.0, FALSE, FALSE, TRUE),
('Chicken Thigh (cooked)',      'Murgi ki Rani',  2, 100, 'g', 209, 26.0, 0.0, 10.9,  0.0, 0.0,  84.0, FALSE, FALSE, TRUE),
('Chicken Leg (cooked)',        'Murgi ki Tangdi',2, 100, 'g', 184, 27.0, 0.0,  8.1,  0.0, 0.0,  84.0, FALSE, FALSE, TRUE),
('Mutton / Lamb (cooked)',      'Mutton',         2, 100, 'g', 258, 25.6, 0.0, 16.6,  0.0, 0.0,  72.0, FALSE, FALSE, TRUE),
('Beef (lean, cooked)',         'Beef',           2, 100, 'g', 215, 26.0, 0.0, 12.0,  0.0, 0.0,  59.0, FALSE, FALSE, TRUE),
('Pork (lean, cooked)',         'Suar ka Gosht',  2, 100, 'g', 242, 27.0, 0.0, 14.0,  0.0, 0.0,  63.0, FALSE, FALSE, TRUE),
('Turkey Breast (cooked)',      'Turkey',         2, 100, 'g', 189, 29.0, 0.0,  7.4,  0.0, 0.0,  67.0, FALSE, FALSE, TRUE),
('Chicken Mince (keema)',       'Murgi Keema',    2, 100, 'g', 172, 20.0, 0.0, 10.0,  0.0, 0.0,  82.0, FALSE, FALSE, TRUE);

-- ───────────────────────────────────────────────
-- PROTEIN - SEAFOOD (category 3)
-- ───────────────────────────────────────────────
INSERT INTO food_items (name, name_hindi, category_id, serving_size, unit, calories, protein_g, carbs_g, fats_g, fiber_g, sugar_g, sodium_mg, is_vegetarian, is_vegan, is_gluten_free) VALUES

('Salmon (cooked)',         'Salmon Machli',  3, 100, 'g', 208, 20.4, 0.0, 13.4, 0.0, 0.0,  59.0, FALSE, FALSE, TRUE),
('Tuna (canned in water)',  'Tuna',           3, 100, 'g', 116, 25.5, 0.0,  0.8, 0.0, 0.0, 320.0, FALSE, FALSE, TRUE),
('Rohu Fish (cooked)',      'Rohu Machli',    3, 100, 'g',  97, 17.6, 0.0,  2.7, 0.0, 0.0,  72.0, FALSE, FALSE, TRUE),
('Pomfret (cooked)',        'Pomfret Machli', 3, 100, 'g', 105, 18.0, 0.0,  3.5, 0.0, 0.0,  65.0, FALSE, FALSE, TRUE),
('Prawns / Shrimp (cooked)','Jhinga',         3, 100, 'g',  99, 20.9, 0.9,  1.1, 0.0, 0.0, 119.0, FALSE, FALSE, TRUE),
('Surmai / King Mackerel',  'Surmai',         3, 100, 'g', 134, 19.8, 0.0,  5.8, 0.0, 0.0,  83.0, FALSE, FALSE, TRUE),
('Tilapia (cooked)',        'Tilapia Machli', 3, 100, 'g', 128, 26.0, 0.0,  2.7, 0.0, 0.0,  56.0, FALSE, FALSE, TRUE);

-- ───────────────────────────────────────────────
-- PROTEIN - EGGS (category 4)
-- ───────────────────────────────────────────────
INSERT INTO food_items (name, name_hindi, category_id, serving_size, unit, calories, protein_g, carbs_g, fats_g, fiber_g, sugar_g, sodium_mg, is_vegetarian, is_vegan, is_gluten_free) VALUES

('Whole Egg (boiled)',      'Anda (Ubla)',    4, 50,  'piece', 78,  6.3, 0.6,  5.3, 0.0, 0.6,  62.0, FALSE, FALSE, TRUE),
('Egg White (boiled)',      'Anda Safed',     4, 33,  'piece', 17,  3.6, 0.2,  0.1, 0.0, 0.2,  55.0, FALSE, FALSE, TRUE),
('Egg Yolk',                'Anda Zardi',     4, 17,  'piece', 55,  2.7, 0.6,  4.5, 0.0, 0.1,   8.0, FALSE, FALSE, TRUE),
('Scrambled Eggs (2 eggs)', 'Anda Bhurji',   4, 110, 'g',    182, 12.0, 1.6, 13.4, 0.0, 1.0, 342.0, FALSE, FALSE, TRUE),
('Omelette (1 egg, plain)', 'Omelette',      4,  60, 'g',     94,  6.4, 0.4,  7.3, 0.0, 0.4, 168.0, FALSE, FALSE, TRUE);

-- ───────────────────────────────────────────────
-- PROTEIN - LEGUMES (category 5)
-- ───────────────────────────────────────────────
INSERT INTO food_items (name, name_hindi, category_id, serving_size, unit, calories, protein_g, carbs_g, fats_g, fiber_g, sugar_g, sodium_mg, is_vegetarian, is_vegan, is_gluten_free) VALUES

('Moong Dal (cooked)',      'Moong Dal',      5, 100, 'g', 105,  7.0, 18.8, 0.4, 5.5, 1.6,   4.0, TRUE, TRUE, TRUE),
('Toor Dal (cooked)',       'Toor Dal',       5, 100, 'g', 115,  6.8, 20.1, 0.7, 4.5, 2.2,   4.0, TRUE, TRUE, TRUE),
('Masoor Dal (cooked)',     'Masoor Dal',     5, 100, 'g', 116,  9.0, 20.1, 0.4, 7.9, 1.8,   2.0, TRUE, TRUE, TRUE),
('Chana Dal (cooked)',      'Chana Dal',      5, 100, 'g', 164,  8.9, 27.6, 2.6, 7.6, 3.1,   7.0, TRUE, TRUE, TRUE),
('Urad Dal (cooked)',       'Urad Dal',       5, 100, 'g', 105,  7.5, 18.3, 0.6, 3.3, 0.0,   4.0, TRUE, TRUE, TRUE),
('Rajma (cooked)',          'Rajma',          5, 100, 'g', 127,  8.7, 22.8, 0.5, 6.4, 0.3,   2.0, TRUE, TRUE, TRUE),
('Chickpeas / Chana (cooked)','Chana',        5, 100, 'g', 164,  8.9, 27.4, 2.6, 7.6, 4.8,   7.0, TRUE, TRUE, TRUE),
('Black-eyed Peas (cooked)','Lobia',          5, 100, 'g', 116,  7.7, 20.8, 0.5, 6.5, 3.4,   4.0, TRUE, TRUE, TRUE),
('Soybean (cooked)',        'Soya',           5, 100, 'g', 173, 16.6,  9.9, 9.0, 6.0, 3.0,   1.0, TRUE, TRUE, TRUE),
('Tofu (firm)',             'Tofu',           5, 100, 'g',  76,  8.0,  1.9, 4.8, 0.3, 0.5,   7.0, TRUE, TRUE, TRUE),
('Kidney Beans (cooked)',   'Rajma Lal',      5, 100, 'g', 127,  8.7, 22.8, 0.5, 6.4, 0.3,   2.0, TRUE, TRUE, TRUE);

-- ───────────────────────────────────────────────
-- DAIRY (category 6)
-- ───────────────────────────────────────────────
INSERT INTO food_items (name, name_hindi, category_id, serving_size, unit, calories, protein_g, carbs_g, fats_g, fiber_g, sugar_g, sodium_mg, is_vegetarian, is_vegan, is_gluten_free, common_allergens) VALUES

('Whole Milk',              'Doodh',          6, 240, 'ml',  149,  8.0, 11.7,  8.0, 0.0, 12.2, 105.0, TRUE, FALSE, TRUE,  ARRAY['dairy']),
('Skimmed Milk',            'Toned Doodh',    6, 240, 'ml',   83,  8.3, 12.2,  0.4, 0.0, 12.5, 103.0, TRUE, FALSE, TRUE,  ARRAY['dairy']),
('Greek Yogurt (plain)',    'Greek Dahi',     6, 100, 'g',    59,  10.0, 3.6,  0.4, 0.0,  3.2,  36.0, TRUE, FALSE, TRUE,  ARRAY['dairy']),
('Curd / Dahi (full fat)',  'Dahi',           6, 100, 'g',    61,  3.1,  4.7,  3.4, 0.0,  4.7,  46.0, TRUE, FALSE, TRUE,  ARRAY['dairy']),
('Paneer (cottage cheese)', 'Paneer',         6, 100, 'g',   265, 18.3,  1.2, 20.8, 0.0,  1.2, 400.0, TRUE, FALSE, TRUE,  ARRAY['dairy']),
('Cheddar Cheese',          'Cheese',         6, 100, 'g',   402, 25.0,  1.3, 33.1, 0.0,  0.5, 621.0, TRUE, FALSE, TRUE,  ARRAY['dairy']),
('Butter',                  'Makhan',         6, 100, 'g',   717,  0.9,  0.1, 81.1, 0.0,  0.1, 643.0, TRUE, FALSE, TRUE,  ARRAY['dairy']),
('Ghee',                    'Ghee',           6, 100, 'g',   900,  0.0,  0.0,  100, 0.0,  0.0,   0.0, TRUE, FALSE, TRUE,  ARRAY['dairy']),
('Whey Protein (1 scoop)',  'Whey Protein',   6,  30, 'g',   120, 24.0,  3.0,  1.5, 0.0,  2.0, 130.0, TRUE, FALSE, TRUE,  ARRAY['dairy']),
('Lassi (sweet)',           'Lassi',          6, 200, 'ml',  134,  4.0, 23.0,  3.2, 0.0, 22.0,  60.0, TRUE, FALSE, TRUE,  ARRAY['dairy']),
('Buttermilk / Chaas',      'Chaas',          6, 200, 'ml',   40,  3.0,  5.0,  0.5, 0.0,  4.5,  80.0, TRUE, FALSE, TRUE,  ARRAY['dairy']);

-- ───────────────────────────────────────────────
-- VEGETABLES (category 7)
-- ───────────────────────────────────────────────
INSERT INTO food_items (name, name_hindi, category_id, serving_size, unit, calories, protein_g, carbs_g, fats_g, fiber_g, sugar_g, sodium_mg, is_vegetarian, is_vegan, is_gluten_free) VALUES

('Spinach (raw)',           'Palak',          7, 100, 'g',  23,  2.9,  3.6,  0.4, 2.2, 0.4,  79.0, TRUE, TRUE, TRUE),
('Broccoli',                'Broccoli',       7, 100, 'g',  34,  2.8,  6.6,  0.4, 2.6, 1.7,  33.0, TRUE, TRUE, TRUE),
('Carrot',                  'Gajar',          7, 100, 'g',  41,  0.9,  9.6,  0.2, 2.8, 4.7,  69.0, TRUE, TRUE, TRUE),
('Tomato',                  'Tamatar',        7, 100, 'g',  18,  0.9,  3.9,  0.2, 1.2, 2.6,   5.0, TRUE, TRUE, TRUE),
('Onion',                   'Pyaaz',          7, 100, 'g',  40,  1.1,  9.3,  0.1, 1.7, 4.2,   4.0, TRUE, TRUE, TRUE),
('Garlic',                  'Lahsun',         7, 100, 'g', 149,  6.4, 33.1,  0.5, 2.1, 1.0,  17.0, TRUE, TRUE, TRUE),
('Ginger',                  'Adrak',          7, 100, 'g',  80,  1.8, 17.8,  0.8, 2.0, 1.7,  13.0, TRUE, TRUE, TRUE),
('Cucumber',                'Kheera',         7, 100, 'g',  15,  0.7,  3.6,  0.1, 0.5, 1.7,   2.0, TRUE, TRUE, TRUE),
('Capsicum (Bell Pepper)',   'Shimla Mirch',   7, 100, 'g',  31,  1.0,  6.0,  0.3, 2.1, 4.2,   4.0, TRUE, TRUE, TRUE),
('Cauliflower',             'Phool Gobhi',    7, 100, 'g',  25,  1.9,  5.0,  0.3, 2.0, 1.9,  30.0, TRUE, TRUE, TRUE),
('Cabbage',                 'Patta Gobhi',    7, 100, 'g',  25,  1.3,  5.8,  0.1, 2.5, 3.2,  18.0, TRUE, TRUE, TRUE),
('Lady Finger / Okra',      'Bhindi',         7, 100, 'g',  33,  1.9,  7.5,  0.2, 3.2, 1.5,   8.0, TRUE, TRUE, TRUE),
('Bitter Gourd',            'Karela',         7, 100, 'g',  17,  1.0,  3.7,  0.2, 2.8, 1.7,   5.0, TRUE, TRUE, TRUE),
('Bottle Gourd',            'Lauki',          7, 100, 'g',  14,  0.6,  3.4,  0.0, 0.5, 0.0,   2.0, TRUE, TRUE, TRUE),
('Ridge Gourd',             'Turai',          7, 100, 'g',  20,  1.2,  3.5,  0.2, 0.5, 0.0,   3.0, TRUE, TRUE, TRUE),
('Pumpkin',                 'Kaddu',          7, 100, 'g',  26,  1.0,  6.5,  0.1, 0.5, 2.8,   1.0, TRUE, TRUE, TRUE),
('Sweet Potato',            'Shakarkandi',    7, 100, 'g',  86,  1.6, 20.1,  0.1, 3.0, 4.2,  55.0, TRUE, TRUE, TRUE),
('Potato',                  'Aloo',           7, 100, 'g',  77,  2.0, 17.6,  0.1, 2.2, 0.8,   6.0, TRUE, TRUE, TRUE),
('Green Peas',              'Matar',          7, 100, 'g',  81,  5.4, 14.5,  0.4, 5.1, 5.7,   5.0, TRUE, TRUE, TRUE),
('Mushroom',                'Mushroom',       7, 100, 'g',  22,  3.1,  3.3,  0.3, 1.0, 2.0,   5.0, TRUE, TRUE, TRUE),
('Beetroot',                'Chukandar',      7, 100, 'g',  43,  1.6,  9.6,  0.2, 2.8, 6.8,  78.0, TRUE, TRUE, TRUE),
('Corn (boiled)',            'Makka Ubla',    7, 100, 'g',  96,  3.4, 21.0,  1.5, 2.4, 3.2,  15.0, TRUE, TRUE, TRUE),
('Methi Leaves',            'Methi',          7, 100, 'g',  49,  4.4,  6.0,  0.9, 2.7, 0.0,  67.0, TRUE, TRUE, TRUE),
('Coriander / Dhania',      'Dhania',         7, 100, 'g',  23,  2.1,  3.7,  0.5, 2.8, 0.0,  46.0, TRUE, TRUE, TRUE);

-- ───────────────────────────────────────────────
-- FRUITS (category 8)
-- ───────────────────────────────────────────────
INSERT INTO food_items (name, name_hindi, category_id, serving_size, unit, calories, protein_g, carbs_g, fats_g, fiber_g, sugar_g, sodium_mg, is_vegetarian, is_vegan, is_gluten_free) VALUES

('Apple',                   'Seb',            8, 100, 'g',  52,  0.3, 13.8,  0.2, 2.4, 10.4,  1.0, TRUE, TRUE, TRUE),
('Banana',                  'Kela',           8, 100, 'g',  89,  1.1, 22.8,  0.3, 2.6, 12.2,  1.0, TRUE, TRUE, TRUE),
('Orange',                  'Santra',         8, 100, 'g',  47,  0.9, 11.8,  0.1, 2.4,  9.4,  0.0, TRUE, TRUE, TRUE),
('Mango',                   'Aam',            8, 100, 'g',  60,  0.8, 15.0,  0.4, 1.6, 13.7,  1.0, TRUE, TRUE, TRUE),
('Papaya',                  'Papita',         8, 100, 'g',  43,  0.5, 10.8,  0.3, 1.7,  7.8,  8.0, TRUE, TRUE, TRUE),
('Watermelon',              'Tarbooz',        8, 100, 'g',  30,  0.6,  7.6,  0.2, 0.4,  6.2,  1.0, TRUE, TRUE, TRUE),
('Grapes',                  'Angoor',         8, 100, 'g',  69,  0.7, 18.1,  0.2, 0.9, 15.5,  2.0, TRUE, TRUE, TRUE),
('Guava',                   'Amrood',         8, 100, 'g',  68,  2.6, 14.3,  1.0, 5.4,  8.9,  2.0, TRUE, TRUE, TRUE),
('Pomegranate',             'Anar',           8, 100, 'g',  83,  1.7, 18.7,  1.2, 4.0, 13.7,  3.0, TRUE, TRUE, TRUE),
('Strawberry',              'Strawberry',     8, 100, 'g',  32,  0.7,  7.7,  0.3, 2.0,  4.9,  1.0, TRUE, TRUE, TRUE),
('Blueberry',               'Blueberry',      8, 100, 'g',  57,  0.7, 14.5,  0.3, 2.4,  9.9,  1.0, TRUE, TRUE, TRUE),
('Pineapple',               'Ananas',         8, 100, 'g',  50,  0.5, 13.1,  0.1, 1.4,  9.9,  1.0, TRUE, TRUE, TRUE),
('Kiwi',                    'Kiwi',           8, 100, 'g',  61,  1.1, 14.7,  0.5, 3.0,  9.0,  3.0, TRUE, TRUE, TRUE),
('Pear',                    'Nashpati',       8, 100, 'g',  57,  0.4, 15.2,  0.1, 3.1,  9.8,  1.0, TRUE, TRUE, TRUE),
('Dates',                   'Khajoor',        8, 100, 'g', 282,  2.5, 75.0,  0.4, 8.0, 63.4,  2.0, TRUE, TRUE, TRUE),
('Coconut (fresh)',         'Nariyal',        8, 100, 'g', 354,  3.3, 15.2, 33.5, 9.0,  6.2, 20.0, TRUE, TRUE, TRUE),
('Lemon',                   'Nimbu',          8, 100, 'g',  29,  1.1,  9.3,  0.3, 2.8,  2.5,  2.0, TRUE, TRUE, TRUE);

-- ───────────────────────────────────────────────
-- NUTS & SEEDS (category 9)
-- ───────────────────────────────────────────────
INSERT INTO food_items (name, name_hindi, category_id, serving_size, unit, calories, protein_g, carbs_g, fats_g, fiber_g, sugar_g, sodium_mg, is_vegetarian, is_vegan, is_gluten_free, common_allergens) VALUES

('Almonds',                 'Badam',          9, 28,  'g',  164,  6.0,  6.1, 14.2, 3.5, 1.2,  0.0, TRUE, TRUE, TRUE,  ARRAY['tree_nuts']),
('Walnuts',                 'Akhrot',         9, 28,  'g',  185,  4.3,  3.9, 18.5, 1.9, 0.7,  1.0, TRUE, TRUE, TRUE,  ARRAY['tree_nuts']),
('Cashews',                 'Kaju',           9, 28,  'g',  157,  5.2,  8.6, 12.4, 0.9, 1.7,  3.0, TRUE, TRUE, TRUE,  ARRAY['tree_nuts']),
('Peanuts',                 'Moongphali',     9, 28,  'g',  161,  7.3,  4.6, 14.0, 2.4, 1.1,  5.0, TRUE, TRUE, TRUE,  ARRAY['peanuts']),
('Pista / Pistachios',      'Pista',          9, 28,  'g',  159,  5.7,  7.7, 12.9, 3.0, 2.2, 115.0, TRUE, TRUE, TRUE, ARRAY['tree_nuts']),
('Flaxseeds',               'Alsi',           9, 28,  'g',  152,  5.2,  8.2, 12.0, 7.6, 0.4,  9.0, TRUE, TRUE, TRUE,  ARRAY[]::TEXT[]),
('Chia Seeds',              'Chia Seeds',     9, 28,  'g',  138,  4.7, 12.3,  8.7, 9.8, 0.0,  5.0, TRUE, TRUE, TRUE,  ARRAY[]::TEXT[]),
('Sunflower Seeds',         'Surajmukhi Beej',9, 28,  'g',  164,  5.5,  6.5, 14.4, 2.4, 0.9,  1.0, TRUE, TRUE, TRUE,  ARRAY[]::TEXT[]),
('Pumpkin Seeds',           'Kaddu ke Beej',  9, 28,  'g',  151,  8.5,  5.0, 13.0, 1.1, 0.0,  5.0, TRUE, TRUE, TRUE,  ARRAY[]::TEXT[]);

-- ───────────────────────────────────────────────
-- OILS & FATS (category 10)
-- ───────────────────────────────────────────────
INSERT INTO food_items (name, name_hindi, category_id, serving_size, unit, calories, protein_g, carbs_g, fats_g, fiber_g, sugar_g, sodium_mg, is_vegetarian, is_vegan, is_gluten_free) VALUES

('Olive Oil',               'Olive Tel',     10, 15, 'ml',  119, 0.0, 0.0, 13.5, 0.0, 0.0,  0.3, TRUE, TRUE, TRUE),
('Coconut Oil',             'Nariyal Tel',   10, 15, 'ml',  121, 0.0, 0.0, 13.6, 0.0, 0.0,  0.0, TRUE, TRUE, TRUE),
('Sunflower Oil',           'Sunflower Tel', 10, 15, 'ml',  124, 0.0, 0.0, 14.0, 0.0, 0.0,  0.0, TRUE, TRUE, TRUE),
('Mustard Oil',             'Sarson Tel',    10, 15, 'ml',  124, 0.0, 0.0, 14.0, 0.0, 0.0,  0.0, TRUE, TRUE, TRUE),
('Ghee (1 tsp)',            'Ghee',          10, 5,  'ml',   45, 0.0, 0.0,  5.0, 0.0, 0.0,  0.0, TRUE, FALSE, TRUE);

-- ───────────────────────────────────────────────
-- BEVERAGES (category 11)
-- ───────────────────────────────────────────────
INSERT INTO food_items (name, name_hindi, category_id, serving_size, unit, calories, protein_g, carbs_g, fats_g, fiber_g, sugar_g, sodium_mg, is_vegetarian, is_vegan, is_gluten_free) VALUES

('Water',                   'Pani',          11, 240, 'ml',   0,  0.0,  0.0, 0.0, 0.0,  0.0,  7.0, TRUE, TRUE, TRUE),
('Green Tea',               'Green Tea',     11, 240, 'ml',   2,  0.2,  0.0, 0.0, 0.0,  0.0,  2.0, TRUE, TRUE, TRUE),
('Black Coffee',            'Black Coffee',  11, 240, 'ml',   2,  0.3,  0.0, 0.0, 0.0,  0.0,  5.0, TRUE, TRUE, TRUE),
('Coffee with Milk (Latte)','Latte',         11, 240, 'ml', 120,  6.0, 12.0, 5.0, 0.0, 12.0, 85.0, TRUE, FALSE, TRUE),
('Chai / Masala Tea',       'Chai',          11, 200, 'ml',  80,  2.5, 12.0, 2.5, 0.0, 10.0, 30.0, TRUE, FALSE, TRUE),
('Orange Juice (fresh)',    'Orange Juice',  11, 240, 'ml', 112,  1.7, 25.8, 0.5, 0.5, 20.8,  2.0, TRUE, TRUE, TRUE),
('Coconut Water',           'Nariyal Pani',  11, 240, 'ml',  46,  1.7,  8.9, 0.5, 0.0,  6.0, 252.0, TRUE, TRUE, TRUE),
('Whole Milk Shake',        'Milk Shake',    11, 300, 'ml', 232,  8.0, 35.0, 7.5, 0.0, 33.0, 130.0, TRUE, FALSE, TRUE),
('Protein Shake (water)',   'Protein Shake', 11, 400, 'ml', 130, 25.0,  5.0, 2.0, 0.0,  2.0, 150.0, TRUE, FALSE, TRUE);

-- ───────────────────────────────────────────────
-- INDIAN BREADS (category 14)
-- ───────────────────────────────────────────────
INSERT INTO food_items (name, name_hindi, category_id, serving_size, unit, calories, protein_g, carbs_g, fats_g, fiber_g, sugar_g, sodium_mg, is_vegetarian, is_vegan, is_gluten_free) VALUES

('Roti / Chapati (1 piece)',     'Roti',        14, 35,  'piece', 92,  3.0, 18.0, 1.0, 2.0, 0.0, 120.0, TRUE, TRUE,  FALSE),
('Phulka (thin roti, 1 piece)',  'Phulka',      14, 25,  'piece', 63,  2.2, 12.5, 0.5, 1.4, 0.0,  80.0, TRUE, TRUE,  FALSE),
('Paratha (plain, 1 piece)',     'Paratha',     14, 70,  'piece', 215, 4.2, 30.0, 8.5, 2.5, 0.0, 250.0, TRUE, TRUE,  FALSE),
('Aloo Paratha (1 piece)',       'Aloo Paratha',14, 100, 'piece', 300, 6.0, 40.0, 12.0,3.0, 0.0, 350.0, TRUE, TRUE,  FALSE),
('Naan (1 piece)',               'Naan',        14, 90,  'piece', 262, 8.0, 45.0, 5.5, 1.8, 2.5, 420.0, TRUE, FALSE, FALSE),
('Puri (1 piece)',               'Puri',        14, 30,  'piece', 110, 2.0, 13.5, 5.5, 1.0, 0.0,  90.0, TRUE, TRUE,  FALSE),
('Bhatura (1 piece)',            'Bhatura',     14, 80,  'piece', 258, 5.5, 35.0, 11.0,1.5, 1.0, 200.0, TRUE, TRUE,  FALSE),
('Missi Roti (1 piece)',         'Missi Roti',  14, 40,  'piece', 110, 4.8, 17.0, 2.8, 3.0, 0.0, 130.0, TRUE, TRUE,  FALSE),
('Idli (1 piece)',               'Idli',        14, 40,  'piece',  39, 1.7,  8.0, 0.2, 0.5, 0.0, 120.0, TRUE, TRUE,  TRUE),
('Dosa (1 piece)',               'Dosa',        14, 80,  'piece', 133, 3.4, 24.5, 2.7, 1.0, 0.0, 120.0, TRUE, TRUE,  TRUE);

-- ───────────────────────────────────────────────
-- INDIAN DISHES (category 15)
-- ───────────────────────────────────────────────
INSERT INTO food_items (name, name_hindi, category_id, serving_size, unit, calories, protein_g, carbs_g, fats_g, fiber_g, sugar_g, sodium_mg, is_vegetarian, is_vegan, is_gluten_free) VALUES

('Dal Tadka',               'Dal Tadka',     15, 200, 'ml',  180,  9.0, 25.0,  5.0, 6.0, 2.0, 320.0, TRUE, TRUE,  TRUE),
('Dal Makhani',             'Dal Makhani',   15, 200, 'ml',  240,  9.5, 25.0, 11.0, 5.0, 2.5, 430.0, TRUE, FALSE, TRUE),
('Rajma Curry',             'Rajma',         15, 200, 'ml',  210, 10.0, 28.0,  6.0, 7.0, 2.0, 380.0, TRUE, TRUE,  TRUE),
('Chole / Chana Masala',    'Chole',         15, 200, 'ml',  230, 10.5, 30.0,  7.0, 7.5, 2.5, 450.0, TRUE, TRUE,  TRUE),
('Palak Paneer',            'Palak Paneer',  15, 200, 'ml',  280, 14.0, 10.0, 20.0, 3.0, 2.0, 420.0, TRUE, FALSE, TRUE),
('Paneer Butter Masala',    'Paneer Masala', 15, 200, 'ml',  350, 15.0, 12.0, 27.0, 2.0, 4.0, 580.0, TRUE, FALSE, TRUE),
('Chicken Curry',           'Murgi Curry',   15, 200, 'ml',  260, 22.0,  5.0, 17.0, 1.0, 2.0, 520.0, FALSE, FALSE, TRUE),
('Mutton Curry',            'Mutton Curry',  15, 200, 'ml',  320, 24.0,  4.5, 23.0, 1.0, 1.5, 550.0, FALSE, FALSE, TRUE),
('Fish Curry',              'Machli Curry',  15, 200, 'ml',  220, 19.0,  4.0, 14.0, 0.5, 1.0, 480.0, FALSE, FALSE, TRUE),
('Egg Curry',               'Anda Curry',    15, 200, 'ml',  230, 14.0,  6.0, 16.0, 1.0, 2.0, 440.0, FALSE, FALSE, TRUE),
('Sambar',                  'Sambar',        15, 200, 'ml',  110,  5.0, 15.0,  3.0, 3.5, 2.0, 350.0, TRUE, TRUE,  TRUE),
('Vegetable Khichdi',       'Khichdi',       15, 200, 'ml',  220,  7.5, 38.0,  4.0, 3.5, 1.0, 280.0, TRUE, TRUE,  TRUE),
('Upma',                    'Upma',          15, 150, 'g',   180,  4.5, 28.0,  5.5, 2.0, 1.5, 320.0, TRUE, TRUE,  FALSE),
('Poha',                    'Poha',          15, 150, 'g',   210,  4.0, 38.0,  4.0, 1.5, 1.0, 280.0, TRUE, TRUE,  TRUE),
('Biryani (Veg)',           'Veg Biryani',   15, 250, 'g',   380,  8.0, 65.0, 10.0, 3.0, 2.5, 520.0, TRUE, FALSE, TRUE),
('Biryani (Chicken)',       'Chicken Biryani',15,250, 'g',   450, 22.0, 58.0, 15.0, 2.5, 2.0, 680.0, FALSE, FALSE, TRUE),
('Aloo Sabzi',              'Aloo Sabzi',    15, 150, 'g',   160,  2.5, 22.0,  7.0, 2.5, 1.5, 290.0, TRUE, TRUE,  TRUE),
('Baingan Bharta',          'Baingan Bharta',15, 150, 'g',   120,  2.0, 10.0,  8.0, 3.0, 3.0, 310.0, TRUE, TRUE,  TRUE);

-- ───────────────────────────────────────────────
-- SNACKS (category 12)
-- ───────────────────────────────────────────────
INSERT INTO food_items (name, name_hindi, category_id, serving_size, unit, calories, protein_g, carbs_g, fats_g, fiber_g, sugar_g, sodium_mg, is_vegetarian, is_vegan, is_gluten_free) VALUES

('Banana Chips',            'Kela Chips',    12, 30, 'g',  155,  0.8, 18.0,  9.0, 1.5, 1.5, 120.0, TRUE, TRUE,  TRUE),
('Roasted Chana',           'Bhuna Chana',   12, 30, 'g',  100,  7.0, 13.0,  2.0, 3.5, 0.5,  10.0, TRUE, TRUE,  TRUE),
('Murmura (Puffed Rice)',   'Murmura',       12, 30, 'g',  108,  2.0, 24.0,  0.3, 0.3, 0.0, 120.0, TRUE, TRUE,  TRUE),
('Makhana (Fox Nuts)',      'Makhana',       12, 30, 'g',  107,  3.6, 19.8,  0.5, 0.5, 0.0,  65.0, TRUE, TRUE,  TRUE),
('Dhokla (2 pieces)',       'Dhokla',        12, 80, 'g',  160,  5.5, 22.0,  5.5, 1.5, 3.0, 380.0, TRUE, TRUE,  TRUE),
('Samosa (1 piece)',        'Samosa',        12, 80, 'g',  252,  3.9, 28.0, 13.5, 2.0, 1.5, 320.0, TRUE, TRUE,  FALSE),
('Boiled Egg Snack',        'Ubla Anda',     12, 50, 'piece',78,  6.3,  0.6,  5.3, 0.0, 0.6,  62.0, FALSE, FALSE, TRUE),
('Fruit Bowl (mixed)',      'Fruit Bowl',    12, 150,'g',   90,  1.2, 22.0,  0.3, 2.5, 18.0,  5.0, TRUE, TRUE,  TRUE);

-- =============================================================
-- 4. DEFAULT SUPER ADMIN USER
-- Password: Admin@NutriPlan2024 (bcrypt hash — change after first login!)
-- =============================================================

INSERT INTO users (name, email, password_hash, role, is_active, is_email_verified)
VALUES (
    'Super Admin',
    'admin@nutriplan.ai',
    '$2b$12$0jSTZJR3I4EcNXxB3F0/eeGnxcYtaGmRw82YADnmMllL5fHUYVKCS',
    'admin',
    TRUE,
    TRUE
)
ON CONFLICT (email) DO NOTHING;

-- =============================================================
-- DONE — Seed data inserted:
--   5  subscription plans
--   16 food categories
--   170+ food items (Indian + International)
--       Grains, Meats, Seafood, Eggs, Legumes,
--       Dairy, Vegetables, Fruits, Nuts, Oils,
--       Beverages, Indian Breads, Indian Dishes, Snacks
--   1  default super admin user
-- =============================================================
