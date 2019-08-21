
# 2018 PowerShell Quick Start

2018-01-27

## Basics

- ```Update-Help``` (run as admin): Download newest Help files from Internet
- ```Get-Alias –Definition target```: show all aliases that use or point to target
- To get a single property value: ```(Get-Process -PID $PID).Name```
- To search for command: ```Get-Command -Noun process```

### Modules

- to list some modules: 
- ```Get-Module -ListAvailable -Name VMware*```
- to update some modules:
- ```Update-Module VMware.*```
- 
- to find and install a modules:
- ```Find-Module -Name VMware.PowerCLI```
- ```Install-Module -Name VMware.PowerCLI -Scope CurrentUser```
- ```Get-Command -Module *VMWare*```

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

- ```$obj = [PSCustomObject]@{ 'Some Name' = "My Value" }```

- Example:

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

**Other ideas:**

Only use the **ForEach-Object** cmdlet if you are concerned about saving memory as follows:

- While the loop is running (because only one of the evaluated objects is loaded into memory at one time).
- If you want to start seeing output from your loop faster (because the cmdlet starts the loop the second it has the first object in a collection versus waiting to gather them all like - the **ForEach** construct).

You should use the **ForEach** loop construct in the following situations:

- If you want the loop to finish executing faster (notice I said finish faster and not start showing results faster).
- You want to Break/Continue out of the loop (because you can’t with the **ForEach-Object** cmdlet).

See also: https://blogs.technet.microsoft.com/heyscriptingguy/2014/05/18/weekend-scripter-powershell-speed-improvement-techniques/

## Where-Object

- alias: ? -> Where-Object
- ```Where-Object [-Property] <String> [[-Value] <Object>]```
- ```Get-Process | ? -Property Id -lt 1000```

## Select-Object

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

## Sort-Object

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
- Similar to *grep -n*: sls DiReCtoRY .\files.txt | select linenumber,line | ft -a

See also: https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/select-string

See also: https://communary.net/2014/11/10/grep-the-powershell-way/

_____

## Matching with Regular Expressions

- $a = "Cannot find an object with identity: 'jdoe' under: 'DC=uhs,DC=uga,DC=edu'."
- To get just *jdoe*: $a -match "'(.\*?)'" ; $matches[1]

See also: https://stackoverflow.com/questions/2988880/extricate-a-substring-using-powershell

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
# To create a new profile file:
# New-item –type file –force $profile

# of = Out-File
function of($fname) { $input | Out-File -Encoding ascii $fname }

# rf - Read-File (this is much faster than using Get-Content)
function rf($fname) { [System.IO.File]::ReadLines($fname) }

# GUI for Get-Help
function gh($topic) { Get-Help $topic | Out-GridView -PassThru | Get-Help -ShowWindow }

# directory, sort by date
function dirod($dname) { Get-ChildItem $dname | Sort-Object LastWriteTime | Select LastWriteTime, Length, Name | format-table @{ n="Modified";e={$_.LastWriteTime};align="right"}, @{n="Size";e={$_.Length.ToString("N0")};align="right" }, Name}

# directory, sort by size
function diros($dname) { Get-ChildItem -File $dname | Sort-Object Length | Select LastWriteTime, Length, Name | format-table @{ n="Modified";e={$_.LastWriteTime};align="right"}, @{n="Size";e={$_.Length.ToString("N0")};align="right" }, Name}

# reverse the output of a pipeline
function reverse { 
 $arr = @($input)
 [array]::reverse($arr)
 $arr
}

# similar to using 'set' under a cmd prompt
function env() { Get-ChildItem env: }

# An optimized C# version is here: 
# https://github.com/jftuga/universe/blob/master/freq.cs
# https://github.com/jftuga/universe/blob/master/bin/freq.exe
function Get-Frequency() {
    $freq = New-Object "System.Collections.Generic.Dictionary[string,int]"
    foreach( $line in $input) {
        $val = $freq[$line]
        if( $val ) {
            $freq[$line] = $val + 1
        } else {
            $freq.Add($line,1)
        }
    }
    $result = $freq.GetEnumerator() | Sort-Object -Property @{Expression = {$_.Value}; Ascending = $false}, @{Expression= {$_.Name}; Ascending = $true} | Format-Table -AutoSize -HideTableHeaders -Property Value, Key
    [System.GC]::Collect()
    $result
}

