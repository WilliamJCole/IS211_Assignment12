drop table if exists students;
create table students (
  student_id integer primary key autoincrement,
  first_name text not null,
  last_name text not null
);

drop table if exists quizzes;
create table quizzes (
  quizz_id integer primary key autoincrement,
  subject text not null,
  questions text not null,
  date text not null
);

drop table if exists results;
create table results (
  student_id integer not null,
  quizz_id integer not null,
  score integer not null
);
