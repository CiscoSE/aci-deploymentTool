[cmdletbinding()]
param(
    [string]$apic,
    [string]$user='admin',
    [PSCredential]$cred=(get-credential -UserName $user),
    [string]$sourcefolder='.\sourceFolder\',
    [string]$processedFolder='.\processedFolder',
    [switch]$failsafe
)

function main {
    Param()
    getCookie    
}

function getCookie{
    param()
    $cookieResult = getData -data "<aaaUser name='admin' pwd='$($cred.GetNetworkCredential().password)' />" -urlPath '/api/aaaLogin.xml' 
    $cookieResult
}
function getData {
    param(
        $data='',
        $urlPath,
        $type='Post',
        $headers=@{'Content-Type'='application/xml'}    
    )
    $result = Invoke-WebRequest -uri "https://$($apic)$($urlPath)" -body "$($data)" -SkipCertificateCheck -Headers $Headers -Method Post 
    return $result
}
main