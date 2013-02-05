drop table linename;
CREATE TABLE "linename" (
        "dataownercode" VARCHAR(10) NOT NULL,
        "lineplanningnumber" VARCHAR(10) NOT NULL,
        "linename" VARCHAR(50),
         PRIMARY KEY ("dataownercode", "lineplanningnumber")
);

copy linename from '/home/projects/openebs/kv78turbo/linenames.csv' CSV;
update line as l set linename = (select linename from linename as n where l.lineplanningnumber = n.lineplanningnumber and l.dataownercode 
= n.dataownercode) where dataownercode||'|'||lineplanningnumber in (select dataownercode||'|'||lineplanningnumber from linename); 
