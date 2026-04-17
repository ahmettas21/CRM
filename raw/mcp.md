Kısa cevap: **hayır, tek başına o `frappe-dev-mcp-server` sana tam yetmez**; o daha çok **geliştirme/oluşturma tarafı** için iyi, ama senin istediğin “AI ERPNext’in içini anlayıp kayıt oluştursun, düzenlesin, rapor çalıştırsın, workspace kursun” seviyesi için ayrıca **ERPNext’e bağlı operasyonel bir MCP** de lazım. En iyi kurulum genelde **iki MCP birlikte** olur: biri development için, biri canlı ERP işlemleri için. [github](https://github.com/SajmustafaKe/frappe-dev-mcp-server)

## Bu MCP ne yapar

Sajmustafake’in `frappe-dev-mcp-server` projesi; **DocType JSON üretme, Python controller oluşturma, bench komutları çalıştırma, app yönetimi ve custom API endpoint üretme** gibi geliştirme odaklı işler için tasarlanmış. Yani “custom app kur, yeni DocType scaffold et, geliştirme adımlarını hızlandır” tarafında faydalıdır. [mcpmarket](https://mcpmarket.com/server/frappe-dev)

Bu çok değerli, ama esasen **developer toolbox** gibi çalışır. Tek başına “canlı ERP verisini güvenli şekilde okuyup yazan iş ajanı” rolünü tam karşılamaz. [pulsemcp](https://www.pulsemcp.com/servers/sajmustafake-frappe-dev)

## Neden tek başına yetmez

Senin hedefin sadece kod üretmek değil; “AI tam detaylı kontrol etsin ve istediğim yapıyı kursun” diyorsun. Bu hedefte AI’nin sadece app dosyalarına değil, aynı zamanda **ERPNext document operations**, **raporlar**, **DocType field metadata**, **izinlerle uyumlu CRUD**, hatta canlı instance üzerindeki nesnelere erişmesi gerekir. [github](https://github.com/buildswithpaul/Frappe_Assistant_Core)

Toplulukta ERPNext MCP sunucuları bu yüzden ayrı ayrı şu araçları sunuyor: `create_document`, `update_document`, `get_documents`, `run_report`, `get_doctype_fields`, `get_doctypes`. Bu araçlar olmadan AI geliştirme yapar, ama ERP içindeki iş akışını tam yönetemez. [mcp](https://mcp.pizza/mcp-server/hh6D/erpnext-mcp-server)

## Sana gereken mimari

Bence sana uygun yapı şu:

| Katman | Görev | Gerekli mi |
|---|---|---|
| Frappe Dev MCP | DocType/app/script/workspace kodu üretmek, bench işleri, scaffolding. [github](https://github.com/SajmustafaKe/frappe-dev-mcp-server) | Evet |
| ERPNext Runtime MCP | Canlı sitede belge oluşturmak, güncellemek, rapor çalıştırmak, metadata okumak. [github](https://github.com/buildswithpaul/Frappe_Assistant_Core) | Evet |
| GitHub MCP | Repo dosyalarını düzenlemek, commit/PR akışı yönetmek. [github](https://github.com/github/github-mcp-server) | Çok faydalı |
| Tarayıcı/manuel kontrol | Son doğrulama, kritik ayarlar, deploy sonrası test. [discuss.frappe](https://discuss.frappe.io/t/mcp-server-for-frappe/147635) | Evet |

Bu kombinasyonla AI hem “geliştirici” hem “ERP operatörü” gibi davranabilir. [github](https://github.com/SajmustafaKe/frappe-dev-mcp-server)

## Senin senaryoda nasıl çalışır

Örnek akış şöyle olur:

1. Sen “Travel operasyon workspace’i kur, Trip/Traveler akışını hazırla” dersin. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/111015962/c8cfe4d5-44ac-4851-b546-f83246de51ad/muhasebe_uygulama_plani.md)
2. **Dev MCP** yeni DocType, custom field, workspace tanımı, script/report iskeletini üretir. [mcpmarket](https://mcpmarket.com/server/frappe-dev)
3. **GitHub MCP** bunları repo’ya işler ve sürüm akışına sokar. [github](https://github.com/github/github-mcp-server)
4. **ERPNext MCP** canlı veya staging ERP’de DocType alanlarını doğrular, örnek kayıt açar, rapor çalıştırır, verileri test eder. [github](https://github.com/buildswithpaul/Frappe_Assistant_Core)
5. Sonra sen UI’dan sadece son kontrol yaparsın. [discuss.frappe](https://discuss.frappe.io/t/mcp-server-for-frappe/147635)

Bu model, yalnızca tek MCP kullanmaktan çok daha güçlüdür. [github](https://github.com/SajmustafaKe/frappe-dev-mcp-server)

## Workspace konusu

Workspace kurmak iki seviyede ele alınmalı:

- **tanımını üretmek**: Dev MCP ile yapılabilir; custom app dosyaları, desk page, workspace config, script üretimi bu tarafa yakın durur. [mcpmarket](https://mcpmarket.com/server/frappe-dev)
- **ERP içinde gerçekten çalıştığını doğrulamak**: shortcut açılıyor mu, rapor veri döndürüyor mu, DocType field’ları doğru mu; bu da ERPNext MCP tarafına girer. [mcp](https://mcp.pizza/mcp-server/hh6D/erpnext-mcp-server)

Yani “workspace’i oluşturmak” ile “workspace’i işleyen sisteme bağlamak” aynı şey değil. [github](https://github.com/buildswithpaul/Frappe_Assistant_Core)

## Resmî Frappe MCP yeterli mi

Frappe’ın resmî `frappe/mcp` reposu var, ama kendi açıklamasına göre hâlâ **erken aşamada** ve şu an yalnızca **tools** desteğiyle sınırlı; resources, prompts ve SSE gibi parçalar sonradan gelecek deniyor. Bu yüzden bugün üretim senaryosunda sadece ona güvenmek yerine, topluluk ERPNext MCP çözümleriyle birlikte düşünmek daha gerçekçi olur. [github](https://github.com/frappe/mcp)

## Sana net cevap

Senin hedefin için:

- **Sadece `frappe-dev-mcp-server` yeterli değil**. [mcp](https://mcp.pizza/mcp-server/hh6D/erpnext-mcp-server)
- Eğer AI’nin gerçekten ERPNext içinde oluşturma/düzenleme/test yapmasını istiyorsan, **ayrıca ERPNext runtime MCP** kurmalısın. [github](https://github.com/buildswithpaul/Frappe_Assistant_Core)
- Eğer kodu da repo seviyesinde düzgün yönetsin istiyorsan, bir de **GitHub MCP** eklemek çok mantıklı olur. [github](https://github.com/github/github-mcp-server)

## En iyi kombinasyon

Senin gibi hem teknik hem ürün tarafını birlikte götüren biri için bence en doğru stack:

- **1 adet Dev MCP**: Frappe app, DocType, workspace, script üretimi. [github](https://github.com/SajmustafaKe/frappe-dev-mcp-server)
- **1 adet ERPNext MCP**: canlı/staging belge ve rapor işlemleri. [lobehub](https://lobehub.com/mcp/web3viralabs-erpnext-mcp-server)
- **1 adet GitHub MCP**: repo düzenleme ve PR akışı. [github](https://github.com/github/github-mcp-server)

Bu üçlüyle “AI bana yapıyı kursun” hedefin gerçekten uygulanabilir hale gelir. [mcp](https://mcp.pizza/mcp-server/hh6D/erpnext-mcp-server)

İstersen bir sonraki mesajda sana **senin Railway/ERPNext yapına özel exact MCP stack** yazayım: hangi MCP nerede çalışsın, hangi environment variable’lar olsun, hangisi staging’e hangisi production’a bağlansın.

Evet, **ERPNext/Frappe tarafı için API erişimi hazırlaman lazım**; ama çoğu durumda sıfırdan özel API yazman gerekmez, önce **mevcut Frappe REST API + API key/secret** ile başlamak yeterlidir. Yani ilk adım “custom endpoint yazmak” değil, **MCP’nin ERPNext’e bağlanacağı yetkili bir kullanıcı ve token oluşturmak** olmalı. [docs.frappe](https://docs.frappe.io/framework/user/en/api/rest)

## Sana ne lazım

Başlangıç için minimum gerekenler şunlar:

- ERPNext/Frappe site URL’i,
- API kullanacak ayrı bir kullanıcı,
- o kullanıcı için **API Key + API Secret**,
- bu kullanıcının doğru rollerle yetkilendirilmesi. [docs.frappe](https://docs.frappe.io/framework/user/en/guides/integration/rest_api/token_based_authentication)

Frappe dokümanına göre token tabanlı erişim `Authorization: token api_key:api_secret` başlığıyla yapılır. Bu kullanıcı üzerinden yapılan tüm istekler o kullanıcının izinleriyle çalışır; yani rol tasarımı çok önemlidir. [docs.frappe](https://docs.frappe.io/framework/user/en/api/rest)

## Özel API yazman gerekir mi

İlk aşamada çoğunlukla **hayır**. Çünkü standart REST/RPC uçlarıyla belge oluşturma, güncelleme, listeleme ve method çağrıları zaten yapılabiliyor. [docs.frappe](https://docs.frappe.io/framework/user/en/guides/integration/how_to_setup_token_based_auth)

Ama şu durumlarda **custom API/method** yazman mantıklı olur:

- tek çağrıda birden fazla iş yapılacaksa,
- iş kuralların standart CRUD’dan karmaşıksa,
- AI’nin kullanacağı araçları sınırlı ve güvenli hale getirmek istiyorsan,
- özel import, özel rapor, özel workflow aksiyonu gerekiyorsa. [github](https://github.com/buildswithpaul/Frappe_Assistant_Core)

## En doğru kurulum sırası

Bence şöyle ilerle:

### 1. API kullanıcısı oluştur

ERPNext içinde normal `Administrator` yerine MCP için ayrı bir kullanıcı aç. Doküman da API çağrıları için ayrı kullanıcı oluşturmanın uygun olduğunu söylüyor. [discuss.frappe](https://discuss.frappe.io/t/generate-a-new-api-key-for-my-erpnext-site/136297)

### 2. API key/secret üret

`User -> Settings / API Access -> Generate Keys` yoluyla API Key ve API Secret üret. Secret genelde bir kez gösterildiği için güvenli yere kaydetmen gerekir. [docs.frappe](https://docs.frappe.io/framework/user/en/guides/integration/how_to_set_up_token_based_auth)

### 3. Rolleri dar ver

Bu kullanıcıya önce gerçekten gereken rolleri ver; örneğin Travel operasyonları için ilgili DocType’lara erişim, ama gereksiz tam admin yetkisi verme. Çünkü API çağrılarında izin kontrolü bu kullanıcıya göre yapılır. [discuss.frappe](https://discuss.frappe.io/t/token-authentication-not-works-in-rest-api-erpnext/137602)

### 4. Önce standart endpointlerle test et

İlk test için `frappe.auth.get_logged_user` gibi basit bir çağrı yapıp token’ın çalıştığını doğrula. Sonra `api/resource/...` veya ihtiyacına göre method çağrılarına geç. [docs.frappe](https://docs.frappe.io/framework/user/en/guides/integration/how_to_setup_token_based_auth)

### 5. Yetmiyorsa custom tool/API ekle

AI’nin “tek komutta workspace kur, alanları oluştur, örnek kayıtları bas” gibi daha üst seviye işler yapmasını istiyorsan, burada özel whitelisted method veya custom API yazman faydalı olur. [github](https://github.com/SajmustafaKe/frappe-dev-mcp-server)

## Senin durumda önerim

Senin kullanım hedefin “AI detaylı kontrol etsin, yapı kursun” olduğu için bence iki katman kurmalısın:

| Katman | Ne yapacak |
|---|---|
| GitHub MCP | Repo dosyalarını, custom app’i, workspace config’leri, scriptleri düzenleyecek. [github](https://github.com/github/github-mcp-server) |
| ERPNext API/MCP | Canlı veya staging ERP içinde belge, metadata, rapor ve doğrulama işlemleri yapacak. [docs.frappe](https://docs.frappe.io/framework/user/en/api/rest) |

Yani GitHub MCP tek başına kodu yönetir; ama ERP’nin içindeki gerçek nesneleri yönetmek için **ERPNext erişimi** şarttır. [github](https://github.com/github/github-mcp-server)

## Sana pratik cevap

Şu anda yapman gerekenler:

1. ERPNext’te **MCP için ayrı kullanıcı** aç. [docs.frappe](https://docs.frappe.io/framework/user/en/guides/integration/rest_api/token_based_authentication)
2. O kullanıcıya **API Key / Secret** üret. [docs.frappe](https://docs.frappe.io/framework/user/en/guides/integration/how_to_set_up_token_based_auth)
3. Gerekli rolleri ver. [docs.frappe](https://docs.frappe.io/framework/user/en/guides/integration/rest_api/token_based_authentication)
4. MCP server’ını bu URL + token ile ERPNext’e bağla. [mcp](https://mcp.pizza/mcp-server/hh6D/erpnext-mcp-server)
5. Sonra ihtiyaç olursa özel method’lar yaz. [github](https://github.com/SajmustafaKe/frappe-dev-mcp-server)

## Ne zaman custom API yaz

Şu aşamada hemen özel API yazma. Önce standart API ile şu işler yapılabiliyor mu bak: [docs.frappe](https://docs.frappe.io/framework/user/en/api/rest)

- DocType listeleme,
- belge oluşturma/güncelleme,
- alan metadata’sı çekme,
- rapor çalıştırma,
- whitelisted method çağırma. [docs.frappe](https://docs.frappe.io/framework/user/en/guides/integration/how_to_setup_token_based_auth)

Bunlar yetmezse o zaman senin işine özel 3–5 temiz endpoint yazmak en doğru yaklaşım olur. [github](https://github.com/SajmustafaKe/frappe-dev-mcp-server)

## Net sonuç

Özetle:

- **Evet, API erişimi hazırlaman lazım**. [docs.frappe](https://docs.frappe.io/framework/user/en/api/rest)
- **Hayır, hemen özel API üretmen şart değil**. [docs.frappe](https://docs.frappe.io/framework/user/en/guides/integration/how_to_setup_token_based_auth)
- İlk işin **API user + key/secret + role setup** yapmak olmalı. [docs.frappe](https://docs.frappe.io/framework/user/en/guides/integration/how_to_set_up_token_based_auth)
- Sonra ERPNext MCP’yi buna bağlayıp test etmelisin. [mcp](https://mcp.pizza/mcp-server/hh6D/erpnext-mcp-server)

İstersen bir sonraki mesajda sana **ERPNext içinde hangi kullanıcıyı açacaksın, hangi rolleri vereceksin, hangi test endpointini vuracaksın** diye birebir yapılacaklar listesi çıkarayım.

<https://erpnext-production-1b2e.up.railway.app/app/user/webmaster%40ucuyos.com>

api_key,"api_secret"
3ccbc53e38b3175,
"0e774f739f03ea8"
Şimdi sende **GitHub MCP var**, sıradaki iş **ERPNext/Frappe MCP tarafını temiz ve güvenli kurmak**; en kritik nokta da gereksiz fazla yetki vermemek ve staging/production’ı ayırmak. Yani kuracağın şeyler aslında 3 parçaya ayrılıyor: GitHub, ERPNext API/MCP ve opsiyonel dev-side Frappe MCP. [github](https://github.com/github/github-mcp-server)

## Kuracağın şeyler

Bence şu sırayla git:

1. **GitHub MCP**  
Repo okuma/yazma, dosya düzenleme, PR açma için. [docs.github](https://docs.github.com/en/copilot/how-tos/provide-context/use-mcp/use-the-github-mcp-server)

2. **ERPNext API tabanlı MCP**  
Canlı ERPNext içinde belge oluşturma, güncelleme, veri çekme, rapor çalıştırma için. [github](https://github.com/rakeshgangwar/erpnext-mcp-server)

3. **Opsiyonel Frappe Dev MCP**  
Custom app, DocType, script, workspace scaffolding gibi geliştirme işleri için. [github](https://github.com/frappe/mcp)

Senin kullanımda **olmazsa olmaz** olan ikili: **GitHub MCP + ERPNext MCP**. [github](https://github.com/github/github-mcp-server)

## GitHub tarafında dikkat

GitHub MCP için mümkünse **fine-grained PAT** kullan ve sadece gerekli repolara erişim ver. GitHub dokümanları da minimum repository access ve minimum permission mantığını öneriyor. [github](https://github.blog/security/application-security/introducing-fine-grained-personal-access-tokens-for-github/)

Başlangıç için genelde gerekenler:

- `Contents`: read/write,
- `Metadata`: read,
- `Pull requests`: read/write,
- gerekiyorsa `Issues`: read/write,
- sadece workflow düzenleyecekse `Actions/Workflows` ile ilgili yetki. [github](https://github.com/github/github-mcp-server/issues/552)

Özellikle tüm hesabı açmak yerine **Only select repositories** seçmen daha güvenli olur. [docs.github](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

## ERPNext tarafında dikkat

ERPNext MCP için temel env değişkenleri genelde şunlar:

- `ERPNEXT_URL`
- `ERPNEXT_API_KEY`
- `ERPNEXT_API_SECRET`. [discuss.frappe](https://discuss.frappe.io/t/mcp-server-for-erpnext-120-tools-to-connect-ai-agents-to-your-erp/161198)

Bunlar MCP server’a verilince AI, standart Frappe REST API üstünden ERPNext’e bağlanır. Ama burada en önemli şey şu: MCP’ye verdiğin yetki, o kullanıcının ERP içinde sahip olduğu yetkinin aynısı olur. [pulsemcp](https://www.pulsemcp.com/servers/danielsebastianc-frappe-api)

## En büyük riskler

En çok şunlara dikkat et:

- **Production’a direkt tam yetki verme.** Önce staging’de dene. [discuss.frappe](https://discuss.frappe.io/t/mcp-server-for-erpnext-120-tools-to-connect-ai-agents-to-your-erp/161198)
- **Admin kullanıcıyı MCP için kullanma.** Ayrı teknik kullanıcı kullan. [docs.frappe](https://docs.frappe.io/framework/user/en/guides/integration/rest_api/token_based_authentication)
- **Secret’ları dosyada tutma.** Environment variable olarak sakla. [github](https://github.com/rakeshgangwar/erpnext-mcp-server)
- **GitHub ile ERPNext’i aynı ajan altında körlemesine full-write açma.** Önce read-heavy başla. [docs.github](https://docs.github.com/en/copilot/how-tos/provide-context/use-mcp/set-up-the-github-mcp-server)
- **Employee/User Permission kısıtlarını unutma.** API’de beklenmedik permission hataları çıkarabilir. [docs.frappe](https://docs.frappe.io/erpnext/user-permissions)

## Sana önerdiğim yetki modeli

Bence 3 aşamalı git:

| Aşama | GitHub | ERPNext | Amaç |
|---|---|---|---|
| 1 | Read/limited write. [docs.github](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) | Read + sınırlı create/update. [docs.frappe](https://docs.frappe.io/erpnext/user-permissions) | Güvenli test |
| 2 | Repo write + PR. [github](https://github.com/github/github-mcp-server) | Operasyonel DocType write. [github](https://github.com/rakeshgangwar/erpnext-mcp-server) | Gerçek kullanım |
| 3 | Workflow/deploy yetkisi gerekiyorsa ekle. [github](https://github.com/github/github-mcp-server/issues/552) | Daha geniş ERP araçları. [discuss.frappe](https://discuss.frappe.io/t/mcp-server-for-erpnext-120-tools-to-connect-ai-agents-to-your-erp/161198) | Otomasyon |

Bu şekilde bir anda her şeyi açmamış olursun. [docs.github](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

## Sende şimdi yapılacaklar

Şu an sırayla bunu yap:

- GitHub MCP token’ında hangi repo ve permission’lar açık, kontrol et. [docs.github](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- ERPNext teknik user’ı için yeni secret üret, eskisini kullanma. [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/111015962/2a142fc3-23c5-48c2-b149-cf5e8b9ff69d/frappe_api_keys.csv)
- ERPNext MCP server kur ve URL/key/secret ile bağla. [github](https://github.com/rakeshgangwar/erpnext-mcp-server)
- Önce `get_logged_user` ve basit document list testleri yap. [docs.frappe](https://docs.frappe.io/framework/user/en/api/rest)
- Sonra AI’ye küçük görevler ver: “Trip listesini getir”, “workspace shortcut ekle”, “draft kayıt oluştur”. [discuss.frappe](https://discuss.frappe.io/t/mcp-server-for-erpnext-120-tools-to-connect-ai-agents-to-your-erp/161198)

## Ben olsam nasıl kurarım

Senin senaryoda ben şunu yaparım:

- **GitHub MCP**: yalnızca ilgili ERP repo’larına erişim. [docs.github](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- **ERPNext MCP**: ayrı teknik user, sınırlı roller. [docs.frappe](https://docs.frappe.io/framework/user/en/guides/integration/rest_api/token_based_authentication)
- **Staging ERPNext**: AI önce burada değişiklik yapar. [discuss.frappe](https://discuss.frappe.io/t/mcp-server-for-erpnext-120-tools-to-connect-ai-agents-to-your-erp/161198)
- **Production**: ilk etapta read ağırlıklı veya kontrollü write. [docs.frappe](https://docs.frappe.io/erpnext/user-permissions)

Bu en güvenli ve sürdürülebilir model olur. [github](https://github.com/rakeshgangwar/erpnext-mcp-server)

## Net liste

Yani şu anda kuruyor olman gerekenler:

- GitHub MCP, repo erişimleriyle birlikte. [github](https://github.com/github/github-mcp-server)
- ERPNext MCP, URL + API key + API secret ile. [github](https://github.com/rakeshgangwar/erpnext-mcp-server)
- Gerekirse sonra Frappe Dev MCP. [github](https://github.com/SajmustafaKe/frappe-dev-mcp-server)

Ve dikkat etmen gerekenler:

- minimum yetki,
- ayrı teknik kullanıcı,
- production/staging ayrımı,
- secret rotasyonu,
- API testleri,
- permission testleri. [docs.frappe](https://docs.frappe.io/framework/user/en/guides/integration/rest_api/token_based_authentication)

İstersen bir sonraki mesajda sana **senin için exact kurulum checklist’i** çıkarayım: GitHub permission’ları ne olsun, ERPNext user rolleri ne olsun, MCP env’leri tam ne olsun.
