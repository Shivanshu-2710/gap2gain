-- Seeded demo catalogue (no external integrations; all listings are fictional)
insert into skills (name) values
 ('Python'),('Data Entry'),('Excel'),('Content Writing'),('Social Media'),
 ('Graphic Design'),('Tutoring'),('Math'),('Translation'),('Customer Support'),('Video Editing')
on conflict do nothing;

insert into jobs (title, description, source, external_url, duration_minutes, setup_minutes, pay_amount, pay_verified, remote, flagged, flag_reason) values
 ('Spreadsheet data cleanup', 'Clean and standardise a 500-row customer sheet.', 'Seeded demo', 'https://example.com/jobs/1', 90, 10, 600, true, true, false, null),
 ('Math tutor (school students)', 'One-hour online session for a Class 9 student.', 'Seeded demo', 'https://example.com/jobs/2', 60, 5, 500, true, true, false, null),
 ('Blog post: 800 words on study habits', 'Write an original 800-word article.', 'Seeded demo', 'https://example.com/jobs/3', 120, 0, 900, true, true, false, null),
 ('Instagram captions (10 posts)', 'Short captions for a local cafe.', 'Seeded demo', 'https://example.com/jobs/4', 45, 0, 350, false, true, false, null),
 ('Python script: CSV report', 'Small script that summarises a CSV into a report.', 'Seeded demo', 'https://example.com/jobs/5', 150, 15, 1500, true, true, false, null),
 ('Weekend event helper (on-site)', 'Help set up a college fest stall.', 'Seeded demo', 'https://example.com/jobs/6', 240, 30, 800, false, false, false, null),
 ('Hindi to English translation (2 pages)', 'Translate two pages of product copy.', 'Seeded demo', 'https://example.com/jobs/7', 100, 0, 700, true, true, false, null),
 ('Earn 5000/day, registration fee required', 'Pay a fee first and earn guaranteed income.', 'Unknown', 'https://example.com/jobs/scam', 30, 0, 5000, false, true, true, 'Asks for upfront payment; unrealistic pay');

insert into job_skills (job_id, skill_id, importance)
select j.id, s.id, v.imp from (values
 ('Spreadsheet data cleanup','Excel',3),('Spreadsheet data cleanup','Data Entry',2),
 ('Math tutor (school students)','Math',3),('Math tutor (school students)','Tutoring',2),
 ('Blog post: 800 words on study habits','Content Writing',3),
 ('Instagram captions (10 posts)','Social Media',3),('Instagram captions (10 posts)','Content Writing',2),
 ('Python script: CSV report','Python',3),('Python script: CSV report','Excel',1),
 ('Weekend event helper (on-site)','Customer Support',2),
 ('Hindi to English translation (2 pages)','Translation',3)
) as v(title, skill, imp)
join jobs j on j.title = v.title
join skills s on s.name = v.skill;
