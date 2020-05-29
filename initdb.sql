create sequence if not exists reservation_seq start 1 increment 1;
create sequence if not exists spot_seq start 1 increment 1;

create table if not exists spot (
   name varchar(100) not null,
   id int8 not null not null,
   primary key (id)
);

create table if not exists reservation (
   spot_id int8 not null,
   reserved_at DATE not null,
   user_id int8 not null,
   id int8 not null not null,
   created_at timestamp not null,
   primary key (id)
);

alter table reservation
   add constraint reservation_spot
   foreign key (spot_id)
   references spot;

alter table reservation
   add constraint reservation_spot_id_reserved_at_unique unique (spot_id, reserved_at);

insert into spot(name, id) values ('Spot1', (nextval('spot_seq')));