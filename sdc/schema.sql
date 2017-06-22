
drop table if exists files;
create table if not exists files (
    id                   integer primary key autoincrement,
    section              varchar(256) collate nocase,
    device_name          varchar(256) collate nocase,
    device_type          varchar(256) collate nocase,
    username             varchar(64) collate nocase,
    ip                   varchar(256) collate nocase,
    port                 integer not null default 22,
    config_fname         varchar(1024) collate nocase,
    config_sha1          char(40),
    config_sha256        char(64),
    config_fsize         int not null default 0,
    db_insert_date       timestamp,
    run_time             timestamp,
    same_as_prev_cfg     int not null default 0

    constraint section_len check( length(section) >= 2 and length(section) <= 256),
    constraint device_name_len check( length(device_name) >= 2 and length(device_name) <= 256),
    constraint username_len check( length(username) >= 2 and length(username) <= 64),
    constraint device_type_len check( length(device_type) >= 2 and length(device_type) <= 256),
    constraint ip_len check( length(ip) >= 2 and length(ip) <= 256),
    constraint port_range check (port >= 1 and port <=65535),
    constraint config_fname check( length(config_fname) >=2 and length(config_fname) <= 1024),
    constraint config_sha1 check( length(config_sha1) == 40),
    constraint config_fsize check(config_fsize > 0),
    constraint did_date check( db_insert_date >= '2017-06-19' ),
    --
    constraint date_year check( cast(substr(db_insert_date,1,4) as integer) >= 2017 and cast(substr(db_insert_date,1,4) as integer) <= 2099),
    constraint date_month check( cast(substr(db_insert_date,6,2) as integer) >= 1    and cast(substr(db_insert_date,6,2) as integer) <= 12),
    constraint date_day check( cast(substr(db_insert_date,9,2) as integer) >= 1    and cast(substr(db_insert_date,9,2) as integer) <= 31)
);
drop trigger if exists trig_files_did;
create trigger trig_files_did after insert on files
begin
    update files set db_insert_date = datetime('now','localtime') where rowid = new.rowid;
end;
