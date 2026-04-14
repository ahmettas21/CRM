# Izge Travel - AltÄ±n Deployment Script v1.0
# Bu script yereldeki kodlarÄ± push eder ve sunucuda doÄ\u011fru PIP yollarÄ±yla aktive eder.

Write-Host "â\u0130Å\u015flem BaÅ\u015flÄ±yor: Yerel Push..." -ForegroundColor Cyan
git add .
git commit -m "Deploy: Automated Update via Deploy Script"
git push origin main

Write-Host "Sunucuya BaÄ\u011flanÄ±lÄ±yor ve MatruÅ\u015fka KorumalÄ± Kurulum BaÅ\u015flatÄ±lÄ±yor..." -ForegroundColor Yellow

# Sunucuda Ã§alÄ±Å\u015facak komutlar dizisi
$cmd = @"
cd /home/frappe/bench/apps/izge_travel
git fetch origin main
git reset --hard origin/main
chown -R frappe:frappe .
# ALT KLASÃ\u0096RDEN KURULUM (MÃ\u009cHÃ\u009cR)
su - frappe -c 'cd /home/frappe/bench/apps/izge_travel && /home/frappe/bench/env/bin/pip install -e ./izge_travel'
# MÄ°GRATE
su - frappe -c 'cd /home/frappe/bench && /home/frappe/.local/bin/bench --site erpnext-production-1b2e.up.railway.app migrate'
"@

# Base64 Sarmalama (Karakter bozulmalarÄ±na karÅ\u015fÄ± en gÃ¼Ã§lÃ¼ kalkan)
$encoded = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($cmd))

# Railway SSH Ã¼zerinden gÃ¶nderim
railway ssh -s erpnext --environment production "echo $encoded | base64 -d | bash"

Write-Host "Deployment BaÅ\u015farÄ±yla TamamlandÄ±! İzge Travel CanlÄ±da." -ForegroundColor Green
