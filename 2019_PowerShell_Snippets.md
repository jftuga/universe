# 2019 PowerShell Snippets

2019-04-11

## Active Directory

- Find accounts whos passwords are about to expire.  In this scenario, mandatory password changes occur every 90 days.
- Find accounts that will expire in 10 days or less

```powershell

$limit = (Get-Date).AddDays(-80)
get-aduser -filter * -properties Name,PasswordNeverExpires,LastLogon,PasswordLastSet | ? { $_.passwordNeverExpires -eq $False -and $_.PasswordLastSet -lt $limit -and $_.LastLogon -gt 0 }  | sort PasswordLastSet | select Name,PasswordLastSet,@{N='LastLogin';E={[DateTime]::FromFileTime($_.LastLogon)}},PasswordNeverExpires


```

## Signing a PowerShell Script

```powershell

Set-AuthenticodeSignature .\MyScript.ps1 @(Get-ChildItem cert:\CurrentUser\My -codesign)[0]

```
