<#
vm_snaps.ps1
-John Taylor
Aug 20 2021

Check all VMs on a vCenter server for a snapshot. If a snapshot is found, send an email message.
How to exlude VMs that you expect to have snapshots, in the code below, search for: "VM-To-Exclude-1" and "VM-To-Exclude-2"

Dependencies: VMWare Power CLI module: https://docs.vmware.com/en/VMware-vSphere/7.0/com.vmware.esxi.install.doc/GUID-F02D0C2D-B226-4908-9E5C-2E783D41FE2D.html
See also: Save PSCredential in the file: https://stackoverflow.com/a/40029496

#>

# change these variables

$vCenter = "vcenterServer.example.com"
$email_server = "smtp.example.com"
$email_from = "alerts@example.com"
$email_to = "sysAdmin@example.com"
$email_subject = "VM snapshots detected"

# Nothing to change below this line

$vmware_module = "VMWare.PowerCli"
if (Get-Module -ListAvailable -Name $vmware_module ) {
    Import-Module $vmware_module 
} else {
    ""
    "Please install $vmware_module"
    "Instructions: https://docs.vmware.com/en/VMware-vSphere/7.0/com.vmware.esxi.install.doc/GUID-F02D0C2D-B226-4908-9E5C-2E783D41FE2D.html"
    ""
    "Or just run this command: Install-Module VMware.PowerCLI -Scope CurrentUser -AllowClobber"
    ""
    exit
}

$credential_file = "vm_snaps_credentials.xml"
if(-not (Test-Path $credential_file)) {
    ""
    "Crendential file does not exist: $credential_file"
    "Instructions: https://stackoverflow.com/a/40029496"
    "Hint: for the username, use this format: MyDomain\UserName"
    ""
    exit
}

Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false | Out-Null
$credential = Import-CliXml -Path $credential_file
"Connecting to vCenter server: $vCenter"
$result = Connect-VIServer -Server $vCenter -credential $credential
if( $result.Length -eq 0 ) {
    ""
    "Unable to connect to vCenter server: $vCenter"
    exit
}

# this file contains the email message to be sent, if VM snapshots are found
$output = "vm_snaps_email_msg.txt"
New-Item -type file $output -force | out-null

$success = $true
$snaps = Get-VM | Where-Object { -not $_.Name.StartsWith("VM-To-Exclude-1") -and -not $_.Name.StartsWith("VM-To-Exclude-2") } | Get-Snapshot | Select-Object vm,name,description,created, @{n="SizeGB"; e={[math]::Round($_.sizegb,2)}} | Format-Table -autosize
if( $snaps.length -gt 0) {
    $snaplist = $snaps | out-string
    add-content $output ""
    add-content $output "VMs with Snapshots"
    add-content $output ""
    add-content $output $snaplist
    $success = $false
} else {
    add-content $output ""
    add-content $output "No VM Snapshots exist"
}
Disconnect-VIServer -Confirm:$false

if ($success) {
    "No VMs with snapshots were found"
    exit
} else {
    ""
    "Sending warning email: $email_subject"
    ""
    $body = "<pre>"
    $temp = get-content $output
    foreach( $line in $temp ) {
        $body += "$line `r`n"
    }
    $body += "</pre> `r`n"

    $smtp = new-object Net.Mail.SmtpClient($email_server)
    $message = New-Object System.Net.Mail.Mailmessage $email_from, $email_to, $email_subject, $body
    $message.IsBodyHTML = $true
    $smtp.Send($message)
    ""
    ""
    $body
}
