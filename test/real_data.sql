INSERT INTO student
  (id,name,belt,active)
VALUES
  (0,'Robin','4 Dan',True),
  (1,'Alyssa Teo En Qi','11 Kyu',True),
  (2,'Teo Tze Teng','11 Kyu',True),
  (3,'Teo Tze Ki','11 Kyu',True),
  (4,'Tan Wei Dong','11 Kyu',True),
  (5,'Caius Tan Ju Yao','11 Kyu',True),
  (6,'Kalene Loi','11 Kyu',True),
  (7,'Queenie Valyn Chiang','12 Kyu',True),
  (8,'Chong Jun Hao','12 Kyu',True),
  (9,'Kaven Loi Kai Jun','12 Kyu',True),
  (10,'Brooklyn Huang','White',True),
  (11,'Liew Si Jia','White',True),
  (12,'Analee Po Shi En','White',True),
  (13,'Person13','0 Kyu',True);

INSERT INTO instructor
  (id,username)
  VALUES
  (0,'Robin123');

INSERT INTO dojo
  (id,name,location,instructor_id)
VALUES
  (0,'NSCC','Nee Soon Central CC', 0);

INSERT INTO enrollment
("studentActive",student_id, dojo_id)
VALUES
('True',0,0),
('True',1,0),
('True',2,0),
('True',3,0),
('True',4,0),
('True',5,0),
('True',6,0),
('True',7,0),
('True',8,0),
('True',9,0),
('True',10,0),
('True',11,0),
('True',12,0),
('True',13,0);