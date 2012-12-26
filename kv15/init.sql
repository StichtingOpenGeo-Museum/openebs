CREATE TABLE kv15_stopmessage (
DataOwnerCode VARCHAR(10) NOT NULL,
MessageCodeDate DATE NOT NULL,
MessageCodeNumber NUMERIC(4,0) NOT NULL,
MessagePriority VARCHAR(10) NOT NULL,
MessageType VARCHAR(10) NOT NULL,
MessageDurationType VARCHAR(10) NOT NULL,
MessageStartTime TIMESTAMP,
MessageEndTime TIMESTAMP,
MessageContent VARCHAR(255),
ReasonType NUMERIC(3,0),
SubReasonType VARCHAR(10),
ReasonContent VARCHAR(255),
EffectType NUMERIC(3,0),
SubEffectType VARCHAR(10),
EffectContent VARCHAR(255),
MeasureType NUMERIC(3,0),
SubMeasureType VARCHAR(10),
MeasureContent VARCHAR(255),
AdviceType NUMERIC(3,0),
SubAdviceType VARCHAR(10),
AdviceContent VARCHAR(255),
MessageTimeStamp TIMESTAMP NOT NULL,
Scenario VARCHAR(255),
PRIMARY KEY(DataOwnerCode, MessageCodeDate, MessageCodeNumber)
);

CREATE TABLE kv15_stopmessage_userstopcode (
DataOwnerCode VARCHAR(10) NOT NULL,
MessageCodeDate DATE NOT NULL,
MessageCodeNumber NUMERIC(4,0) NOT NULL,
UserStopCode VARCHAR(10) NOT NULL,
PRIMARY KEY(DataOwnerCode, MessageCodeDate, MessageCodeNumber, UserStopCode),
FOREIGN KEY(DataOwnerCode, MessageCodeDate, MessageCodeNumber) REFERENCES kv15_stopmessage
);

CREATE TABLE kv15_stopmessage_lineplanningnumber (
DataOwnerCode VARCHAR(10) NOT NULL,
MessageCodeDate DATE NOT NULL,
MessageCodeNumber NUMERIC(4,0) NOT NULL,
LinePlanningNumber VARCHAR(10) NOT NULL,
PRIMARY KEY(DataOwnerCode, MessageCodeDate, MessageCodeNumber, LinePlanningNumber),
FOREIGN KEY(DataOwnerCode, MessageCodeDate, MessageCodeNumber) REFERENCES kv15_stopmessage
);

CREATE TABLE kv15_schedule (
DataOwnerCode VARCHAR(10) NOT NULL,
MessageCodeDate DATE NOT NULL,
MessageCodeNumber NUMERIC(4,0) NOT NULL,
MessageStartTime TIMESTAMP,
MessageEndTime TIMESTAMP,
Weekdays SMALLINT,
PRIMARY KEY(DataOwnerCode, MessageCodeDate, MessageCodeNumber),
FOREIGN KEY(DataOwnerCode, MessageCodeDate, MessageCodeNumber) REFERENCES kv15_stopmessage
);

CREATE TABLE kv15_log (
DataOwnerCode VARCHAR(10) NOT NULL,
MessageCodeDate DATE NOT NULL,
MessageCodeNumber NUMERIC(4,0) NOT NULL,
Author VARCHAR(255),
Message TEXT,
PRIMARY KEY(DataOwnerCode, MessageCodeDate, MessageCodeNumber),
FOREIGN KEY(DataOwnerCode, MessageCodeDate, MessageCodeNumber) REFERENCES kv15_stopmessage
);
