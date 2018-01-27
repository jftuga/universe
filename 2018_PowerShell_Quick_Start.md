
# 2018 PowerShell Quick Start

2018-01-27

## Basics

- ```Update-Help``` (run as admin): Download newest Help files from Internet
- ```Get-Alias –Definition target```: show all aliases that use or point to target
- To get a single property value: ```(Get-Process -PID $PID).Name```
- To search for command: ```Get-Command -Noun process```

### Misc

- to create a string containing a line of X's: ```$line = "x"*77```
- to change the Powershell window title: ```$host.UI.RawUI.WindowTitle = $host.UI.RawUI.WindowTitle ="PS Window @ " + (get-date -Format g)```

## History

- h -> Get-History
- r -> Invoke-History 
- ```Get-History | ? -Property Id -gt 190```
- ```Get-History | ? CommandLine -like "dir*"```
- ```h |? CommandLine -like dir*```
- to run the fifth command from history: ```r 5```

See also: https://blogs.technet.microsoft.com/heyscriptingguy/2011/01/18/use-powershell-history-to-speed-repetitive-commands/

## Get-Member

- Get-Member: Gets the type, properties and methods of an object.
- gm: a built-in alias to Get-Member
- object.GetType() will return this Powershell’s object type and base type

## PowerShell Objects

- Page 69-70:
- ```$obj = [PSCustomObject]@{ 'Some Name' = "My Value" }```


- Page 74:

```powershell
$obj = New-Object Object
$obj | Add-Member -Name Age -Value 45 -MemberType NoteProperty
```

- *Note:* a NoteProperty is: A property defined by a Name-Value pair

See also: https://docs.microsoft.com/en-us/dotnet/api/system.management.automation.psmembertypes

## ForEach-Object vs ForEach

- alias: % -> ForEach-Object
- When you are piping input into **ForEach**, it is the alias for **ForEach-Object**. But when you place **ForEach** at the beginning of the line, it is a Windows PowerShell statement.
- **ForEach-Object** is best used when sending data through the pipeline because it will continue streaming the objects to the next command in the pipeline.
- The **ForEach** statement loads all of the items up front into a collection before processing them one at a time. **ForEach-Object** expects the items to be streamed via the pipeline, thus lowering the memory requirements, but at the same time, taking a performance hit.
- **ForEach-Object** also allows us to specify Begin, Process, and End script blocks that we can use (similar to an advanced function) to set up our environment, process each item, and then do something (such as clean up at the end of the command).
    - In the -End section, you could then pass this to another cmdlet, such as Export-CSV
- **ForEach** is perfect if you have plenty of memory, want the best performance, and do not care about passing the output to another command via the pipeline.
- **ForEach-Object** (with its aliases % and **ForEach**) take input from the pipeline. Although it is slower to process everything, it gives you the benefit of **Begin**, **Process**, and **End** blocks. In addition, it allows you to stream the objects to another command via the pipeline.

See also: https://blogs.technet.microsoft.com/heyscriptingguy/2014/07/08/getting-to-know-foreach-and-foreach-object/

## Where-Object

- alias: ? -> Where-Object
- ```Where-Object [-Property] <String> [[-Value] <Object>]```
- ```Get-Process | ? -Property Id -lt 1000```

## Select-Object (pg. 77-78)

- alias: select -> Select-Object
- allow a subset of data to be returned
- more restrictive number of elements 
- smaller number of properties
- case insensitive for Property names
- ```get-process | select -Property naMe,cPu```
- ```get-process | select-object -Property Name, *MemOrY*```
- ```get-process | select-object -Property Name, *MemOrY* -Exclude *paged*, virtual*```
- ```get-process | select-object -Property Name -First 5```    #head
- ```get-process | select-object -Property Name -Last 5```     #tail
- ```get-process | select-object -Property Name -Skip 4 -First 1```   #return 5th item
- ```get-process | select-object -Property Name -Skip 2 –Last 1```   #return 3rd from end
- ```get-process | Select Name –Unique``` *vs.* ```get-process | Select Name```

## Sort-Object (pg. 79)

- alias: sort -> Sort-Object
- sorts by unicode sorting conventions, which are different than latin-1
- ```dir | sort LastWriteTime –Descending```
- ```get-process| sort ProcessName``` *vs.* ```get-process| sort ProcessName, Id```
- sort first column (Count) *Desceding*, and then second column (Name) *Ascending*: 
    - ```Sort-Object -Property @{Expression = {$_.Count}; Ascending = $false}, @{Expression= {$_.Name}; Ascending = $true}```

## Measure-Object

- ```6,9,3,9,2,5,8,4,8,5 | Measure-Object -Average -Sum -Minimum -Maximum```
- similar to *wc*: ```Get-Content .\test.txt | Measure-Object -Character -Line -Word```

## Group-Object

- Recommended: ```Group-Object -NoElement -CaseSensitive```

## Compare-Object

- To see all files that have the same name and length:

```powershell
$reference = Get-ChildItem C:\Windows\System32 -File
$difference = Get-ChildItem C:\Windows\SysWOW64 -File
Compare-Object $reference $difference -Property Name, Length -IncludeEqual -ExcludeDifferent
```

## Select-String

- alias: sls -> Select-String
- This is the PS version of grep and findstr
- Default search in not case-sensative
- To search all files in a single directory: ```dir | sls DiReCtoRY```

See also: https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/select-string

_____

## Out-GridView
- ```Get-History | Out-GridView -PassThru  | Invoke-Expression```
- ```Get-Process | Out-GridView -PassThru  | Invoke-Expression```
- ```Get-Command | Out-GridView -PassThru  | Get-Help –ShowWindow```
- ```Get-Help about* | Out-GridView  -PassThru |  Get-Help –ShowWindow```
- ```Powershell.exe -Command "Get-Service | Out-GridView -Wait"```

See also: https://mcpmag.com/articles/2016/02/17/creating-a-gui-using-out-gridview.aspx
_____

## $Profile => C:\Users\jftuga\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1

```powershell
function of($fname) { $input | Out-File -Encoding ascii $fname }

<#
pssus: PowerShell Sort => Unique => Sort
----------------------------------------
# of Items, Time(s), Time(m:s)
100000,  10,  0:10
200000,  26,  0:26
300000,  73,  1:13
500000, 222,  3:42

A much faster equivalent (500k rows in 3s; 8.5m rows in 52s):
gsort.exe -S 3000000 - | uniq.exe -c | gsort.exe -n -k1,1r -k2,2 -S 3000000
downloaded these EXEs from: https://github.com/bmatzelle/gow

#>
function pssus() {
     $input | Group-Object -NoElement -CaseSensitive | Sort-Object -Property @{Expression = {$_.Count}; Ascending = $false}, @{Expression= {$_.Name}; Ascending = $true} | Format-Table -AutoSize -HideTableHeaders
}

function Test-Elevated {
  $wid = [System.Security.Principal.WindowsIdentity]::GetCurrent()
  $prp = New-Object System.Security.Principal.WindowsPrincipal($wid)
  $adm = [System.Security.Principal.WindowsBuiltInRole]::Administrator
  $prp.IsInRole($adm)
}
```

## To Do

- help about_comparison_operators
- Export-Csv, ConvertTo-Csv (pg. 87-88)