# Is PowerShell running as Admin?
function Test-Elevated {
  $wid = [System.Security.Principal.WindowsIdentity]::GetCurrent()
  $prp = New-Object System.Security.Principal.WindowsPrincipal($wid)
  $adm = [System.Security.Principal.WindowsBuiltInRole]::Administrator
  $prp.IsInRole($adm)
}

# Show all groups a user is a member of with GUI
function Get-Grps($username_id) {
  ([ADSISEARCHER]"samaccountname=$username_id").Findone().Properties.memberof -replace '^CN=([^,]+).+$','$1' | Sort-Object | select @{Name="Group Name";expression={$_}} | Out-GridView -Title $username_id
}

# Show all groups a user is a member
function Get-Grps2($username_id) {
  ([ADSISEARCHER]"samaccountname=$username_id").Findone().Properties.memberof -replace '^CN=([^,]+).+$','$1' | Sort-Object | select @{Name="Group Name";expression={$_}}
}

#######################################################################################################################################################################

# Search path for Import-Module
$env:PSModulePath = "$env:PSModulePath;$env:USERPROFILE\Documents\WindowsPowerShell\Modules"

# change windows title to: 'user@hostname date/time'  -or-  'user@hostname [DMIN] date/time'
$host.UI.RawUI.WindowTitle = $(if (Test-Elevated) {"[ADMIN] "} else {""}) + $env:username.ToLower() + "@" + $env:computername.ToLower() + " "  + (get-date -Format g)
```

## Before and After

```bash
gfind . -type d -maxdepth 2 | mawk -F \\ "{print $NF}" | sus
gfind . -type d -maxdepth 2 | mawk -F \\ "{print $NF}" | sus | head -10 | cut -c 9-
gfind . -type d -maxdepth 2 |  mawk -F \\ "{print $NF}" | sus | head -10 | cut -c 9- | mawk "{print 'mkdir ~'$0'~'}" | tr ~ \042 | cmd
# last line is 130 chars line
````

```powershell
(dir -Recurse -Depth 1 -Directory).Name | freq
((dir -Recurse -Depth 1 -Directory).Name | freq | select -First 10).Substring(8)
((dir -Recurse -Depth 1 -Directory).Name | freq | select -First 10).Substring(8) | foreach { mkdir $_ }
# last line is 103 chars long (21% shorter)
```

____

```cmd
dir /s/b/a-d > dir_sb.txt
```

```powershell
dir -Recurse -File | foreach { $_.FullName } | of .\dir_sb.txt
```

## Misc

```powershell
# find all .ps1 files that have been modified within the last 10 days
dir -Recurse -File *.ps1 | ? { $_.LastWriteTime -gt (Get-Date).AddDays(-10) }

# change the Import-Module search path
$env:PSModulePath = "$env:PSModulePath;$env:USERPROFILE\Documents\WindowsPowerShell\Modules"

# GUI front-end for Get-Help
function gh($topic) { Get-Help $topic | Out-GridView -PassThru | Get-Help -ShowWindow }

# Output File: save to a file in ascii to avoid BOM and unicode
function of($fname) { $input | Out-File -Encoding ascii $fname }

# much faster version of Get-Content (aka 'type')
function rf($fname) { [System.IO.File]::ReadLines($fname) }

# display all environment variables
function env() { Get-ChildItem env: }

# remove all subdirectories with no files in them
dir | foreach { $_.ToString(); ($a = dir $_ | measure -Line).Lines } | of lines.txt
# lines.txt now contains 2 lines per entry: (1) directory name; (2) number of files in that directory
(type .\lines.txt | sls -Pattern ^0 -Context 1) | foreach { $_.Context.PreContext} | sls "System Volume Information" -NotMatch | foreach { rmdir $_ }
# Explanation
# search for 0 at beginning of line and then get one line of context because we need the line before (aka PreContext) 
# to see what this means, run: 
(type .\lines.txt | sls -Pattern ^0 -Context 1)[1].Context
# end of remove all subdirectories

# Find all servers that are running the Trend Micro process
(Get-ADComputer -Filter 'Name -like "SVR*"').Name | % { Get-Process -ComputerName $_ | ? {$_.ProcessName -Contains "NTRTScan" } | ft -Property MachineName }

```



###
[What is Your top 5 powershell commands, which save you the most time](https://www.reddit.com/r/sysadmin/comments/au94n3/your_top_5_powershell_commands_which_save_you_the/)


## To Do

- help about_comparison_operators
- Export-Csv, ConvertTo-Csv

