/****** Script for SelectTopNRows command from SSMS  ******/
delete temp
from temp
inner join
(SELECT [Column 0]
      ,[Column 1]
      ,[Column 2]
      ,[Column 3]
      ,[Column 4]
      ,[Column 5]
      ,[Column 6]
      ,[Column 7]
      ,[Column 8]
      ,[Column 9]
  FROM [BS_FONDOS_SBS_JUN2016].[dbo].[temp]
 WHERE [Column 7] IS NULL) as ttemp
 on temp.[Column 1] = ttemp.[Column 1]
 and temp.[Column 2] = ttemp.[Column 2]
 and temp.[Column 3] = ttemp.[Column 3]
 and temp.[Column 4] = ttemp.[Column 4]
 and temp.[Column 5] = ttemp.[Column 5]
 and temp.[Column 6] = ttemp.[Column 6]
 and temp.[Column 0] = 'Hotspot'

delete from temp where [Column 7] is null

delete from temp where [Column 8] = 0

select * from temp where [Column 0] = 'eVST-RS'
select * from temp where [Column 0] = 'Hotspot'

select * from temp where [Column 0] = 'eVST-RS' and [Column 5] = 5
select * from temp where [Column 0] = 'Hotspot' and [Column 5] = 5