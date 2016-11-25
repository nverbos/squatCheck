drop table if exists vibrationEvent;
create table vibrationEvent (
   source INTEGER,
   timeStamp INTEGER not null,
   dayOfWeek INTEGER not null,
   hour INTEGER not null,
   PRIMARY KEY (source, timestamp)
);
