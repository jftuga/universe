<#
github_backup.ps1
-John Taylor
01-06-2022
#>

$SOURCE_ROOT_FLDR="C:\Users\john\go\src\github.com"
$GH_USER="jftuga"
$DEST_ROOT_FLDR="k:\backups\github_backups"

# Delete all date folders older than this many days
# For example, this will delete all hourlies created subdirectories for all days older than $DaysBack
$DAYSBACK = "-14"

# end of user settings 

$source="$SOURCE_ROOT_FLDR\$GH_USER"
if( -not (Test-Path $source)) {
    "source folder does not exist: $source"
}

$now = get-date -format yyyyMMdd
$dest = "$DEST_ROOT_FLDR\$now"
if( -not (Test-Path $dest)) {
    "creating dest folder: $dest"
    mkdir $dest
}

$now = get-date -format yyyyMMdd.HHmmss
$archive = "$dest\gh_backup--$now.rar"
cd $SOURCE_ROOT_FLDR
rar a -m5 -mt8 -rr -s -x*exe -x*jar -x*lock -x*tmp -x*dll -x*avi -x*pack -x*site-packages* "-x*alpha.zip" "-x*find_similar_images\?.jpg" "-x*fzfmips64*" "-x*grafana-infinity-datasource\**svg" "-x*grafana-infinity-datasource\**map" $archive $GH_USER
attrib +r $archive
dir $archive

""
"Removing old directories (if any)..."
$CurrentDate = Get-Date
$DatetoDelete = $CurrentDate.AddDays($DAYSBACK)
$old = Get-ChildItem $DEST_ROOT_FLDR | Where-Object { $_.LastWriteTime -le $DatetoDelete }
$old
#Get-ChildItem $DEST_ROOT_FLDR | Where-Object { $_.LastWriteTime -le $DatetoDelete } | Remove-Item -recurse -force
$old | Remove-Item -recurse -force
